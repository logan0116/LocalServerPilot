from pydantic import BaseModel
from typing import Optional, Any


class APIResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None


class ServiceOperationResponse(BaseModel):
    success: bool
    output: str
    error: Optional[str] = None
