"""Shared fixtures for methodology self-tests."""
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def repo_root() -> Path:
    """Absolute path to the AI SDLC repo root."""
    return REPO_ROOT


def read_file(relative_path: str) -> str:
    """Read a file relative to repo root as text."""
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")
