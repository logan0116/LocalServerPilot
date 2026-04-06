import pytest
from datetime import datetime
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.status import ServerStatus, GPUInfo, ContainerInfo, AllServersStatus


@pytest.fixture
def mock_status_service(mocker):
    return mocker.patch("app.api.status.status_service")


@pytest.fixture
def sample_status():
    return ServerStatus(
        server_id="srv-1",
        gpu_info=[
            GPUInfo(
                gpu_name="NVIDIA GeForce RTX 3090",
                gpu_usage="45%",
                memory_total="24576MiB",
                memory_used="16384MiB",
                temperature="65C"
            )
        ],
        container_info=[
            ContainerInfo(
                name="model-server-1",
                image="registry.example.com/model:v1",
                status="Up 2 hours"
            )
        ]
    )


class TestStatusAPI:
    @pytest.mark.asyncio
    async def test_get_server_status(self, mocker, sample_status):
        """TC-STAT-001: 获取服务器完整状态"""
        mocker.patch(
            "app.api.status.get_server_status",
            return_value=sample_status
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/servers/srv-1/status")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["gpu_info"]) == 1
        assert len(data["data"]["container_info"]) == 1

    @pytest.mark.asyncio
    async def test_get_gpu_status_only(self, mocker, sample_status):
        """TC-STAT-002: 仅获取 GPU 状态"""
        mocker.patch(
            "app.api.status.get_gpu_status",
            return_value=sample_status.gpu_info
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/servers/srv-1/gpu")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert "gpu_name" in data["data"][0]

    @pytest.mark.asyncio
    async def test_get_container_status_only(self, mocker, sample_status):
        """TC-STAT-003: 仅获取容器状态"""
        mocker.patch(
            "app.api.status.get_container_status",
            return_value=sample_status.container_info
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/servers/srv-1/containers")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1

    @pytest.mark.asyncio
    async def test_poll_all_servers_status(self, mocker, sample_status):
        """TC-STAT-004: 轮询所有服务器状态"""
        all_status = AllServersStatus(servers=[sample_status], polled_at=datetime.now())
        mocker.patch(
            "app.api.status.poll_all_servers_status",
            return_value=all_status
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/status/poll")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["servers"]) == 1
