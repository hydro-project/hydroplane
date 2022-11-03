from typing import Optional

from pydantic import BaseModel, Field


class HydroplaneSecret(BaseModel):
    """
    A reference to a secret in Hydroplane's secret store that Hydroplane will use to authenticate
    with the runtime.
    """

    secret_name: str = Field(description='the name of the secret')

    key: Optional[str] = Field(
        None,
        description="if the secret itself is an object, the key within that object that "
        "contains the desired secret data"
    )


class ProcessSecret(BaseModel):
    """
    A reference to a secret value that the process will need to run.
    """

    secret_name: str = Field(description='the name of the secret')

    key: Optional[str] = Field(
        None,
        description="if the secret itself is an object, the key within that object that "
        "contains the desired secret data"
    )
