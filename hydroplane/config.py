from functools import lru_cache
from getpass import getpass
import os
from typing import Union

from pydantic import BaseSettings, Field, SecretStr

from .secret_stores.local import Settings as LocalSecretStoreSettings
from .runtimes.docker import Settings as DockerRuntimeSettings
from .runtimes.eks import Settings as EKSRuntimeSettings


class Settings(BaseSettings):
    # TODO: when I implement a "real" secret store, this will be a discriminated union, e.g.
    # secret_store: Union[LocalSecretStoreSettings, AWSParameterStoreSecretStoreSettings] = \
    #     Field(..., discriminator='secret_store_type')
    secret_store: LocalSecretStoreSettings

    # TODO: same here when there's more than one runtime
    runtime: Union[DockerRuntimeSettings, EKSRuntimeSettings] = \
        Field(..., discriminator='runtime_type')

    class Config:
        case_sensitive = False
        env_file = os.getenv('ENV_FILE', '.env')


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()

    if settings.secret_store.secret_store_type == 'local':
        settings.secret_store.password = SecretStr(
            getpass('Enter local secret store password: ').strip()
        )
        if len(settings.secret_store.password) == 0:
            raise ValueError('Must provide a password for local secret stores')

    return settings
