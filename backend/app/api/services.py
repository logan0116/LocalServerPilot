from fastapi import APIRouter, HTTPException
from app.models.response import APIResponse
from app.services.server_manager import server_manager
from app.services.config_manager import config_manager
from app.services.service_operations import (
    start_service, stop_service, check_service_status,
    ServiceOperationError
)

router = APIRouter(prefix="/api/v1/services", tags=["services"])


@router.post("/{server_id}/{config_id}/start", response_model=APIResponse)
async def start_service_endpoint(server_id: str, config_id: str):
    server = server_manager.get_server(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    config = config_manager.get_config(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")

    try:
        result = await start_service(server, config)
        return APIResponse(data=result)
    except ServiceOperationError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{server_id}/{config_id}/stop", response_model=APIResponse)
async def stop_service_endpoint(server_id: str, config_id: str):
    server = server_manager.get_server(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    config = config_manager.get_config(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")

    try:
        result = await stop_service(server, config)
        return APIResponse(data=result)
    except ServiceOperationError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{server_id}/{config_id}/status", response_model=APIResponse)
async def get_service_status(server_id: str, config_id: str):
    server = server_manager.get_server(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    config = config_manager.get_config(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")

    try:
        result = await check_service_status(server, config)
        return APIResponse(data=result)
    except ServiceOperationError as e:
        raise HTTPException(status_code=500, detail=str(e))
