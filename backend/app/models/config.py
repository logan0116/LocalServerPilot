from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class ServiceConfigBase(BaseModel):
    name: str = Field(..., description="Service name")
    start_command: str = Field(..., description="Command to start service")
    stop_command: str = Field(..., description="Command to stop service")


class ServiceConfigCreate(ServiceConfigBase):
    description: Optional[str] = Field(None, description="Service description")
    image_depend: List[str] = Field(default_factory=list, description="Dependent images")
    if_gpu: bool = Field(default=False, description="Whether GPU is required")
    allow_server: List[str] = Field(default_factory=list, description="Allowed servers")


class ServiceConfigUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_depend: Optional[List[str]] = None
    if_gpu: Optional[bool] = None
    allow_server: Optional[List[str]] = None
    start_command: Optional[str] = None
    stop_command: Optional[str] = None


class ServiceConfig(ServiceConfigBase):
    id: str = Field(..., description="Unique config identifier")
    description: Optional[str] = None
    image_depend: List[str] = Field(default_factory=list)
    if_gpu: bool = False
    allow_server: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ServiceConfigListResponse(BaseModel):
    items: List[ServiceConfig]
    total: int
