from functools import lru_cache
from typing import TYPE_CHECKING

from .docker import DockerRuntime, RUNTIME_TYPE as DOCKER_RUNTIME_TYPE
from .eks import EKSRuntime, RUNTIME_TYPE as EKS_RUNTIME_TYPE
from .gke import GKERuntime, RUNTIME_TYPE as GKE_RUNTIME_TYPE
from .runtime import Runtime
from ..secret_stores.secret_store import SecretStore

if TYPE_CHECKING:
    from ..config import Settings


def get_runtime(secret_store: SecretStore, settings: "Settings") -> Runtime:
    if settings.runtime.runtime_type == DOCKER_RUNTIME_TYPE:
        return DockerRuntime(settings.runtime, secret_store)
    elif settings.runtime.runtime_type == EKS_RUNTIME_TYPE:
        return EKSRuntime(settings.runtime, secret_store)
    elif settings.runtime.runtime_type == GKE_RUNTIME_TYPE:
        return GKERuntime(settings.runtime, secret_store)
