from typing import Union, Optional

from pydantic import BaseModel, Field

from .secret_stores.local import Settings as LocalSecretStoreSettings
from .runtimes.docker import Settings as DockerRuntimeSettings
from .runtimes.eks import Settings as EKSRuntimeSettings
from .utils.process_culler import Settings as ProcessCullerSettings


class Settings(BaseModel):
    # TODO: when I implement a "real" secret store, this will be a discriminated union, e.g.
    # secret_store: Union[LocalSecretStoreSettings, AWSParameterStoreSecretStoreSettings] = \
    #     Field(..., discriminator='secret_store_type')
    secret_store: LocalSecretStoreSettings

    runtime: Union[DockerRuntimeSettings, EKSRuntimeSettings] = \
        Field(..., discriminator='runtime_type')

    process_culling: Optional[ProcessCullerSettings]
