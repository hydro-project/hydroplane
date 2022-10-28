from abc import ABC, abstractmethod
from typing import List, Optional

from ..models.process_info import ProcessInfo
from ..models.process_spec import ProcessSpec


class Runtime(ABC):
    @abstractmethod
    def start_process(self, process_spec: ProcessSpec):
        pass

    @abstractmethod
    def stop_process(self, process_name: str):
        pass

    @abstractmethod
    def list_processes(self, group: Optional[str]) -> List[ProcessInfo]:
        pass

    @abstractmethod
    def refresh_api_clients(self):
        pass
