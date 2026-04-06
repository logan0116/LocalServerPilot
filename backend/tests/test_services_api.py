import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.server import Server
from app.models.config import ServiceConfig
from app.services.service_operations import ServiceOperationError


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


@pytest.fixture
def sample_config():
    return ServiceConfig(
        id="cfg-1",
        name="TestService",
        description="A test service",
        image_depend=["python:3.10"],
        if_gpu=True,
        allow_server=["server1"],
        start_command="python start.py",
        stop_command="python stop.py"
    )


class TestServicesAPI:
    @pytest.mark.asyncio
    async def test_start_service_success(self, mocker, sample_server, sample_config):
        """TC-SVC-001: 启动服务成功"""
        mocker.patch(
            "app.api.services.server_manager.get_server",
            return_value=sample_server
        )
        mocker.patch(
            "app.api.services.config_manager.get_config",
            return_value=sample_config
        )
        mocker.patch(
            "app.api.services.start_service",
            return_value={"success": True, "output": "Started"}
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/v1/services/srv-1/cfg-1/start")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["success"] is True

    @pytest.mark.asyncio
    async def test_stop_service_success(self, mocker, sample_server, sample_config):
        """TC-SVC-002: 停止服务成功"""
        mocker.patch(
            "app.api.services.server_manager.get_server",
            return_value=sample_server
        )
        mocker.patch(
            "app.api.services.config_manager.get_config",
            return_value=sample_config
        )
        mocker.patch(
            "app.api.services.stop_service",
            return_value={"success": True, "output": "Stopped"}
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/v1/services/srv-1/cfg-1/stop")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["success"] is True

    @pytest.mark.asyncio
    async def test_get_service_status(self, mocker, sample_server, sample_config):
        """TC-SVC-003: 查看服务状态"""
        mocker.patch(
            "app.api.services.server_manager.get_server",
            return_value=sample_server
        )
        mocker.patch(
            "app.api.services.config_manager.get_config",
            return_value=sample_config
        )
        mocker.patch(
            "app.api.services.check_service_status",
            return_value={"running": True, "output": "process info"}
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/services/srv-1/cfg-1/status")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["running"] is True

    @pytest.mark.asyncio
    async def test_server_not_found(self, mocker):
        """TC-SVC-004: 目标服务器不存在"""
        mocker.patch("app.api.services.server_manager.get_server", return_value=None)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/v1/services/nonexistent/cfg-1/start")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_ssh_execution_timeout(self, mocker, sample_server, sample_config):
        """TC-SVC-005: SSH 执行超时"""
        mocker.patch(
            "app.api.services.server_manager.get_server",
            return_value=sample_server
        )
        mocker.patch(
            "app.api.services.config_manager.get_config",
            return_value=sample_config
        )
        mocker.patch(
            "app.api.services.start_service",
            side_effect=ServiceOperationError("Command timed out")
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/v1/services/srv-1/cfg-1/start")

        assert response.status_code == 500
