import base64
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import tempfile
from typing import Literal, Optional

from awscli.customizations.eks.get_token import TokenGenerator
import kubernetes
from pydantic import BaseModel, Field

from ..models.aws import AWSCredentials
from ..models.process_spec import ProcessSpec
from ..models.secret import SecretValue, SecretSource
from .runtime import Runtime
from ..secret_stores.secret_store import SecretStore
from ..utils.aws import boto3_client_from_creds

RUNTIME_TYPE = 'eks'

TOKEN_EXPIRATION_MINS = 14

K8S_AWS_ID_HEADER = 'x-k8s-aws-id'


class Settings(BaseModel):
    runtime_type: Literal[RUNTIME_TYPE] = RUNTIME_TYPE

    credentials: AWSCredentials
    cluster_name: str
    region: str
    namespace: Optional[str] = Field('default')


def discover_k8s_api_version():
    # Taking a page from awscli's book, we'll look at the KUBERNETES_EXEC_INFO environment variable
    # to find the k8s API version we're supposed to use, and fall back to v1beta1, which should be
    # supported in k8s up to 1.29 (which should GA around December of 2023)

    exec_info_raw = os.environ.get('KUBERNETES_EXEC_INFO', '')

    if not exec_info_raw:
        return 'client.authentication.k8s.io/v1beta1'

    try:
        exec_info = json.loads(exec_info_raw)
    except json.JSONDecodeError:
        raise ValueError(
            "The contents of the KUBERNETES_EXEC_INFO environment variable is "
            "malformed, so we can't the version of the Kubernetes API we're "
            "supposed to use from it."
        )

    if 'apiVersion' not in exec_info:
        raise ValueError('Unable to extract API version number from KUBERNETES_EXEC_INFO')

    return exec_info['apiVersion']


def process_spec_to_pod_manifest(process_spec: ProcessSpec) -> dict:
    container_spec = process_spec.container

    env = []

    for e in container_spec.env:
        if isinstance(e.value, SecretValue):
            secret_value = e.value

            if e.source == SecretSource.K8S_SECRET:
                secret_ref = {
                    'name': secret_value.secret_name
                }

                if e.value.key is not None:
                    secret_ref['key'] = secret_value.key

                env.append({
                    'name': e.name,
                    'valueFrom': {
                        'secretRef': secret_ref
                    }
                })
            else:
                raise ValueError("Secret values with source {e.source} currently unsupported")
        else:
            env.append({'name': e.name, 'value': e.value})

    ports = []

    for i, p in enumerate(container_spec.ports):
        # Ignoring host port, since k8s will handle that for us
        ports.append({
            'containerPort': p.container_port,
            'name': p.name or f'{process_spec.process_name}-port-{i + 1}'
        })

    pod_manifest = {
        'apiVersion': 'v1',
        'kind': 'Pod',
        'metadata': {
            'name': process_spec.process_name
        },
        'spec': {
            'containers': [{
                'image': container_spec.image_uri,
                'name': process_spec.process_name,
                'env': env,
                'ports': ports
            }],
            'restartPolicy': 'never'
        }
    }

    return pod_manifest


class EKSRuntime(Runtime):
    def __init__(self, settings: Settings, secret_store: SecretStore):
        self.settings = settings
        self.secret_store = secret_store

        # We need to store certs on the filesystem for the k8s client to be able to read them.
        self.cert_storage_dir = Path(tempfile.mkdtemp())

    def _get_k8s_client(self, cluster_name: str):
        """Configure and return an Kubernetes client that can be used to modify the EKS cluster.

        Programmatically configuring a k8s client without access to a local kube_config is a bit
        challenging. Luckily, someone else figured out how to do it already; their experience is
        documented here: https://www.analogous.dev/blog/using-the-kubernetes-python-client-with-aws/
        """

        # First, retrieve information about the EKS cluster from AWS via boto3
        eks_client = boto3_client_from_creds(
            'eks', self.settings.region, self.settings.credentials, self.secret_store
        )

        cluster_data = eks_client.describe_cluster(name=cluster_name)['cluster']

        # The client will need to know what endpoint to communicate with the cluster over.
        endpoint = cluster_data['endpoint']

        # We need to write a CA cert to disk that the k8s client can use to communicate with the
        # cluster over TLS.
        ca_cert_file = self._get_ca_cert_file(cluster_data)

        # We'll also need to configure a bearer token for authentication with the cluster.
        bearer_token = self._generate_bearer_token(cluster_name)

        # Now that we've got all those pieces, we can configure the client itself
        kube_config = kubernetes.config.kube_config.Configuration(
            host=endpoint,
            api_key={'authorization': f'Bearer {bearer_token}'}
        )

        kube_config.ssl_ca_cert = ca_cert_file

        kube_client = kubernetes.client.ApiClient(configuration=kube_config)

        return kubernetes.client.CoreV1Api(api_client=kube_client)

    def _get_ca_cert_file(self, cluster_data: dict) -> Path:
        cert_file_path = self.cert_storage_dir / f"{cluster_data['name']}.cert"

        if not cert_file_path.exists():
            with open(cert_file_path, 'w+b') as fp:
                fp.write(base64.b64decode(cluster_data['certificateAuthority']['data']))

        return cert_file_path

    def _retrieve_k8s_aws_id(self, params, context, **kwargs):
        if K8S_AWS_ID_HEADER in params:
            context[K8S_AWS_ID_HEADER] = params.pop(K8S_AWS_ID_HEADER)

    def _inject_k8s_aws_id_header(self, request, **kwargs):
        if K8S_AWS_ID_HEADER in request.context:
            request.headers[K8S_AWS_ID_HEADER] = request.context[K8S_AWS_ID_HEADER]

    def _generate_bearer_token(self, cluster_name: str) -> dict:
        # We're borrowing the technique that the AWS CLI uses to retrieve a bearer token
        # (https://github.com/aws/aws-cli/blob/develop/awscli/customizations/eks/get_token.py#L128)
        sts_client = boto3_client_from_creds(
            'sts', self.settings.region, self.settings.credentials, self.secret_store
        )
        sts_client.meta.events.register(
            'provide-client-params.sts.GetCallerIdentity',
            self._retrieve_k8s_aws_id
        )

        sts_client.meta.events.register(
            'before-sign.sts.GetCallerIdentity',
            self._inject_k8s_aws_id_header
        )

        token = TokenGenerator(sts_client).get_token(cluster_name)

        token_expiration = (datetime.utcnow() + timedelta(
            minutes=TOKEN_EXPIRATION_MINS
        )).strftime('%Y-%m-%dT%H:%M:%SZ')

        return {
            'kind': 'ExecCredential',
            'apiVersion': discover_k8s_api_version(),
            'spec': {},
            'status': {
                'expirationTimestamp': token_expiration,
                'token': token
            }
        }

    def start_process(self, process_spec: ProcessSpec):
        k8s_client = self._get_k8s_client(self.settings.cluster_name)

        pod_manifest = process_spec_to_pod_manifest(process_spec)

        k8s_client.create_namespaced_pod(
            body=pod_manifest,
            namespace=self.settings.namespace
        )

    def stop_process(self, process_name: str):
        k8s_client = self._get_k8s_client(self.settings.cluster_name)

        k8s_client.delete_namespaced_pod(
            name=process_name,
            namespace=self.settings.namespace
        )
