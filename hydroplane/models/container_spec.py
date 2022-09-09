from dataclasses import dataclass
from typing import Optional, List, Union

from .value_types import SecretValue


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
    ports: List[PortMapping]
    env: List[EnvironmentVariable]
    command: List[str]
