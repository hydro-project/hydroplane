import base64
from datetime import datetime, timedelta
import logging
from pathlib import Path
import tempfile
from typing import Dict, List, Literal, Optional

from awscli.customizations.eks.get_token import TokenGenerator
from fastapi import HTTPException
import kubernetes
from pydantic import BaseModel, Field

from ..models.aws import AWSCredentials
from ..models.process_info import ProcessInfo, SocketAddress
from ..models.process_spec import ProcessSpec
from .runtime import Runtime
from ..secret_stores.secret_store import SecretStore
from ..utils.aws import boto3_client_from_creds
from ..utils.k8s import (HYDROPLANE_PROCESS_LABEL,
                         HYDROPLANE_GROUP_LABEL,
                         discover_k8s_api_version,
                         k8s_api_exception_to_http_exception,
                         process_spec_to_pod_manifest,
                         process_spec_to_service_manifest)

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

        self._k8s_client = None
        self._k8s_client_expiration_time: datetime = None

        # We need to store certs on the filesystem for the k8s client to be able to read them.
        self.cert_storage_dir = Path(tempfile.mkdtemp())

    def _k8s_client_expired(self) -> bool:
        # We'll give ourselves a one minute grace period before the token expires so we don't run
        # into problems if we process a request _right_ before it expires.

        return self._k8s_client_expiration_time <= datetime.now() + timedelta(minutes=1)

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

        try:
            k8s_client.create_namespaced_pod(
                body=pod_manifest,
                namespace=self.settings.namespace
            )
        except kubernetes.client.exceptions.ApiException as e:
            if e.status == 409 and e.reason == 'Conflict':
                raise HTTPException(
                    status_code=409,
                    detail=f'A pod named "{process_spec.process_name}" already exists'
                )
            else:
                raise k8s_api_exception_to_http_exception(e)

        service_manifest = process_spec_to_service_manifest(process_spec)

        try:
            k8s_client.create_namespaced_service(
                body=service_manifest,
                namespace=self.settings.namespace
            )
        except kubernetes.client.exceptions.ApiException as e:
            if e.status == 409 and e.reason == 'Conflict':
                raise HTTPException(
                    status_code=409,
                    detail=f'A service named "{process_spec.process_name}" already exists'
                )
            else:
                raise k8s_api_exception_to_http_exception(e)

    def stop_process(self, process_name: str):
        k8s_client = self._get_k8s_client(self.settings.cluster_name)

        k8s_client.delete_namespaced_pod(
            name=process_name,
            namespace=self.settings.namespace
        )

        service_list = k8s_client.list_namespaced_service(
            label_selector=f'{HYDROPLANE_PROCESS_LABEL}={process_name}',
            namespace=self.settings.namespace
        )

        for service in service_list.items:
            k8s_client.delete_namespaced_service(
                name=service.metadata.name,
                namespace=self.settings.namespace
            )

    def stop_group(self, group: str):
        k8s_client = self._get_k8s_client(self.settings.cluster_name)

        pods = k8s_client.list_namespaced_pod(
            label_selector=f'{HYDROPLANE_GROUP_LABEL}={group}',
            namespace=self.settings.namespace
        )

        services = k8s_client.list_namespaced_service(
            label_selector=f'{HYDROPLANE_GROUP_LABEL}={group}',
            namespace=self.settings.namespace
        )

        for pod in pods.items:
            k8s_client.delete_namespaced_pod(
                name=pod.metadata.name,
                namespace=self.settings.namespace
            )

        for service in services.items:
            k8s_client.delete_namespaced_service(
                name=service.metadata.name,
                namespace=self.settings.namespace
            )

    def list_processes(self, group: Optional[str]) -> List[ProcessInfo]:
        k8s_client = self._get_k8s_client(self.settings.cluster_name)

        # Pods will tell us the internal IP addresses of the nodes they're running on, but
        # not what the external IP addresses of those nodes are (or if they have them at all). We
        # need this information to tell the caller which node to talk to, so we'll list the
        # cluster's nodes and establish a map from internal to external IPs from that.
        nodes = k8s_client.list_node()

        node_private_to_public_ip: Dict[str, Optional[str]] = {}

        for node in nodes.items:
            external_ip = None
            internal_ip = None
            hostname = None

            for address in node.status.addresses:
                if address.type == 'ExternalIP':
                    external_ip = address.address
                elif address.type == 'InternalIP':
                    internal_ip = address.address
                elif address.type == 'Hostname':
                    hostname = address.address

            if internal_ip is None:
                raise RuntimeError(f'Unable to determine internal IP for node {hostname}')

            node_private_to_public_ip[internal_ip] = external_ip

        if group is not None:
            label_selector = f"{HYDROPLANE_GROUP_LABEL}={group}"
        else:
            label_selector = HYDROPLANE_PROCESS_LABEL

        services = k8s_client.list_namespaced_service(
            label_selector=label_selector,
            namespace=self.settings.namespace
        )

        pods = k8s_client.list_namespaced_pod(
            label_selector=label_selector,
            namespace=self.settings.namespace
        )

        pods_by_name = {pod.metadata.labels[HYDROPLANE_PROCESS_LABEL]: pod for pod in pods.items}

        process_infos = []

        for service in services.items:
            process_name = service.metadata.labels[HYDROPLANE_PROCESS_LABEL]
            service_type = service.spec.type
            service_cluster_ip = service.spec.cluster_ip

            socket_addresses = []

            for port_spec in service.spec.ports:
                # For public services, node_port will be specified and will be the same on each
                # port. For private services, it will be None and port will be specified instead.
                port = port_spec.node_port or port_spec.port

                if service_type == 'NodePort':
                    pod_private_ip = pods_by_name[process_name].status.host_ip
                    socket_ip = node_private_to_public_ip[pod_private_ip]

                    if socket_ip is None:
                        raise RuntimeError(
                            f"We expected the public process {process_name} to be running on a "
                            "node with an external IP address, but the node it's running on "
                            f"({pod_private_ip}) doesn't have one."
                        )

                    is_public = True
                else:
                    socket_ip = service_cluster_ip
                    is_public = False

                socket_addresses.append(
                    SocketAddress(
                        host=socket_ip,
                        port=port,
                        is_public=is_public
                    )
                )

            process_infos.append(ProcessInfo(
                process_name=process_name,
                group=group,
                socket_addresses=socket_addresses
            ))

        return process_infos

    def refresh_api_clients(self):
        self._get_k8s_client(self.settings.cluster_name)
