from abc import ABC, abstractmethod
from typing import Dict, Optional, Union


class SecretStore(ABC):
    @abstractmethod
    def get_secret(self, secret_name: str) -> str:
        pass
