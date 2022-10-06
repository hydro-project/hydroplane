from typing import Optional, List, Union

from pydantic import BaseModel, Field, conint, validator

from .secret import SecretValue


class PortMapping(BaseModel):
    container_port: conint(ge=1, le=65535)
    host_port: Optional[conint(ge=1, le=65535)]

    @validator('host_port', pre=True, always=True)
    def default_host_port(cls, v, *, values, **kwargs):
        # If host port isn't provided, set it to container port
        return v or values.get('container_port')


class EnvironmentVariable(BaseModel):
    name: str
    value: Union[SecretValue, str]


class ContainerSpec(BaseModel):
    image_uri: str

    ports: List[PortMapping] = Field(default_factory=lambda: [])
    env: List[EnvironmentVariable] = Field(default_factory=lambda: [])
    command: Optional[List[str]] = Field(None)
    username: Optional[Union[str, SecretValue]] = Field(None)
    password: Optional[SecretValue] = Field(None)
