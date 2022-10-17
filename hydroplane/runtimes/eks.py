import base64
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
from typing import Literal, Optional

from awscli.customizations.eks.get_token import TokenGenerator
import kubernetes
from pydantic import BaseModel, Field

from ..models.aws import AWSCredentials
from ..models.process_spec import ProcessSpec
from .runtime import Runtime
from ..secret_stores.secret_store import SecretStore
from ..utils.aws import boto3_client_from_creds
from ..utils.k8s import discover_k8s_api_version, process_spec_to_pod_manifest

RUNTIME_TYPE = 'eks'

TOKEN_EXPIRATION_MINS = 14

K8S_AWS_ID_HEADER = 'x-k8s-aws-id'


class Settings(BaseModel):
    runtime_type: Literal[RUNTIME_TYPE] = RUNTIME_TYPE

    credentials: AWSCredentials
    cluster_name: str
    region: str
    namespace: Optional[str] = Field('default')


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

        # Now that we've got all those pieces, we can build the client's configuration ...
        kube_config = kubernetes.config.kube_config.Configuration(
            host=endpoint,
            api_key={'authorization': f"Bearer {bearer_token['status']['token']}"}
        )

        kube_config.ssl_ca_cert = ca_cert_file

        # ... and use that configuration to create an API client. Whew!
        kube_client = kubernetes.client.ApiClient(configuration=kube_config)

        return kubernetes.client.CoreV1Api(api_client=kube_client)

    def _get_ca_cert_file(self, cluster_data: dict) -> Path:
        cert_file_path = self.cert_storage_dir / f"{cluster_data['name']}.cert"

        if not cert_file_path.exists():
            with open(cert_file_path, 'w+b') as fp:
                fp.write(base64.b64decode(cluster_data['certificateAuthority']['data']))

        return cert_file_path

    def _generate_bearer_token(self, cluster_name: str) -> dict:
        # We're borrowing the technique that the AWS CLI uses to retrieve a bearer token
        # (https://github.com/aws/aws-cli/blob/develop/awscli/customizations/eks/get_token.py#L128)
        sts_client = boto3_client_from_creds(
            'sts', self.settings.region, self.settings.credentials, self.secret_store
        )

        # This is mimicking what `aws sts get-caller-identity` does. Best as I can tell, it's
        # turning a parameter to get-caller-identity into an HTTP header by hooking into a couple of
        # lifecycle events on the get-caller-identity call itself, but I honestly have no idea
        # why. Without this, token generation doesn't work, so: when in Rome, do as the Romans.
        sts_client.meta.events.register(
            'provide-client-params.sts.GetCallerIdentity',
            self._retrieve_k8s_aws_id
        )

        sts_client.meta.events.register(
            'before-sign.sts.GetCallerIdentity',
            self._inject_k8s_aws_id_header
        )

        token = TokenGenerator(sts_client).get_token(cluster_name)

        # The actual amount of token expiration doesn't really matter for our purposes, since the
        # calls we're making are short. If we find ourselves needing to keep the token cached and
        # renew it, we'll need to know this expiration time in order to decide when to renew.
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

    def _retrieve_k8s_aws_id(self, params, context, **kwargs):
        if K8S_AWS_ID_HEADER in params:
            context[K8S_AWS_ID_HEADER] = params.pop(K8S_AWS_ID_HEADER)

    def _inject_k8s_aws_id_header(self, request, **kwargs):
        if K8S_AWS_ID_HEADER in request.context:
            request.headers[K8S_AWS_ID_HEADER] = request.context[K8S_AWS_ID_HEADER]

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
