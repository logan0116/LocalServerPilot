import json
import uuid
from typing import List, Optional
from pathlib import Path
from app.models.config import ServiceConfig, ServiceConfigCreate, ServiceConfigUpdate
from app.config import get_settings


class ConfigManager:
    def __init__(self):
        self.settings = get_settings()
        self._configs: dict[str, ServiceConfig] = {}
        self._load_configs()

    def _load_configs(self):
        configs_file = Path(self.settings.configs_file)
        if configs_file.exists():
            with open(configs_file, "r") as f:
                data = json.load(f)
                for item in data:
                    if "id" not in item:
                        item["id"] = str(uuid.uuid5(uuid.NAMESPACE_DNS, item["name"]))
                    config = ServiceConfig(**item)
                    self._configs[config.id] = config

    def _save_configs(self):
        configs_file = Path(self.settings.configs_file)
        data = [config.model_dump() for config in self._configs.values()]
        with open(configs_file, "w") as f:
            json.dump(data, f, indent=2)

    def list_configs(self) -> List[ServiceConfig]:
        return list(self._configs.values())

    def get_config(self, config_id: str) -> Optional[ServiceConfig]:
        return self._configs.get(config_id)

    def create_config(self, config_data: ServiceConfigCreate) -> ServiceConfig:
        import uuid
        config = ServiceConfig(
            id=str(uuid.uuid4()),
            name=config_data.name,
            description=config_data.description,
            image_depend=config_data.image_depend,
            if_gpu=config_data.if_gpu,
            allow_server=config_data.allow_server,
            start_command=config_data.start_command,
            stop_command=config_data.stop_command
        )
        self._configs[config.id] = config
        self._save_configs()
        return config

    def update_config(self, config_id: str, update_data: ServiceConfigUpdate) -> Optional[ServiceConfig]:
        config = self._configs.get(config_id)
        if not config:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(config, key, value)

        self._save_configs()
        return config

    def delete_config(self, config_id: str) -> bool:
        if config_id in self._configs:
            del self._configs[config_id]
            self._save_configs()
            return True
        return False


config_manager = ConfigManager()
