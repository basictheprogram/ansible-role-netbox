"""Env-file tests for the ansible-role-netbox_docker Molecule scenario.

Parametrized existence/permission checks over ENV_FILES. Content
assertions get their own single-purpose test function per file/setting
pair -- never combine an existence check and a content check in the same
test function.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ._data import DEPLOY_DIR, ENV_DIR, ENV_FILES

if TYPE_CHECKING:
    from testinfra.host import Host


@pytest.mark.parametrize("filename", [name for name, _ in ENV_FILES])
def test_env_file_exists(host: Host, filename: str) -> None:
    f = host.file(f"{ENV_DIR}/{filename}")
    assert f.exists
    assert f.is_file


@pytest.mark.parametrize(("filename", "expected_mode"), ENV_FILES)
def test_env_file_mode(host: Host, filename: str, expected_mode: str) -> None:
    f = host.file(f"{ENV_DIR}/{filename}")
    assert f.mode == int(expected_mode, 8)


def test_project_env_file_exists(host: Host) -> None:
    f = host.file(f"{DEPLOY_DIR}/.env")
    assert f.exists
    assert f.is_file


def test_project_env_contains_version(host: Host) -> None:
    f = host.file(f"{DEPLOY_DIR}/.env")
    assert f.contains("^VERSION=")


def test_postgres_env_contains_db_name(host: Host) -> None:
    f = host.file(f"{ENV_DIR}/postgres.env")
    assert f.contains("^POSTGRES_DB=netbox$")


def test_netbox_env_contains_db_host(host: Host) -> None:
    f = host.file(f"{ENV_DIR}/netbox.env")
    assert f.contains("^DB_HOST=postgres$")
