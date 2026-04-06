from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


class GPUInfo(BaseModel):
    gpu_name: str = Field(..., description="GPU model name")
    gpu_usage: str = Field(..., description="GPU utilization percentage")
    memory_total: str = Field(..., description="Total memory")
    memory_used: str = Field(..., description="Used memory")
    temperature: str = Field(..., description="GPU temperature")


class ContainerInfo(BaseModel):
    name: str = Field(..., description="Container name")
    image: str = Field(..., description="Container image")
    status: str = Field(..., description="Container status")


class ServerStatus(BaseModel):
    server_id: str = Field(..., description="Server identifier")
    gpu_info: List[GPUInfo] = Field(default_factory=list)
    container_info: List[ContainerInfo] = Field(default_factory=list)
    checked_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AllServersStatus(BaseModel):
    servers: List[ServerStatus]
    polled_at: datetime
