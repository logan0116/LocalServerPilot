import pytest
from unittest.mock import MagicMock
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.server import Server
from app.services.server_manager import ServerManager


@pytest.fixture
def mock_server_manager(mocker):
    """Mock ServerManager"""
    mock = mocker.patch("app.api.servers.server_manager")
    return mock


@pytest.fixture
def sample_server():
    return Server(
        id="srv-1",
        name="Test Server",
        ip="192.168.1.100",
        user="admin",
        password="secret",
        port=22
    )


class TestServersAPI:
    @pytest.mark.asyncio
    async def test_get_servers_empty(self, mocker):
        """TC-SERVER-001a: 获取空服务器列表"""
        mocker.patch("app.api.servers.server_manager.list_servers", return_value=[])

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/servers")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["items"] == []
        assert data["data"]["total"] == 0

    @pytest.mark.asyncio
    async def test_get_servers_with_data(self, mocker, sample_server):
        """TC-SERVER-001b: 获取服务器列表（有数据）"""
        mocker.patch(
            "app.api.servers.server_manager.list_servers",
            return_value=[sample_server]
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/servers")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]["items"]) == 1
        assert data["data"]["items"][0]["name"] == "Test Server"

    @pytest.mark.asyncio
    async def test_get_server_by_id(self, mocker, sample_server):
        """TC-SERVER-002: 获取服务器详情"""
        mocker.patch(
            "app.api.servers.server_manager.get_server",
            return_value=sample_server
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/servers/srv-1")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == "srv-1"

    @pytest.mark.asyncio
    async def test_get_server_not_found(self, mocker):
        """TC-SERVER-003: 服务器不存在"""
        mocker.patch(
            "app.api.servers.server_manager.get_server",
            return_value=None
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/servers/nonexistent")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_server(self, mocker):
        """TC-SERVER-006: 新增服务器"""
        new_server_data = {
            "name": "New Server",
            "ip": "192.168.1.200",
            "user": "admin",
            "password": "secret"
        }
        mocker.patch(
            "app.api.servers.server_manager.create_server",
            return_value=Server(id="srv-new", **new_server_data)
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/v1/servers", json=new_server_data)

        assert response.status_code == 201
        data = response.json()
        assert data["data"]["id"] == "srv-new"

    @pytest.mark.asyncio
    async def test_update_server(self, mocker, sample_server):
        """TC-SERVER-007: 更新服务器"""
        updated_data = {"name": "Updated Name"}
        mocker.patch(
            "app.api.servers.server_manager.update_server",
            return_value=Server(**{**sample_server.model_dump(), "name": "Updated Name"})
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.put(
                "/api/v1/servers/srv-1",
                json=updated_data
            )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == "Updated Name"

    @pytest.mark.asyncio
    async def test_delete_server(self, mocker):
        """TC-SERVER-008: 删除服务器"""
        mocker.patch(
            "app.api.servers.server_manager.delete_server",
            return_value=True
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete("/api/v1/servers/srv-1")

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_test_server_connection_success(self, mocker, sample_server):
        """TC-SERVER-009: 连接测试成功"""
        mocker.patch(
            "app.api.servers.server_manager.get_server",
            return_value=sample_server
        )
        from unittest.mock import AsyncMock
        mock_executor = MagicMock()
        mock_executor.test_connection = AsyncMock(return_value=True)
        mocker.patch(
            "app.api.servers.SSHExecutor",
            return_value=mock_executor
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/v1/servers/srv-1/test")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["success"] is True

    @pytest.mark.asyncio
    async def test_test_server_connection_failure(self, mocker, sample_server):
        """TC-SERVER-010: 连接测试失败"""
        mocker.patch(
            "app.api.servers.server_manager.get_server",
            return_value=sample_server
        )
        mocker.patch(
            "app.services.ssh_executor.SSHExecutor.test_connection",
            return_value=False
        )
        mocker.patch(
            "app.services.ssh_executor.SSHExecutor.close"
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/v1/servers/srv-1/test")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["success"] is False
