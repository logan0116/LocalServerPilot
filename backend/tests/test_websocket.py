import pytest
from unittest.mock import AsyncMock, MagicMock
from app.core.websocket import WebSocketManager, subscribe_message, status_update_message


class TestWebSocket:
    @pytest.mark.asyncio
    async def test_websocket_subscribe_message(self):
        """TC-WS-002: 订阅特定服务器"""
        msg = subscribe_message(["server1", "server2"])
        assert msg["type"] == "subscribe"
        assert msg["data"]["server_ids"] == ["server1", "server2"]

    @pytest.mark.asyncio
    async def test_websocket_subscribe_all(self):
        """TC-WS-002b: 订阅所有服务器"""
        msg = subscribe_message([])
        assert msg["type"] == "subscribe"
        assert msg["data"]["server_ids"] == []


class TestWebSocketManager:
    def test_manager_initialization(self):
        """WebSocketManager 初始化"""
        manager = WebSocketManager()
        assert manager.active_connections == []
        assert manager._subscriptions == {}

    def test_status_update_message_format(self):
        """TC-WS-003: 状态推送消息格式"""
        status_data = {
            "server_id": "srv-1",
            "gpu_info": [],
            "container_info": []
        }
        msg = status_update_message(status_data)

        assert msg["type"] == "status_update"
        assert msg["data"]["server_id"] == "srv-1"
        assert "timestamp" in msg["data"]

    @pytest.mark.asyncio
    async def test_handle_subscribe(self):
        """订阅功能测试"""
        manager = WebSocketManager()
        mock_ws = MagicMock()
        await manager.connect(mock_ws)

        manager.handle_subscribe(mock_ws, ["server1", "server2"])

        conn_id = id(mock_ws)
        assert conn_id in manager._subscriptions
        assert "server1" in manager._subscriptions[conn_id]
        assert "server2" in manager._subscriptions[conn_id]

    @pytest.mark.asyncio
    async def test_broadcast_to_all(self):
        """广播到所有连接"""
        manager = WebSocketManager()
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()
        await manager.connect(mock_ws1)
        await manager.connect(mock_ws2)

        await manager.broadcast({"type": "test", "data": {}})

        mock_ws1.send_json.assert_called_once()
        mock_ws2.send_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_status_to_subscribed_servers(self):
        """只向订阅的服务器发送状态"""
        manager = WebSocketManager()
        mock_ws = AsyncMock()
        await manager.connect(mock_ws)
        manager.handle_subscribe(mock_ws, ["srv-1"])

        await manager.send_status_update("srv-1", {"gpu_info": []})

        mock_ws.send_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_status_to_unsubscribed_server(self):
        """未订阅的服务器不发送状态"""
        manager = WebSocketManager()
        mock_ws = AsyncMock()
        await manager.connect(mock_ws)
        manager.handle_subscribe(mock_ws, ["srv-1"])

        await manager.send_status_update("srv-2", {"gpu_info": []})

        mock_ws.send_json.assert_not_called()

    @pytest.mark.asyncio
    async def test_empty_subscription_receives_all(self):
        """空订阅接收所有状态"""
        manager = WebSocketManager()
        mock_ws = AsyncMock()
        await manager.connect(mock_ws)
        manager.handle_subscribe(mock_ws, [])

        await manager.send_status_update("srv-2", {"gpu_info": []})

        mock_ws.send_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_removes_subscription(self):
        """断开连接时移除订阅"""
        manager = WebSocketManager()
        mock_ws = MagicMock()
        await manager.connect(mock_ws)
        conn_id = id(mock_ws)
        manager.handle_subscribe(mock_ws, ["srv-1"])

        await manager.disconnect(mock_ws)

        assert conn_id not in manager._subscriptions
        assert mock_ws not in manager.active_connections
