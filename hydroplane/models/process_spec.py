from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from .container_spec import ContainerSpec


class ProcessSpec(BaseModel):
    """
    Provides all the details of the processs that you'd like to launch.
    """

    process_name: str = Field(description='the name of the process to launch')

    container: ContainerSpec

    has_public_ip: bool = Field(
        False,
        description='if true, the process has a publicly-exposed IP'
    )
