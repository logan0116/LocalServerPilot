from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import List
from app.models.response import APIResponse
from app.models.status import ServerStatus, AllServersStatus
from app.services.server_manager import server_manager
from app.services.status_service import status_service

router = APIRouter(prefix="/api/v1", tags=["status"])


async def get_server_status(server_id: str) -> ServerStatus:
    server = server_manager.get_server(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return await status_service.get_server_status(server)


async def get_gpu_status(server_id: str):
    server = server_manager.get_server(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return await status_service.get_gpu_status(server)


async def get_container_status(server_id: str):
    server = server_manager.get_server(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return await status_service.get_container_status(server)


async def poll_all_servers_status() -> AllServersStatus:
    servers = server_manager.list_servers()
    statuses = []
    for server in servers:
        status = await status_service.get_server_status(server)
        statuses.append(status)
    return AllServersStatus(servers=statuses, polled_at=datetime.now())


@router.get("/servers/{server_id}/status", response_model=APIResponse)
async def get_server_status_endpoint(server_id: str):
    status = await get_server_status(server_id)
    return APIResponse(data=status.model_dump())


@router.get("/servers/{server_id}/gpu", response_model=APIResponse)
async def get_gpu_status_endpoint(server_id: str):
    gpu_status = await get_gpu_status(server_id)
    return APIResponse(data=[g.model_dump() for g in gpu_status])


@router.get("/servers/{server_id}/containers", response_model=APIResponse)
async def get_container_status_endpoint(server_id: str):
    container_status = await get_container_status(server_id)
    return APIResponse(data=[c.model_dump() for c in container_status])


@router.get("/status/poll", response_model=APIResponse)
async def poll_all_servers():
    all_status = await poll_all_servers_status()
    return APIResponse(data={
        "servers": [s.model_dump() for s in all_status.servers],
        "polled_at": all_status.polled_at.isoformat()
    })
