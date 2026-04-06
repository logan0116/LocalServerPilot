import pytest
from pydantic import ValidationError
from app.models.server import Server, ServerCreate, ServerUpdate
from app.models.config import ServiceConfig, ServiceConfigCreate, ServiceConfigUpdate
from app.models.status import GPUInfo, ContainerInfo, ServerStatus


class TestServerModel:
    def test_server_required_fields(self):
        """TC-MODEL-001: Server 模型必填字段验证"""
        with pytest.raises(ValidationError) as exc_info:
            Server()
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("name",) for e in errors)
        assert any(e["loc"] == ("ip",) for e in errors)
        assert any(e["loc"] == ("user",) for e in errors)

    def test_server_valid_creation(self):
        """TC-MODEL-001b: Server 模型有效创建"""
        server = Server(
            id="test-1",
            name="Test Server",
            ip="192.168.1.100",
            user="admin",
            password="secret"
        )
        assert server.name == "Test Server"
        assert server.ip == "192.168.1.100"
        assert server.user == "admin"
        assert server.password == "secret"
        assert server.port == 22  # default

    def test_server_optional_fields(self):
        """TC-MODEL-002: Server 模型可选字段"""
        server = Server(
            id="test-1",
            name="Test Server",
            ip="192.168.1.100",
            user="admin",
            private_key="/path/to/key"
        )
        assert server.password is None
        assert server.private_key == "/path/to/key"

    def test_server_create_defaults(self):
        """TC-MODEL-002b: ServerCreate 模型默认值"""
        data = {"name": "Test", "ip": "192.168.1.1", "user": "root"}
        server = ServerCreate(**data)
        assert server.port == 22

    def test_server_with_custom_port(self):
        """Server 模型自定义端口"""
        server = Server(
            id="test-1",
            name="Test",
            ip="192.168.1.100",
            user="admin",
            port=2222
        )
        assert server.port == 2222


class TestServiceConfigModel:
    def test_config_required_fields(self):
        """TC-MODEL-003a: ServiceConfig 必填字段验证"""
        with pytest.raises(ValidationError) as exc_info:
            ServiceConfig()
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("name",) for e in errors)
        assert any(e["loc"] == ("start_command",) for e in errors)

    def test_config_valid_creation(self):
        """TC-MODEL-003b: ServiceConfig 有效创建"""
        config = ServiceConfig(
            id="cfg-1",
            name="TestService",
            description="A test service",
            image_depend=["python:3.10", "cuda:11.8"],
            if_gpu=True,
            allow_server=["server1", "server2"],
            start_command="python start.py",
            stop_command="python stop.py"
        )
        assert config.name == "TestService"
        assert config.if_gpu is True
        assert len(config.image_depend) == 2

    def test_config_create_without_optional(self):
        """ServiceConfig 可选字段可为空"""
        config = ServiceConfigCreate(
            name="MinimalService",
            start_command="python start.py",
            stop_command="python stop.py"
        )
        assert config.description is None
        assert config.if_gpu is False


class TestGPUInfoModel:
    def test_gpu_info_parsing(self):
        """TC-MODEL-004: GPUInfo 数据解析"""
        gpu = GPUInfo(
            gpu_name="NVIDIA GeForce RTX 3090",
            gpu_usage="45%",
            memory_total="24576MiB",
            memory_used="16384MiB",
            temperature="65C"
        )
        assert "3090" in gpu.gpu_name
        assert gpu.gpu_usage == "45%"
        assert gpu.temperature == "65C"


class TestContainerInfoModel:
    def test_container_info_parsing(self):
        """ContainerInfo 数据解析"""
        container = ContainerInfo(
            name="model-server-1",
            image="registry.example.com/model:v1",
            status="Up 2 hours"
        )
        assert container.name == "model-server-1"
        assert "Up" in container.status


class TestServerStatusModel:
    def test_server_status_complete(self):
        """ServerStatus 完整状态"""
        gpu = GPUInfo(
            gpu_name="RTX 3090",
            gpu_usage="45%",
            memory_total="24576MiB",
            memory_used="16384MiB",
            temperature="65C"
        )
        container = ContainerInfo(
            name="test-container",
            image="test:latest",
            status="Up"
        )
        status = ServerStatus(
            server_id="srv-1",
            gpu_info=[gpu],
            container_info=[container]
        )
        assert len(status.gpu_info) == 1
        assert len(status.container_info) == 1
        assert status.server_id == "srv-1"
