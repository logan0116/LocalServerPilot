import pytest
import os
import tempfile
from pathlib import Path
from app.config import Settings, load_config, get_settings


class TestConfigLoading:
    def test_default_config(self):
        """TC-CONF-001: 加载有效配置（默认）"""
        settings = Settings()
        assert settings.app.host == "0.0.0.0"
        assert settings.app.port == 8000
        assert settings.status.poll_interval == 15

    def test_config_from_yaml(self, tmp_path):
        """TC-CONF-001b: 从 YAML 加载配置"""
        config_content = """
app:
  host: "127.0.0.1"
  port: 9000
  debug: true

ssh:
  connection_timeout: 30
  command_timeout: 120

status:
  poll_interval: 30

servers_file: "servers.json"
configs_file: "configs.json"
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)

        settings = load_config(config_file)
        assert settings.app.host == "127.0.0.1"
        assert settings.app.port == 9000
        assert settings.app.debug is True
        assert settings.ssh.connection_timeout == 30
        assert settings.status.poll_interval == 30

    def test_env_var_override(self, monkeypatch):
        """TC-CONF-002: 环境变量覆盖配置"""
        monkeypatch.setenv("LSP_APP_HOST", "192.168.1.1")
        monkeypatch.setenv("LSP_APP_PORT", "8888")

        settings = Settings()
        assert settings.app.host == "192.168.1.1"
        assert settings.app.port == 8888

    def test_missing_config_file(self):
        """TC-CONF-003: 缺少配置文件"""
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/path/config.yaml")

    def test_invalid_yaml_format(self, tmp_path):
        """TC-CONF-003b: 无效 YAML 格式"""
        config_file = tmp_path / "invalid.yaml"
        config_file.write_text("invalid: yaml: content: [}")

        with pytest.raises(Exception):  # YAML解析异常
            load_config(config_file)


class TestSettingsValidation:
    def test_ssh_timeout_defaults(self):
        """SSH 超时默认值"""
        settings = Settings()
        assert settings.ssh.connection_timeout == 10
        assert settings.ssh.command_timeout == 60

    def test_poll_interval_minimum(self):
        """轮询间隔最小值"""
        settings = Settings()
        assert settings.status.poll_interval >= 1

    def test_get_settings_singleton(self):
        """单例模式测试"""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2
