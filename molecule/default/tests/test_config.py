"""Config-file tests for the ansible-role-netbox_docker Molecule scenario.

Parametrized existence/permission checks over CONFIG_FILES. Content
assertions get their own single-purpose test function per file/setting
pair -- never combine an existence check and a content check in the same
test function.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ._data import CONFIG_DIR, CONFIG_FILES

if TYPE_CHECKING:
    from testinfra.host import Host


@pytest.mark.parametrize("filename", CONFIG_FILES)
def test_config_file_exists(host: Host, filename: str) -> None:
    f = host.file(f"{CONFIG_DIR}/{filename}")
    assert f.exists
    assert f.is_file


@pytest.mark.parametrize("filename", CONFIG_FILES)
def test_config_file_mode(host: Host, filename: str) -> None:
    f = host.file(f"{CONFIG_DIR}/{filename}")
    assert f.mode == 0o644
