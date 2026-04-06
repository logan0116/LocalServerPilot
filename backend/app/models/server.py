from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class ServerBase(BaseModel):
    name: str = Field(..., description="Server display name")
    ip: str = Field(..., description="Server IP address")
    user: str = Field(..., description="SSH username")
    port: int = Field(default=22, description="SSH port")


class ServerCreate(ServerBase):
    password: Optional[str] = Field(None, description="SSH password")
    private_key: Optional[str] = Field(None, description="Path to private key")


class ServerUpdate(BaseModel):
    name: Optional[str] = None
    ip: Optional[str] = None
    user: Optional[str] = None
    port: Optional[int] = None
    password: Optional[str] = None
    private_key: Optional[str] = None


class Server(ServerBase):
    id: str = Field(..., description="Unique server identifier")
    password: Optional[str] = None
    private_key: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ServerListResponse(BaseModel):
    items: List[Server]
    total: int


class ServerTestResponse(BaseModel):
    success: bool
    message: str
