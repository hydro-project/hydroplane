from functools import lru_cache

from .local import LocalSecretStore, SECRET_STORE_TYPE as LOCAL_SECRET_STORE_TYPE
from .secret_store import SecretStore
from ..config import get_settings


@lru_cache()
def get_secret_store() -> SecretStore:
    settings = get_settings()
    if settings.secret_store.secret_store_type == LOCAL_SECRET_STORE_TYPE:
        return LocalSecretStore(settings.secret_store)
