from .local import LocalSecretStore, SECRET_STORE_TYPE as LOCAL_SECRET_STORE_TYPE
from .none import NoOpSecretStore, SECRET_STORE_TYPE as NONE_SECRET_STORE_TYPE
from .secret_store import SecretStore
from ..config import Settings


def get_secret_store(settings: Settings) -> SecretStore:
    if settings.secret_store.secret_store_type == LOCAL_SECRET_STORE_TYPE:
        return LocalSecretStore(settings.secret_store)
    elif settings.secret_store.secret_store_type == NONE_SECRET_STORE_TYPE:
        return NoOpSecretStore(settings.secret_store)
    else:
        raise ValueError(f"Unknown secret store type '{settings.secret_store.secret_store_type}'")
