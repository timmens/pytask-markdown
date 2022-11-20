"""Configuration file for pytest."""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner


TEST_RESOURCES = Path(__file__).parent / "resources"

needs_marp = pytest.mark.xfailif(
    shutil.which("marp") is None, reason="marp needs to be installed."
)
needs_quarto = pytest.mark.xfailif(
    shutil.which("quarto") is None, reason="quarto needs to be installed."
)


@pytest.fixture()
def runner():
    return CliRunner()
