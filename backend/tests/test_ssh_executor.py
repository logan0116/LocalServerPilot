import pytest
from unittest.mock import MagicMock, patch
from app.services.ssh_executor import SSHExecutor, SSHError
from app.models.server import Server


class TestSSHExecutor:
    @pytest.fixture
    def server(self):
        return Server(
            id="srv-1",
            name="Test Server",
            ip="192.168.1.100",
            user="admin",
            password="secret",
            port=22
        )

    @pytest.mark.asyncio
    async def test_execute_command_success(self, server):
        """TC-SSH-001: 成功执行命令"""
        mock_client = MagicMock()
        mock_stdout = MagicMock()
        mock_stdout.readlines.return_value = ["output line 1", "output line 2"]
        mock_stderr = MagicMock()
        mock_stderr.readlines.return_value = []
        mock_client.exec_command.return_value = (None, mock_stdout, mock_stderr)

        with patch("app.services.ssh_executor.SSHClient") as mock_ssh_class:
            mock_ssh_class.return_value = mock_client
            executor = SSHExecutor(server)
            result = await executor.execute("ls -la")

            assert "output line 1" in result
            mock_client.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_command_failure(self, server):
        """TC-SSH-001b: 命令执行失败"""
        with patch("app.services.ssh_executor.SSHClient") as mock_ssh_class:
            mock_client = MagicMock()
            mock_client.exec_command.side_effect = Exception("Command failed")
            mock_ssh_class.return_value = mock_client

            executor = SSHExecutor(server)
            with pytest.raises(SSHError):
                await executor.execute("invalid command")

    @pytest.mark.asyncio
    async def test_connection_failure(self, server):
        """TC-SSH-002: 连接失败"""
        with patch("app.services.ssh_executor.SSHClient") as mock_ssh_class:
            mock_client = MagicMock()
            mock_client.connect.side_effect = Exception("Connection refused")
            mock_ssh_class.return_value = mock_client

            with pytest.raises(SSHError):
                SSHExecutor(server)

    @pytest.mark.asyncio
    async def test_command_timeout(self, server):
        """TC-SSH-003: 命令执行超时"""
        with patch("app.services.ssh_executor.SSHClient") as mock_ssh_class:
            mock_client = MagicMock()
            mock_client.exec_command.side_effect = TimeoutError("Command timed out")
            mock_ssh_class.return_value = mock_client

            executor = SSHExecutor(server)
            with pytest.raises(SSHError):
                await executor.execute("sleep 100")


class TestGPUStatusParsing:
    def test_parse_gpu_info(self):
        """TC-SSH-004: GPU 状态解析"""
        raw_output = "NVIDIA GeForce RTX 3090, 45 %, 24576 MiB, 16384 MiB, 65 C\n"
        gpu_info = SSHExecutor.parse_gpu_info(raw_output)

        assert gpu_info.gpu_name == "NVIDIA GeForce RTX 3090"
        assert gpu_info.gpu_usage == "45 %"
        assert gpu_info.memory_total == "24576 MiB"
        assert gpu_info.memory_used == "16384 MiB"
        assert gpu_info.temperature == "65 C"

    def test_parse_container_info(self):
        """TC-SSH-004b: 容器状态解析"""
        raw_output = "model-server-1 | registry.example.com/model:v1 | Up 2 hours"
        container_info = SSHExecutor.parse_container_info(raw_output)

        assert container_info.name == "model-server-1"
        assert container_info.image == "registry.example.com/model:v1"
        assert container_info.status == "Up 2 hours"
