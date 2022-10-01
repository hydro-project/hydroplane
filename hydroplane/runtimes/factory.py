from functools import lru_cache
from typing import TYPE_CHECKING

from .docker import DockerRuntime, RUNTIME_TYPE as DOCKER_RUNTIME_TYPE
from .runtime import Runtime
from ..secret_stores.secret_store import SecretStore

if TYPE_CHECKING:
    from ..config import Settings


# FIXME resolve circular import and make get_runtime() retrieve settings so that it can be cached
# (currently, Settings is unhashable, os lru_cache won't work)
# @lru_cache()
def get_runtime(secret_store: SecretStore, settings: "Settings") -> Runtime:
    if settings.runtime.runtime_type == DOCKER_RUNTIME_TYPE:
        return DockerRuntime(settings.runtime, secret_store)
