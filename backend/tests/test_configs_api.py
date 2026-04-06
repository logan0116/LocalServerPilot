import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.config import ServiceConfig


@pytest.fixture
def mock_config_manager(mocker):
    """Mock ConfigManager"""
    mock = mocker.patch("app.api.configs.config_manager")
    return mock


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


class TestConfigsAPI:
    @pytest.mark.asyncio
    async def test_get_configs_empty(self, mocker):
        """TC-CONFIG-001a: 获取空配置列表"""
        mocker.patch("app.api.configs.config_manager.list_configs", return_value=[])

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/configs")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["items"] == []

    @pytest.mark.asyncio
    async def test_get_configs_with_data(self, mocker, sample_config):
        """TC-CONFIG-001b: 获取配置列表（有数据）"""
        mocker.patch(
            "app.api.configs.config_manager.list_configs",
            return_value=[sample_config]
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/configs")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["items"]) == 1
        assert data["data"]["items"][0]["name"] == "TestService"

    @pytest.mark.asyncio
    async def test_get_config_by_id(self, mocker, sample_config):
        """TC-CONFIG-002: 获取配置详情"""
        mocker.patch(
            "app.api.configs.config_manager.get_config",
            return_value=sample_config
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/configs/cfg-1")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == "cfg-1"

    @pytest.mark.asyncio
    async def test_create_config(self, mocker):
        """TC-CONFIG-003: 新增配置"""
        new_config_data = {
            "name": "NewService",
            "start_command": "python start.py",
            "stop_command": "python stop.py"
        }
        mocker.patch(
            "app.api.configs.config_manager.create_config",
            return_value=ServiceConfig(id="cfg-new", **new_config_data)
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/v1/configs", json=new_config_data)

        assert response.status_code == 201
        data = response.json()
        assert data["data"]["id"] == "cfg-new"

    @pytest.mark.asyncio
    async def test_update_config(self, mocker, sample_config):
        """TC-CONFIG-004: 更新配置"""
        updated_data = {"description": "Updated description"}
        mocker.patch(
            "app.api.configs.config_manager.update_config",
            return_value=ServiceConfig(**{**sample_config.model_dump(), "description": "Updated description"})
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.put(
                "/api/v1/configs/cfg-1",
                json=updated_data
            )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["description"] == "Updated description"

    @pytest.mark.asyncio
    async def test_delete_config(self, mocker):
        """TC-CONFIG-005: 删除配置"""
        mocker.patch(
            "app.api.configs.config_manager.delete_config",
            return_value=True
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete("/api/v1/configs/cfg-1")

        assert response.status_code == 204
