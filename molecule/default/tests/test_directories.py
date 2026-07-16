"""Deploy directory layout tests for the ansible-role-netbox_docker Molecule scenario."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._data import CONFIG_DIR, DEPLOY_DIR, ENV_DIR

if TYPE_CHECKING:
    from testinfra.host import Host


def test_deploy_dir_exists(host: Host) -> None:
    d = host.file(DEPLOY_DIR)
    assert d.exists
    assert d.is_directory
    assert d.mode == 0o755


def test_env_dir_exists(host: Host) -> None:
    d = host.file(ENV_DIR)
    assert d.exists
    assert d.is_directory
    assert d.mode == 0o750


def test_config_dir_exists(host: Host) -> None:
    d = host.file(CONFIG_DIR)
    assert d.exists
    assert d.is_directory
    assert d.mode == 0o755
