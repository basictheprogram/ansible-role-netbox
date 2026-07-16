"""Compose-file tests for the ansible-role-netbox_docker Molecule scenario."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ._data import COMPOSE_FILES, DEPLOY_DIR

if TYPE_CHECKING:
    from testinfra.host import Host


@pytest.mark.parametrize("filename", COMPOSE_FILES)
def test_compose_file_exists(host: Host, filename: str) -> None:
    f = host.file(f"{DEPLOY_DIR}/{filename}")
    assert f.exists
    assert f.is_file


def test_overlay_declares_traefik_network(host: Host) -> None:
    f = host.file(f"{DEPLOY_DIR}/docker-compose.overlay.yml")
    assert f.contains("traefik_proxy")
