from typing import List, Optional
from app.models.server import Server
from app.models.config import ServiceConfig
from app.services.ssh_executor import SSHExecutor, SSHError


class ServiceOperationError(Exception):
    """Service operation error"""
    pass


async def execute_service_command(
    server: Server,
    command: str
) -> dict:
    try:
        executor = SSHExecutor(server)
        output = await executor.execute(command)
        executor.close()
        return {"success": True, "output": output}
    except SSHError as e:
        raise ServiceOperationError(str(e))


async def start_service(server: Server, config: ServiceConfig) -> dict:
    return await execute_service_command(server, config.start_command)


async def stop_service(server: Server, config: ServiceConfig) -> dict:
    return await execute_service_command(server, config.stop_command)


async def check_service_status(server: Server, config: ServiceConfig) -> dict:
    try:
        executor = SSHExecutor(server)
        command = f"ps aux | grep {config.name}"
        output = await executor.execute(command)
        executor.close()

        running = config.start_command.split()[0] in output
        return {"running": running, "output": output}
    except SSHError as e:
        raise ServiceOperationError(str(e))
