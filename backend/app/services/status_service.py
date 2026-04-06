from datetime import datetime
from typing import List
from app.models.server import Server
from app.models.status import ServerStatus, GPUInfo, ContainerInfo
from app.services.ssh_executor import SSHExecutor, SSHError


class StatusService:
    GPU_COMMAND = (
        "nvidia-smi --query-gpu=name,utilization.gpu,memory.total,memory.used,temperature.gpu "
        "--format=csv,noheader"
    )

    CONTAINER_COMMAND = 'docker ps --format "{{.Names}} | {{.Image}} | {{.Status}}"'

    async def get_gpu_status(self, server: Server) -> List[GPUInfo]:
        try:
            executor = SSHExecutor(server)
            output = await executor.execute(self.GPU_COMMAND)
            executor.close()

            gpu_list = []
            for line in output.strip().split("\n"):
                if line:
                    gpu_list.append(SSHExecutor.parse_gpu_info(line))
            return gpu_list
        except SSHError:
            return []

    async def get_container_status(self, server: Server) -> List[ContainerInfo]:
        try:
            executor = SSHExecutor(server)
            output = await executor.execute(self.CONTAINER_COMMAND)
            executor.close()

            container_list = []
            for line in output.strip().split("\n"):
                if line:
                    container_list.append(SSHExecutor.parse_container_info(line))
            return container_list
        except SSHError:
            return []

    async def get_server_status(self, server: Server) -> ServerStatus:
        gpu_info = await self.get_gpu_status(server)
        container_info = await self.get_container_status(server)

        return ServerStatus(
            server_id=server.id,
            gpu_info=gpu_info,
            container_info=container_info,
            checked_at=datetime.now()
        )


status_service = StatusService()
