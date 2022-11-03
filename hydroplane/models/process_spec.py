from typing import Optional

from pydantic import BaseModel, Field

from .container_spec import ContainerSpec


class ProcessSpec(BaseModel):
    """
    Provides all the details of the processs that you'd like to launch.
    """

    process_name: str = Field(description='the name of the process to launch')
    group: Optional[str] = Field(None, description='the name of the group to which the '
                                 'process belongs, if any')

    container: ContainerSpec

    has_public_ip: bool = Field(
        False,
        description='if true, the process has a publicly-exposed IP'
    )
