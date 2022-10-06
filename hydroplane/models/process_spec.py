from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from .container_spec import ContainerSpec


class ProcessSpec(BaseModel):
    process_name: str
    container: ContainerSpec
    orchestrator_config: Optional[Dict[str, Any]] = Field(default_factory=lambda: {})
