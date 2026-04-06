#!/usr/bin/env python3
import json
import uuid
from pathlib import Path


def generate_id(name: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, name))


def main():
    project_root = Path(__file__).parent
    server_json = project_root / "server_info.json"
    config_json = project_root / "config_info.json"

    print("Reading JSON files...")
    with open(server_json, "r", encoding="utf-8") as f:
        servers_data = json.load(f)
    with open(config_json, "r", encoding="utf-8") as f:
        configs_data = json.load(f)

    print(f"Found {len(servers_data)} servers and {len(configs_data)} configs")

    modified_servers = False
    for server in servers_data:
        if "id" not in server:
            server["id"] = generate_id(server["name"])
            modified_servers = True
            print(f"  Added id to server: {server['name']}")

    modified_configs = False
    for config in configs_data:
        if "id" not in config:
            config["id"] = generate_id(config["name"])
            modified_configs = True
            print(f"  Added id to config: {config['name']}")

    if modified_servers:
        with open(server_json, "w", encoding="utf-8") as f:
            json.dump(servers_data, f, indent=2, ensure_ascii=False)
        print(f"\nUpdated {server_json}")

    if modified_configs:
        with open(config_json, "w", encoding="utf-8") as f:
            json.dump(configs_data, f, indent=2, ensure_ascii=False)
        print(f"\nUpdated {config_json}")

    if not modified_servers and not modified_configs:
        print("\nAll entries already have ids, no changes needed.")

    print("\nDone!")


if __name__ == "__main__":
    main()
