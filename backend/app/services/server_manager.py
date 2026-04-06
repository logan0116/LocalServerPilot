import json
import uuid
from typing import List, Optional
from pathlib import Path
from app.models.server import Server, ServerCreate, ServerUpdate
from app.config import get_settings


class ServerManager:
    def __init__(self):
        self.settings = get_settings()
        self._servers: dict[str, Server] = {}
        self._load_servers()

    def _load_servers(self):
        servers_file = Path(self.settings.servers_file)
        if servers_file.exists():
            with open(servers_file, "r") as f:
                data = json.load(f)
                for item in data:
                    if "id" not in item:
                        item["id"] = str(uuid.uuid5(uuid.NAMESPACE_DNS, item["name"]))
                    server = Server(**item)
                    self._servers[server.id] = server

    def _save_servers(self):
        servers_file = Path(self.settings.servers_file)
        data = [server.model_dump() for server in self._servers.values()]
        with open(servers_file, "w") as f:
            json.dump(data, f, indent=2)

    def list_servers(self) -> List[Server]:
        return list(self._servers.values())

    def get_server(self, server_id: str) -> Optional[Server]:
        return self._servers.get(server_id)

    def create_server(self, server_data: ServerCreate) -> Server:
        import uuid
        server = Server(
            id=str(uuid.uuid4()),
            name=server_data.name,
            ip=server_data.ip,
            user=server_data.user,
            password=server_data.password,
            private_key=server_data.private_key,
            port=server_data.port
        )
        self._servers[server.id] = server
        self._save_servers()
        return server

    def update_server(self, server_id: str, update_data: ServerUpdate) -> Optional[Server]:
        server = self._servers.get(server_id)
        if not server:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(server, key, value)

        self._save_servers()
        return server

    def delete_server(self, server_id: str) -> bool:
        if server_id in self._servers:
            del self._servers[server_id]
            self._save_servers()
            return True
        return False


server_manager = ServerManager()
