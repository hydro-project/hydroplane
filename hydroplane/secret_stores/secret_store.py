from abc import ABC, abstractmethod

from ..models.secret import SecretValue


class SecretStore(ABC):
    @abstractmethod
    def get_secret(self, secret_value: SecretValue) -> str:
        pass
