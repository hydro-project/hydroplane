from typing import Optional

from pydantic import BaseModel, Field


class SecretValue(BaseModel):
    # The name of the secret within the secret store
    secret_name: str

    # (optional) if secret secret_name is an object, the key within that object that contains
    # the desired secret data
    key: Optional[str] = Field(None)
