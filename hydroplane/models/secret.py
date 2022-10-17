from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SecretSource(str, Enum):
    # Secret is stored in Hydroplane's configured secret store
    HYDROPLANE_SECRET_STORE = 'HYDROPLANE_SECRET_STORE',

    # Secret is stored in AWS SSM
    AWS_SSM = 'AWS_SSM',

    # Secret is stored in AWS Secrets Manager
    AWS_SECRETS_MANAGER = 'AWS_SECRETS_MANAGER'

    # Kubernetes Secret
    K8S_SECRET = 'K8S_SECRET'


class SecretValue(BaseModel):
    # The name of the secret within the secret store
    secret_name: str

    # (optional) if secret secret_name is an object, the key within that object that contains
    # the desired secret data
    key: Optional[str] = Field(None)

    source: Optional[SecretSource] = Field(SecretSource.HYDROPLANE_SECRET_STORE)
