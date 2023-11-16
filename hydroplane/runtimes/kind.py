import logging
from pathlib import Path
from typing import List, Literal, Optional

from kubernetes import config as k8sconfig

from kubernetes.client import ApiClient
from pydantic import BaseModel, Field


from ..models.process_info import ProcessInfo
from ..utils.k8s import k8s_start_process, k8s_list_processes, k8s_stop_group, k8s_stop_process
from ..models.process_spec import ProcessSpec
from .runtime import Runtime
from ..secret_stores.secret_store import SecretStore

RUNTIME_TYPE = 'kind'


class Settings(BaseModel):
    runtime_type: Literal[RUNTIME_TYPE] = RUNTIME_TYPE  # type: ignore

    context: str = Field(None, description='context to use')
    namespace: str = Field('default', description='the Kubernetes namespace that Hydroplane will create pods and services within')
    # This is something that Kubernetes auto-assigns. However, in order to expose
    # a NodePort service using kind, we need to pre-map ports in the kind configuration
    # and make sure that nodePort assigned in the serviceSpec is equal to the one
    # used in the port mapping. 
    #
    # A default of 30007 is set because Kubernetes by default assigns a port from
    # the range 30000-32767. It would be nice to validate this range as a pre-check, but
    # starting Kubernetes 1.28, it is possible to assign port ranges to NodePort services
    # (enabled by default). Because of this validation becomes slightly more involved. It
    # might be worth looking into in the future.
    node_port: int = Field(30007, description='the port that will be used to expose the service')

logger = logging.getLogger('kind_runtime')


class KindRuntime(Runtime):
    """
    A runtime for Kubernetes In Docker (https://kind.sigs.k8s.io/)
    """
    def __init__(self, settings: Settings, secret_store: SecretStore):
        self.settings = settings
        self.secret_store = secret_store

        self._k8s_client: Optional[ApiClient] = None
        self._node_port = self.settings.node_port
        
        k8sconfig.load_kube_config()

    @property
    def k8s_client(self) -> ApiClient:
        if self._k8s_client is None:
            self._k8s_client = self._new_k8s_client()
        return self._k8s_client

    def _new_k8s_client(self) -> ApiClient:
        # ApiClient by default loads the default Configuration class
        # which is set by the load_kube_config() method during init.
        return ApiClient()

    def start_process(self, process_spec: ProcessSpec):
        k8s_start_process(
            self.k8s_client,
            namespace=self.settings.namespace,
            process_spec=process_spec,
            node_port=self._node_port
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
            group=group,
            node_port=self._node_port
        )

    def refresh_api_clients(self):
        pass
