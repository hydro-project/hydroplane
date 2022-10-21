from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from .container_spec import ContainerSpec


class ProcessSpec(BaseModel):
    process_name: str
    container: ContainerSpec

    has_public_ip: bool = Field(False)
