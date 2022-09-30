from functools import lru_cache

from ..config import get_settings

from .local import LocalSecretStore, SECRET_STORE_TYPE as LOCAL_SECRET_STORE_TYPE
from .secret_store import SecretStore


@lru_cache()
def get_secret_store() -> SecretStore:
    settings = get_settings()

    if settings.secret_store.secret_store_type == LOCAL_SECRET_STORE_TYPE:
        return LocalSecretStore(settings)
