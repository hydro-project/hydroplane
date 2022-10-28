from typing import List, Optional, Tuple

from pydantic import BaseModel, Field, IPvAnyAddress, conint


class SocketAddress(BaseModel):
    host: IPvAnyAddress = Field(description="the IP address of the socket's host")
    port: conint(ge=0, le=65535) = Field(description="the socket's port number")
    is_public: bool = Field(False, description='if true, the socket is publicly accessible')


class ProcessInfo(BaseModel):
    """
    Information about a running process.
    """
    process_name: str = Field(description="the name of the process")
    group: Optional[str] = Field(None, description="the group to which the process belongs, if any")

    # A list of host/port pairs that the process exposes
    socket_addresses: List[SocketAddress] = Field(
        description='a list of socket addresses that the process is exposing'
    )
