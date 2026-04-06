from fastapi import APIRouter, HTTPException
from app.models.config import (
    ServiceConfig, ServiceConfigCreate, ServiceConfigUpdate,
    ServiceConfigListResponse
)
from app.models.response import APIResponse
from app.services.config_manager import config_manager

router = APIRouter(prefix="/api/v1/configs", tags=["configs"])


@router.get("", response_model=APIResponse)
async def list_configs():
    configs = config_manager.list_configs()
    return APIResponse(
        data={"items": [c.model_dump() for c in configs], "total": len(configs)}
    )


@router.get("/{config_id}", response_model=APIResponse)
async def get_config(config_id: str):
    config = config_manager.get_config(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    return APIResponse(data=config.model_dump())


@router.post("", status_code=201, response_model=APIResponse)
async def create_config(config_data: ServiceConfigCreate):
    config = config_manager.create_config(config_data)
    return APIResponse(data=config.model_dump())


@router.put("/{config_id}", response_model=APIResponse)
async def update_config(config_id: str, update_data: ServiceConfigUpdate):
    config = config_manager.update_config(config_id, update_data)
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    return APIResponse(data=config.model_dump())


@router.delete("/{config_id}", status_code=204)
async def delete_config(config_id: str):
    success = config_manager.delete_config(config_id)
    if not success:
        raise HTTPException(status_code=404, detail="Config not found")
