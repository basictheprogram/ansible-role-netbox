"""Shared test constants for the ansible-role-netbox_docker Molecule scenario."""

from __future__ import annotations

DEPLOY_DIR: str = "/opt/netbox"
ENV_DIR: str = f"{DEPLOY_DIR}/env"
CONFIG_DIR: str = f"{DEPLOY_DIR}/configuration"

# Static config files copied from files/configuration/.
CONFIG_FILES: list[str] = [
    "configuration.py",
    "extra.py",
    "logging.py",
    "plugins.py",
]

# (filename, expected octal mode) for env files templated into ENV_DIR.
ENV_FILES: list[tuple[str, str]] = [
    ("netbox.env", "0640"),
    ("postgres.env", "0640"),
    ("redis.env", "0640"),
    ("redis-cache.env", "0640"),
]

# Compose files deployed to DEPLOY_DIR.
COMPOSE_FILES: list[str] = [
    "docker-compose.yml",
    "docker-compose.overlay.yml",
]
