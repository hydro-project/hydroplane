from typing import Union, Optional

from pydantic import BaseModel, Field

from .secret_stores.local import Settings as LocalSecretStoreSettings
from .secret_stores.none import Settings as NoOpSecretStoreSettings
from .runtimes.docker import Settings as DockerRuntimeSettings
from .runtimes.eks import Settings as EKSRuntimeSettings
from .runtimes.gke import Settings as GKERuntimeSettings
from .utils.process_culler import Settings as ProcessCullerSettings


class Settings(BaseModel):
    secret_store: Union[LocalSecretStoreSettings, NoOpSecretStoreSettings] = \
        Field(..., discriminator='secret_store_type')

    runtime: Union[DockerRuntimeSettings, EKSRuntimeSettings, GKERuntimeSettings] = \
        Field(..., discriminator='runtime_type')

    process_culling: Optional[ProcessCullerSettings]
