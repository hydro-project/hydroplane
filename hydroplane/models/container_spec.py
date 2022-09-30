from dataclasses import dataclass
from typing import Optional, List, Union

from .secret import SecretValue


@dataclass
class PortMapping:
    container_port: int
    host_port: Optional[int]


@dataclass
class EnvironmentVariable:
    name: str
    value: Union[SecretValue, str]


@dataclass
class ContainerSpec:
    image_uri: str
    username: Optional[Union[str, SecretValue]]
    password: Optional[SecretValue]
    ports: List[PortMapping]
    env: List[EnvironmentVariable]
    command: List[str]
