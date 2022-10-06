from abc import ABC, abstractmethod

from ..models.process_spec import ProcessSpec


class Runtime(ABC):
    @abstractmethod
    def start_process(self, process_spec: ProcessSpec):
        pass

    @abstractmethod
    def stop_process(self, process_name: str):
        pass
