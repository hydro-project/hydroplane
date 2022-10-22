from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SecretSource(str, Enum):
    """
    The system in which a secret is stored.
    """
    # Secret is stored in Hydroplane's configured secret store
    HYDROPLANE_SECRET_STORE = 'HYDROPLANE_SECRET_STORE',

    # Secret is stored in AWS Systems Manager Parameter Store
    AWS_SSM = 'AWS_SSM',

    # Secret is stored in AWS Secrets Manager
    AWS_SECRETS_MANAGER = 'AWS_SECRETS_MANAGER'

    # Kubernetes Secret
    K8S_SECRET = 'K8S_SECRET'


class SecretValue(BaseModel):
    """
    A reference to a secret value stored in a secret store.
    """

    secret_name: str = Field(description='the name of the secret within the secret store')

    key: Optional[str] = Field(
        None,
        description="if the secret itself is an object, the key within that object that "
        "contains the desired secret data"
    )

    source: Optional[SecretSource] = Field(
        SecretSource.HYDROPLANE_SECRET_STORE,
        description='the secret store that contains the secret'
    )
