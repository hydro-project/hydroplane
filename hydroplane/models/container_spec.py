from decimal import Decimal
from enum import Enum
from typing import Dict, Optional, List, Union

from pydantic import BaseModel, Field, conint, condecimal, validator

from .secret import ProcessSecret


class PortProtocol(str, Enum):
    TCP = 'tcp',
    UDP = 'udp'


class PortMapping(BaseModel):
    """
    A port inside the container that will be exposed to the outside world.
    """
    container_port: conint(ge=1, le=65535) = Field(
        description='the port that the container will be listening on'
    )

    host_port: Optional[conint(ge=1, le=65535)] = Field(
        description='the port that the host will expose. Some runtimes may not honor this setting.'
    )

    protocol: PortProtocol = Field(
        default=PortProtocol.TCP,
        description='the protocol spoken by the bound port'
    )

    name: Optional[str] = Field(
        None,
        description='the name of the port binding; passed to some runtimes'
    )

    @validator('host_port', pre=True, always=True)
    def default_host_port(cls, v, *, values, **kwargs):
        """If the host port isn't specified, set it to the container port."""
        return v or values.get('container_port')


class EnvironmentVariable(BaseModel):
    """
    An environment variable that will be provided to the process's runtime environment.
    """
    name: str = Field(description='the name of the environment variable')
    value: Union[ProcessSecret, str] = Field(
        description="the environment variable's value; "
        "can be a literal, or a reference to a secret"
    )


class ResourceSpec(BaseModel):
    """
    Encapsulates either a request or limit on the physical resources allocated to a process by
    the runtime.
    """
    cpu_vcpu: Optional[condecimal(ge=Decimal("0.001"))] = Field(
        None,
        description='the number of abstract vCPUs'
    )
    memory_mib: Optional[conint(ge=0)] = Field(
        None,
        description='the number of MiB of memory'
    )


class ContainerSpec(BaseModel):
    image_uri: str = Field(
        description='the URI of a Docker image that the process will run. Can be a '
        'fully-qualified URI, or as a shorthand (e.g. "python" or "nginxdemos/hello" )'
    )
    username: Optional[Union[str, ProcessSecret]] = Field(
        None,
        description='the username used to authenticate with the container registry'
    )
    password: Optional[ProcessSecret] = Field(
        None,
        description='the password used to authenticate with the container registry'
    )

    ports: List[PortMapping] = Field(
        default_factory=lambda: [],
        description='a list of ports that the container should expose'
    )
    env: List[EnvironmentVariable] = Field(
        default_factory=lambda: [],
        description="a list of environment variables that should be given to "
        "the container's runtime"
    )
    command: Optional[List[str]] = Field(
        None,
        description='the command that the container should run'
    )

    resource_request: Optional[ResourceSpec] = Field(
        None,
        description='a request for physical resources that should be allocated to the container'
    )

    resource_limit: Optional[ResourceSpec] = Field(
        None,
        description='a limit on the amount of physical resources that the container is '
        'allowed to consume'
    )

    node_selector: Optional[Dict[str, str]] = Field(
        None,
        description='a collection of label name/label value pairs. if this collection is specified and the runtime supports it, this process will only be scheduled onto a node that has these labels'
    )

    @validator('resource_limit')
    def requests_cannot_exceed_limits(cls, v, *, values, **kwargs):
        """
        If both resource requests and resource limits are specified, ensure that the resource
        request doesn't exceed the resource limit.
        """

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
