from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .container_spec import ContainerSpec


@dataclass
class ProcessSpec:
    process_name: str
    docker_image_uri: str
    container: ContainerSpec
    orchestrator_config: Optional[Dict[str, Any]]
