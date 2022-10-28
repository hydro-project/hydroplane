from .local import LocalSecretStore, SECRET_STORE_TYPE as LOCAL_SECRET_STORE_TYPE
from .secret_store import SecretStore
from ..config import Settings


def get_secret_store(settings: Settings) -> SecretStore:
    if settings.secret_store.secret_store_type == LOCAL_SECRET_STORE_TYPE:
        return LocalSecretStore(settings.secret_store)
