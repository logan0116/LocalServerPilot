from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json

from app.api import servers, configs, services, status
from app.core.websocket import ws_manager, subscribe_message
from app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(status_broadcast_loop())
    yield


app = FastAPI(
    title="LocalServerPilot API",
    description="Backend API for LocalServerPilot server management platform",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(servers.router)
app.include_router(configs.router)
app.include_router(services.router)
app.include_router(status.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {
        "name": "LocalServerPilot API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.websocket("/ws/status")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "subscribe":
                    server_ids = message.get("data", {}).get("server_ids", [])
                    ws_manager.handle_subscribe(websocket, server_ids)
                    await websocket.send_json(subscribe_message(server_ids))
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)


async def status_broadcast_loop():
    settings = get_settings()
    while True:
        await asyncio.sleep(settings.status.poll_interval)
        try:
            all_status = await status.poll_all_servers_status()
            for server_status in all_status.servers:
                await ws_manager.send_status_update(
                    server_status.server_id,
                    {
                        "gpu_info": [g.model_dump() for g in server_status.gpu_info],
                        "container_info": [c.model_dump() for c in server_status.container_info]
                    }
                )
        except Exception:
            pass
