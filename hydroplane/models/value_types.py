from dataclasses import dataclass
from typing import Optional


@dataclass
class SecretValue:
    secret_name: str
    key: Optional[str]
