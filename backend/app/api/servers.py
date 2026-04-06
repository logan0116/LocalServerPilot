from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.server import (
    Server, ServerCreate, ServerUpdate,
    ServerListResponse, ServerTestResponse
)
from app.models.response import APIResponse
from app.services.server_manager import server_manager
from app.services.ssh_executor import SSHExecutor, SSHError

router = APIRouter(prefix="/api/v1/servers", tags=["servers"])


@router.get("", response_model=APIResponse)
async def list_servers():
    servers = server_manager.list_servers()
    return APIResponse(
        data={"items": [s.model_dump() for s in servers], "total": len(servers)}
    )


@router.get("/{server_id}", response_model=APIResponse)
async def get_server(server_id: str):
    server = server_manager.get_server(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return APIResponse(data=server.model_dump())


@router.post("", status_code=201, response_model=APIResponse)
async def create_server(server_data: ServerCreate):
    server = server_manager.create_server(server_data)
    return APIResponse(data=server.model_dump())


@router.put("/{server_id}", response_model=APIResponse)
async def update_server(server_id: str, update_data: ServerUpdate):
    server = server_manager.update_server(server_id, update_data)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return APIResponse(data=server.model_dump())


@router.delete("/{server_id}", status_code=204)
async def delete_server(server_id: str):
    success = server_manager.delete_server(server_id)
    if not success:
        raise HTTPException(status_code=404, detail="Server not found")


@router.post("/{server_id}/test", response_model=APIResponse)
async def test_server_connection(server_id: str):
    server = server_manager.get_server(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    try:
        executor = SSHExecutor(server)
        connected = await executor.test_connection()
        executor.close()

        if connected:
            return APIResponse(data={"success": True, "message": "Connection successful"})
        else:
            return APIResponse(data={"success": False, "message": "Connection test failed"})
    except SSHError as e:
        return APIResponse(data={"success": False, "message": str(e)})
