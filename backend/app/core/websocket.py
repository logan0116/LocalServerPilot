from typing import List, Dict, Set
from datetime import datetime
import json


class WebSocketManager:
    def __init__(self):
        self.active_connections: List = []
        self._subscriptions: Dict = {}

    async def connect(self, websocket):
        self.active_connections.append(websocket)
        self._subscriptions[id(websocket)] = set()

    async def disconnect(self, websocket):
        conn_id = id(websocket)
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if conn_id in self._subscriptions:
            del self._subscriptions[conn_id]

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

    async def send_status_update(self, server_id: str, status_data: dict):
        message = status_update_message({
            "server_id": server_id,
            **status_data
        })
        for connection in self.active_connections:
            conn_id = id(connection)
            subscribed = self._subscriptions.get(conn_id, set())
            if not subscribed or server_id in subscribed:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

    def handle_subscribe(self, websocket, server_ids: List[str]):
        conn_id = id(websocket)
        self._subscriptions[conn_id] = set(server_ids)


def subscribe_message(server_ids: List[str]) -> dict:
    return {
        "type": "subscribe",
        "data": {
            "server_ids": server_ids
        }
    }


def status_update_message(data: dict) -> dict:
    return {
        "type": "status_update",
        "data": {
            **data,
            "timestamp": datetime.now().isoformat()
        }
    }


ws_manager = WebSocketManager()
