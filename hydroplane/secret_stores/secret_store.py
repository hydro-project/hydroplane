from abc import ABC, abstractmethod

from ..models.secret import HydroplaneSecret


class SecretStore(ABC):
    @abstractmethod
    def get_secret(self, secret_value: HydroplaneSecret) -> str:
        pass
