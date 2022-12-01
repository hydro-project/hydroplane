from typing import Literal

from pydantic import BaseModel

from .secret_store import SecretStore
from ..models.secret import HydroplaneSecret


SECRET_STORE_TYPE = 'none'


class Settings(BaseModel):
    secret_store_type: Literal[SECRET_STORE_TYPE] = SECRET_STORE_TYPE


class NoOpSecretStore(SecretStore):
    def __init__(self, settings: Settings):
        pass

    def get_secret(self, secret_value: HydroplaneSecret) -> str:
        raise NotImplementedError(
            f"Hydroplane's runtime requested the secret '{secret_value}' from the "
            "secret store, but you're using the 'none' secret store, and it "
            "doesn't actually store any secrets. You need to configure a real secret "
            "store in order to use this runtime. See "
            "https://hydro-project.github.io/hydroplane/secrets.html#hydroplane-secrets "
            "for more information."
        )
