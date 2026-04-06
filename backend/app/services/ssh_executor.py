import asyncio
from typing import Optional
import paramiko
from paramiko import SSHClient, AutoAddPolicy
from app.models.server import Server
from app.models.status import GPUInfo, ContainerInfo


class SSHError(Exception):
    """SSH operation error"""
    pass


class SSHExecutor:
    def __init__(self, server: Server):
        self.server = server
        self.client: Optional[SSHClient] = None
        self._connect()

    def _connect(self):
        try:
            self.client = SSHClient()
            self.client.set_missing_host_key_policy(AutoAddPolicy())
            if self.server.private_key:
                self.client.connect(
                    hostname=self.server.ip,
                    port=self.server.port,
                    username=self.server.user,
                    key_filename=self.server.private_key,
                    timeout=10
                )
            else:
                self.client.connect(
                    hostname=self.server.ip,
                    port=self.server.port,
                    username=self.server.user,
                    password=self.server.password,
                    timeout=10
                )
        except Exception as e:
            raise SSHError(f"Failed to connect to {self.server.ip}: {str(e)}")

    async def execute(self, command: str, timeout: int = 60) -> str:
        if not self.client:
            raise SSHError("Not connected")

        try:
            stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
            stdout_lines = stdout.readlines()
            stderr_lines = stderr.readlines()

            if stderr_lines:
                return f"ERROR: {''.join(stderr_lines)}"
            return ''.join(stdout_lines)
        except Exception as e:
            raise SSHError(f"Command execution failed: {str(e)}")

    async def test_connection(self) -> bool:
        try:
            if not self.client:
                self._connect()
            stdin, stdout, stderr = self.client.exec_command("echo test", timeout=5)
            result = stdout.readline()
            return "test" in result
        except Exception:
            return False

    def close(self):
        if self.client:
            self.client.close()
            self.client = None

    @staticmethod
    def parse_gpu_info(line: str) -> GPUInfo:
        parts = [p.strip() for p in line.split(",")]
        return GPUInfo(
            gpu_name=parts[0],
            gpu_usage=parts[1],
            memory_total=parts[2],
            memory_used=parts[3],
            temperature=parts[4]
        )

    @staticmethod
    def parse_container_info(line: str) -> ContainerInfo:
        parts = [p.strip() for p in line.split("|")]
        return ContainerInfo(
            name=parts[0],
            image=parts[1],
            status=parts[2]
        )
