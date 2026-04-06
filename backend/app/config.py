import os
import yaml
from pathlib import Path
from functools import lru_cache
from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False


class SSHConfig(BaseModel):
    connection_timeout: int = 10
    command_timeout: int = 60


class StatusConfig(BaseModel):
    poll_interval: int = 15


class DatabaseConfig(BaseModel):
    url: str = "sqlite+aiosqlite:///./lsp.db"


class Settings(BaseSettings):
    app: AppConfig = AppConfig()
    ssh: SSHConfig = SSHConfig()
    status: StatusConfig = StatusConfig()
    database: DatabaseConfig = DatabaseConfig()
    servers_file: str = "server_info.json"
    configs_file: str = "config_info.json"

    model_config = SettingsConfigDict(
        env_prefix="LSP_",
        env_nested_delimiter="_"
    )


def load_config(config_path: str) -> Settings:
    """Load configuration from YAML file"""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(path, "r") as f:
        config_data = yaml.safe_load(f)

    settings = Settings()
    if config_data:
        if "app" in config_data:
            settings.app = AppConfig(**config_data["app"])
        if "ssh" in config_data:
            settings.ssh = SSHConfig(**config_data["ssh"])
        if "status" in config_data:
            settings.status = StatusConfig(**config_data["status"])
        if "servers_file" in config_data:
            settings.servers_file = config_data["servers_file"]
        if "configs_file" in config_data:
            settings.configs_file = config_data["configs_file"]

    return settings


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
