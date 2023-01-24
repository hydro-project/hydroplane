import base64
import logging
from pathlib import Path
import tempfile
from typing import List, Literal, Optional

import google.auth
import google.auth.transport.requests
from google.cloud import container_v1beta1
import kubernetes
from kubernetes.client import ApiClient
from kubernetes.config.kube_config import Configuration as KubeConfiguration
from pydantic import BaseModel, Field


from ..models.process_info import ProcessInfo
from ..utils.k8s import k8s_start_process, k8s_list_processes, k8s_stop_group, k8s_stop_process
from ..models.process_spec import ProcessSpec
from .runtime import Runtime
from ..secret_stores.secret_store import SecretStore

RUNTIME_TYPE = 'gke'


class Settings(BaseModel):
    runtime_type: Literal[RUNTIME_TYPE] = RUNTIME_TYPE  # type: ignore

    cluster_id: str = Field(description='the cluster ID of the GKE cluster')
    namespace: str = Field('default', description='the Kubernetes namespace that Hydroplane will create pods and services within')
    project: str = Field(description='the project in which the GKE cluster is located')
    region: str = Field(description='the GCP region in whcih the cluster is located')


logger = logging.getLogger('gke_runtime')


class GKERuntime(Runtime):
    """
    A runtime for Google Kubernetes Engine (https://cloud.google.com/kubernetes-engine)
    """
    def __init__(self, settings: Settings, secret_store: SecretStore):
        self.settings = settings
        self.secret_store = secret_store

        self._gcp_creds = None
        self._gke_client = None
        self._k8s_client: Optional[ApiClient] = None

        self.cert_storage_dir = Path(tempfile.mkdtemp())

    @property
    def gke_client(self):
        if self._gke_client is None:
            self._gke_client = container_v1beta1.ClusterManagerClient(credentials=self.gcp_creds)

        return self._gke_client

    @property
    def k8s_client(self) -> ApiClient:
        if self._k8s_client is None or self.gcp_creds.expired:
            self._k8s_client = self._new_k8s_client()

        return self._k8s_client

    @property
    def gcp_creds(self):
        if self._gcp_creds is None:
            # Assume Application Default Credentials (ADC)
            # (https://cloud.google.com/docs/authentication/application-default-credentials)
            logger.debug('Using Application Default Credentials')
            self._gcp_creds, project = google.auth.default()

            # Make sure the ADC you retrieved matches the configured cluster's project
            if project != self.settings.project:
                raise ValueError(f'Project returned by google.auth.default() ({project}) '
                    f'does not match configured project ({self.settings.project}); maybe your ADC is '
                    'pointing at the wrong project for this cluster?')

            self._refresh_gcp_creds()

        return self._gcp_creds

    def _refresh_gcp_creds(self):
        # Our GCP credentials are temporary, and will eventually expire and need to be renewed.
        # This method refreshes those credentials.
        auth_req = google.auth.transport.requests.Request()
        self.gcp_creds.refresh(auth_req)

    def _new_k8s_client(self) -> ApiClient:
        # Make sure we've got valid credentials before using their token for authorization
        if self.gcp_creds.expired:
            self._refresh_gcp_creds()

        # We'll use the GKE client to get enough information about the cluster to configure the k8s client
        request = container_v1beta1.GetClusterRequest(
            name=f'projects/{self.settings.project}/locations/{self.settings.region}/clusters/{self.settings.cluster_id}',
        )

        cluster_info = self.gke_client.get_cluster(request=request)

        # The k8s client requires that CA certs be stored on disk, so we'll put the cluster's CA cert (that we retrieved
        # as part of its cluster info from GKE) in a temporary location on disk, and point the client at that file.
        cert_file_path = self.cert_storage_dir / f"{cluster_info.name}.cert"

        if not cert_file_path.exists():
            with open(cert_file_path, 'w+b') as fp:
                fp.write(base64.b64decode(cluster_info.master_auth.cluster_ca_certificate))

        # Now we'll actually start configuring the k8s clien, using the authorization token in our GCP credentials as
        # the bearer token for interactions with the cluster.
        kube_config = KubeConfiguration(
            host=f"https://{cluster_info.endpoint}:443",
            api_key={
                'authorization': f'Bearer {self.gcp_creds.token}'
            }
        )

        kube_config.ssl_ca_cert=cert_file_path  # type: ignore

        # Finally, mercifully, create the client.
        api_client = ApiClient(configuration=kube_config)

        return api_client

    def start_process(self, process_spec: ProcessSpec):
        k8s_start_process(
            self.k8s_client,
            namespace=self.settings.namespace,
            process_spec=process_spec
        )


    def stop_process(self, process_name: str):
        k8s_stop_process(
            self.k8s_client,
            namespace=self.settings.namespace,
            process_name=process_name
        )


    def stop_group(self, group: str):
        k8s_stop_group(
            self.k8s_client,
            namespace=self.settings.namespace,
            group=group
        )


    def list_processes(self, group: Optional[str]) -> List[ProcessInfo]:
        return k8s_list_processes(
            self.k8s_client,
            namespace=self.settings.namespace,
            group=group
        )

    def refresh_api_clients(self):
        if self.gcp_creds.expired:
            logger.debug('GCP credentials expired. Renewing credentials and refreshing k8s client')
            self._refresh_gcp_creds()
            self._k8s_client = self._new_k8s_client()