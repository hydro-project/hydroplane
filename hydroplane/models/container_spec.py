from decimal import Decimal
from typing import Optional, List, Union

from pydantic import BaseModel, Field, conint, condecimal, validator

from .secret import SecretValue


class PortMapping(BaseModel):
    container_port: conint(ge=1, le=65535)
    host_port: Optional[conint(ge=1, le=65535)]
    name: Optional[str] = Field(None)

    @validator('host_port', pre=True, always=True)
    def default_host_port(cls, v, *, values, **kwargs):
        # If host port isn't provided, set it to container port
        return v or values.get('container_port')


class EnvironmentVariable(BaseModel):
    name: str
    value: Union[SecretValue, str]


class ResourceSpec(BaseModel):
    cpu_vcpu: Optional[condecimal(ge=Decimal("0.001"))] = Field(None)
    memory_mib: Optional[conint(ge=0)] = Field(None)


class ContainerSpec(BaseModel):
    image_uri: str
    username: Optional[Union[str, SecretValue]] = Field(None)
    password: Optional[SecretValue] = Field(None)

    ports: List[PortMapping] = Field(default_factory=lambda: [])
    env: List[EnvironmentVariable] = Field(default_factory=lambda: [])
    command: Optional[List[str]] = Field(None)

    resource_request: Optional[ResourceSpec] = Field(None)
    resource_limit: Optional[ResourceSpec] = Field(None)

    @validator('resource_limit')
    def requests_cannot_exceed_limits(cls, v, *, values, **kwargs):
        if (
                v is not None and
                'resource_request' in values
        ):
            resource_request = values['resource_request']

            if resource_request is not None:
                if (
                        resource_request.cpu_vcpu is not None and
                        v.cpu_vcpu is not None and
                        resource_request.cpu_vcpu > v.cpu_vcpu
                ):
                    raise ValueError(f'Requested vCPUs ({resource_request.cpu_vcpu}) '
                                     f'exceeds limit ({v.cpu_vcpu})')

                if (
                        resource_request.memory_mib is not None and
                        v.memory_mib is not None and
                        resource_request.memory_mib > v.memory_mib
                ):
                    raise ValueError(f'Requested memory ({resource_request.memory_mib} MiB) '
                                     f'exceeds limit ({v.memory_mib} MiB)')

        return v
