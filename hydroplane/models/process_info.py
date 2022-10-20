from typing import List, Tuple

from pydantic import BaseModel, Field, IPvAnyAddress, conint


class SocketAddress(BaseModel):
    host: IPvAnyAddress
    port: conint(ge=0, le=65535)
    is_public: bool = Field(False)


class ProcessInfo(BaseModel):
    process_name: str

    # A list of host/port pairs that the process exposes
    socket_addresses: List[SocketAddress]
