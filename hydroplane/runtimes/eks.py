import base64
from datetime import datetime, timedelta
import logging
from pathlib import Path
import tempfile
from typing import List, Literal, Optional

from awscli.customizations.eks.get_token import TokenGenerator
import kubernetes
from pydantic import BaseModel, Field

from ..models.aws import AWSCredentials
from ..models.process_info import ProcessInfo
from ..models.process_spec import ProcessSpec
from .runtime import Runtime
from ..secret_stores.secret_store import SecretStore
from ..utils.aws import boto3_session_from_creds
from ..utils.k8s import (HYDROPLANE_PROCESS_LABEL,
                         HYDROPLANE_GROUP_LABEL,
                         discover_k8s_api_version,
                         k8s_start_process, k8s_stop_group, k8s_stop_process,
                         k8s_list_processes)

RUNTIME_TYPE = 'eks'

TOKEN_EXPIRATION_MINS = 14

K8S_AWS_ID_HEADER = 'x-k8s-aws-id'

logger = logging.getLogger('eks_runtime')


class Settings(BaseModel):
    runtime_type: Literal[RUNTIME_TYPE] = RUNTIME_TYPE

    credentials: AWSCredentials = Field(
        description='the credentials that will be used to authenticate with EKS'
    )
    cluster_name: str = Field(
        description='the name of the EKS cluster'
    )
    region: str = Field(
        description='the AWS region where the cluster is running (e.g. us-west-2)'
    )
    namespace: Optional[str] = Field(
        'default',
        description='the Kubernetes namespace that Hydroplane will create pods and services within'
    )


class EKSRuntime(Runtime):
    def __init__(self, settings: Settings, secret_store: SecretStore):
        self.settings = settings
        self.secret_store = secret_store

        self._boto3_session = None

        self._k8s_client = None
        self._k8s_client_expiration_time: datetime = None

        # We need to store certs on the filesystem for the k8s client to be able to read them.
        self.cert_storage_dir = Path(tempfile.mkdtemp())

    def _k8s_client_expired(self) -> bool:
        # We'll give ourselves a one minute grace period before the token expires so we don't run
        # into problems if we process a request _right_ before it expires.

        return self._k8s_client_expiration_time <= datetime.now() + timedelta(minutes=1)

    @property
    def boto3_session(self):
        if self._boto3_session is None:
            self._boto3_session = boto3_session_from_creds(
                self.settings.credentials, self.secret_store
            )

        return self._boto3_session

    def _get_k8s_client(self, cluster_name: str):
        if self._k8s_client is None or self._k8s_client_expired():
            self._k8s_client = self._create_new_k8s_client(cluster_name)
            self._k8s_client_expiration_time = (datetime.now() +
                                                timedelta(minutes=TOKEN_EXPIRATION_MINS))
            logger.debug(f'k8s client expires {self._k8s_client_expiration_time}')

        return self._k8s_client

    def _create_new_k8s_client(self, cluster_name: str):
        """Configure and return an Kubernetes client that can be used to modify the EKS cluster.

        Programmatically configuring a k8s client without access to a local kube_config is a bit
        challenging. Luckily, someone else figured out how to do it already; their experience is
        documented here: https://www.analogous.dev/blog/using-the-kubernetes-python-client-with-aws/
        """

        logger.debug('Creating a new k8s client')

        # First, retrieve information about the EKS cluster from AWS via boto3
        eks_client = self.boto3_session.client('eks', region_name=self.settings.region)

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
        sts_client = self.boto3_session.client('sts', region_name=self.settings.region)

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
        k8s_start_process(
            k8s_client,
            namespace=self.settings.namespace,
            process_spec=process_spec
        )

    def stop_process(self, process_name: str):
        k8s_client = self._get_k8s_client(self.settings.cluster_name)

        k8s_stop_process(
            k8s_client,
            namespace=self.settings.namespace,
            process_name=process_name
        )

    def stop_group(self, group: str):
        k8s_client = self._get_k8s_client(self.settings.cluster_name)

        k8s_stop_group(
            k8s_client,
            namespace=self.settings.namespace,
            group=group
        )

    def list_processes(self, group: Optional[str]) -> List[ProcessInfo]:
        k8s_client = self._get_k8s_client(self.settings.cluster_name)

        return k8s_list_processes(
            k8s_client,
            namespace=self.settings.namespace,
            group=group
        )

    def refresh_api_clients(self):
        self._get_k8s_client(self.settings.cluster_name)
