import pytest
import json
import os
from pathlib import Path
from app.models.server import Server
from app.services.ssh_executor import SSHExecutor


def get_test_server():
    """从 server_info.json 获取测试服务器"""
    possible_paths = [
        Path(__file__).parent.parent.parent / "server_info.json",
        Path(__file__).parent.parent.parent.parent / "server_info.json",
        Path("server_info.json"),
        Path("/home/mozinodey/PycharmProjects/LocalServerPilot/server_info.json"),
    ]

    server_info_path = None
    for path in possible_paths:
        if path.exists():
            server_info_path = path
            break

    if not server_info_path:
        pytest.skip("server_info.json not found")

    with open(server_info_path, "r") as f:
        servers = json.load(f)

    if not servers:
        pytest.skip("No servers in server_info.json")

    s = servers[0]
    return Server(
        id=f"test-{s['name']}",
        name=s["name"],
        ip=s["ip"],
        user=s["user"],
        password=s.get("password"),
        port=s.get("port", 22)
    )


@pytest.fixture
def real_server():
    """获取真实服务器用于集成测试"""
    return get_test_server()


class TestSSHExecutorIntegration:
    """SSH 执行器集成测试 - 需要真实 SSH 连接"""

    @pytest.mark.asyncio
    async def test_execute_echo_command(self, real_server):
        """集成测试：执行 echo 命令"""
        if not real_server.password:
            pytest.skip("No password available")

        executor = SSHExecutor(real_server)
        try:
            result = await executor.execute("echo 'hello world'")
            assert "hello world" in result
        finally:
            executor.close()

    @pytest.mark.asyncio
    async def test_execute_date_command(self, real_server):
        """集成测试：执行 date 命令"""
        if not real_server.password:
            pytest.skip("No password available")

        executor = SSHExecutor(real_server)
        try:
            result = await executor.execute("date")
            assert len(result.strip()) > 0
        finally:
            executor.close()

    @pytest.mark.asyncio
    async def test_gpu_status_command(self, real_server):
        """集成测试：获取 GPU 状态"""
        if not real_server.password:
            pytest.skip("No password available")

        executor = SSHExecutor(real_server)
        try:
            gpu_cmd = "nvidia-smi --query-gpu=name,utilization.gpu,memory.total,memory.used,temperature.gpu --format=csv,noheader"
            result = await executor.execute(gpu_cmd)
            lines = result.strip().split("\n")
            assert len(lines) > 0
            for line in lines:
                parts = [p.strip() for p in line.split(",")]
                assert len(parts) == 5
        finally:
            executor.close()

    @pytest.mark.asyncio
    async def test_docker_ps_command(self, real_server):
        """集成测试：获取 Docker 容器状态"""
        if not real_server.password:
            pytest.skip("No password available")

        executor = SSHExecutor(real_server)
        try:
            docker_cmd = 'docker ps --format "{{.Names}} | {{.Image}} | {{.Status}}"'
            result = await executor.execute(docker_cmd)
            lines = result.strip().split("\n")
            for line in lines:
                if line.strip():
                    parts = [p.strip() for p in line.split("|")]
                    assert len(parts) == 3
        finally:
            executor.close()

    @pytest.mark.asyncio
    async def test_connection_test(self, real_server):
        """集成测试：连接测试"""
        if not real_server.password:
            pytest.skip("No password available")

        executor = SSHExecutor(real_server)
        try:
            result = await executor.test_connection()
            assert result is True
        finally:
            executor.close()

    @pytest.mark.asyncio
    async def test_invalid_command(self, real_server):
        """集成测试：无效命令返回错误"""
        if not real_server.password:
            pytest.skip("No password available")

        executor = SSHExecutor(real_server)
        try:
            result = await executor.execute("invalid_command_xyz")
            assert "ERROR" in result or "not found" in result.lower()
        finally:
            executor.close()


class TestGPUStatusParsingIntegration:
    """GPU 状态解析集成测试"""

    def test_parse_real_gpu_output(self):
        """解析真实 GPU 输出"""
        raw_output = "NVIDIA GeForce RTX 3090, 45 %, 24576 MiB, 16384 MiB, 65 C\n"
        gpu_info = SSHExecutor.parse_gpu_info(raw_output)

        assert gpu_info.gpu_name == "NVIDIA GeForce RTX 3090"
        assert gpu_info.gpu_usage == "45 %"
        assert gpu_info.memory_total == "24576 MiB"
        assert gpu_info.memory_used == "16384 MiB"
        assert gpu_info.temperature == "65 C"

    def test_parse_real_docker_output(self):
        """解析真实 Docker 输出"""
        raw_output = "chat_server_1 | registry.example.com/chat:v1 | Up 2 hours"
        container_info = SSHExecutor.parse_container_info(raw_output)

        assert container_info.name == "chat_server_1"
        assert container_info.image == "registry.example.com/chat:v1"
        assert container_info.status == "Up 2 hours"
