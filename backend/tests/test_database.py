import pytest
import json
from app.crud.server import ServerCRUD
from app.crud.service_config import ServiceConfigCRUD


class TestServerCRUD:
    @pytest.mark.asyncio
    async def test_create_server(self, test_db):
        """TC-DB-001: 创建服务器记录"""
        server = ServerCRUD.create(
            test_db,
            name="test-server",
            ip="192.168.1.100",
            user="admin",
            password="secret",
            port=22
        )
        await test_db.commit()
        await test_db.refresh(server)

        assert server.id is not None
        assert server.name == "test-server"
        assert server.ip == "192.168.1.100"
        assert server.user == "admin"
        assert server.port == 22

    @pytest.mark.asyncio
    async def test_get_all_servers(self, test_db):
        """TC-DB-002: 查询服务器列表"""
        ServerCRUD.create(test_db, name="server1", ip="192.168.1.1", user="root")
        ServerCRUD.create(test_db, name="server2", ip="192.168.1.2", user="root")
        await test_db.commit()

        servers = await ServerCRUD.get_all(test_db)
        assert len(servers) == 2

    @pytest.mark.asyncio
    async def test_get_server_by_id(self, test_db):
        """TC-DB-003: 按 ID 查询服务器"""
        created = ServerCRUD.create(
            test_db, name="test", ip="192.168.1.1", user="admin"
        )
        await test_db.commit()

        server = await ServerCRUD.get_by_id(test_db, created.id)
        assert server is not None
        assert server.name == "test"

    @pytest.mark.asyncio
    async def test_update_server(self, test_db):
        """TC-DB-004: 更新服务器信息"""
        created = ServerCRUD.create(
            test_db, name="test", ip="192.168.1.1", user="admin"
        )
        await test_db.commit()

        updated = await ServerCRUD.update(test_db, created.id, name="updated", ip="192.168.1.2")
        await test_db.commit()

        assert updated.name == "updated"
        assert updated.ip == "192.168.1.2"

    @pytest.mark.asyncio
    async def test_delete_server(self, test_db):
        """TC-DB-005: 删除服务器记录"""
        created = ServerCRUD.create(
            test_db, name="test", ip="192.168.1.1", user="admin"
        )
        await test_db.commit()

        result = await ServerCRUD.delete(test_db, created.id)
        await test_db.commit()

        assert result is True
        server = await ServerCRUD.get_by_id(test_db, created.id)
        assert server is None


class TestServiceConfigCRUD:
    @pytest.mark.asyncio
    async def test_create_config(self, test_db):
        """TC-DB-006: 创建配置记录"""
        config = ServiceConfigCRUD.create(
            test_db,
            name="test-service",
            start_command="python start.py",
            stop_command="python stop.py",
            description="Test service",
            image_depend=["python:3.10"],
            if_gpu=True,
            allow_server=["server1", "server2"]
        )
        await test_db.commit()
        await test_db.refresh(config)

        assert config.id is not None
        assert config.name == "test-service"
        assert config.start_command == "python start.py"
        assert config.if_gpu is True

    @pytest.mark.asyncio
    async def test_get_all_configs(self, test_db):
        """TC-DB-007: 查询配置列表"""
        ServiceConfigCRUD.create(
            test_db, name="config1", start_command="start1", stop_command="stop1"
        )
        ServiceConfigCRUD.create(
            test_db, name="config2", start_command="start2", stop_command="stop2"
        )
        await test_db.commit()

        configs = await ServiceConfigCRUD.get_all(test_db)
        assert len(configs) == 2

    @pytest.mark.asyncio
    async def test_update_config(self, test_db):
        """TC-DB-008: 更新配置"""
        created = ServiceConfigCRUD.create(
            test_db,
            name="test",
            start_command="start",
            stop_command="stop",
            if_gpu=False
        )
        await test_db.commit()

        updated = await ServiceConfigCRUD.update(
            test_db, created.id, description="updated desc", if_gpu=True
        )
        await test_db.commit()

        assert updated.description == "updated desc"
        assert updated.if_gpu is True

    @pytest.mark.asyncio
    async def test_delete_config(self, test_db):
        """TC-DB-009: 删除配置"""
        created = ServiceConfigCRUD.create(
            test_db, name="test", start_command="start", stop_command="stop"
        )
        await test_db.commit()

        result = await ServiceConfigCRUD.delete(test_db, created.id)
        await test_db.commit()

        assert result is True
        config = await ServiceConfigCRUD.get_by_id(test_db, created.id)
        assert config is None

    @pytest.mark.asyncio
    async def test_json_field_serialization(self, test_db):
        """TC-DB-010: JSON 字段序列化"""
        config = ServiceConfigCRUD.create(
            test_db,
            name="test-service",
            start_command="start",
            stop_command="stop",
            image_depend=["python:3.10", "cuda:11.8"],
            allow_server=["server1", "server2"]
        )
        await test_db.commit()
        await test_db.refresh(config)

        parsed = ServiceConfigCRUD.parse_json_fields(config)
        assert parsed["image_depend"] == ["python:3.10", "cuda:11.8"]
        assert parsed["allow_server"] == ["server1", "server2"]
