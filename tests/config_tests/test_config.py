"""High-level behaviour of agentforge.config.Config.

These tests rely only on the public interface and the default YAML shipped in
`src/agentforge/setup_files`. They are intentionally isolated from the rest of
AgentForge (no model import, no Chroma, etc.) and use the `isolated_config`
fixture defined in `tests/conftest.py` which copies the setup files into a
temporary directory and resets the global singleton.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest

from agentforge.config import Config

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _collect_default_paths(root: Path) -> set[Path]:
    """Return every YAML path inside the shipped setup_files directory."""
    return {p.relative_to(root) for p in root.rglob("*.yaml")}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_defaults_are_loaded(isolated_config: Config):  # noqa: D103
    """Core sections from setup_files must be present in the loaded data."""
    cfg = isolated_config

    # Basic structure checks – we don't need exact file-to-dict mapping.
    assert "settings" in cfg.data
    for section in ("system", "models", "storage"):
        assert section in cfg.data["settings"], f"Missing settings.{section} section"

    # Ensure at least one persona and prompt exists
    assert cfg.data.get("personas"), "No personas loaded"
    assert cfg.data.get("prompts"), "No prompts loaded"


def test_environment_override_and_reset(monkeypatch, isolated_config: Config):  # noqa: D103
    # Toggle an env var that the logger reads in Config.get_model (indirectly)
    monkeypatch.setenv("AF_TEST_ENV", "yes")

    cfg1 = isolated_config
    before = cfg1.data["settings"]["system"]["debug"]["mode"]

    # Manually flip a value in the live config
    cfg1.data["settings"]["system"]["debug"]["mode"] = not before

    # Reset and ensure defaults restored
    cfg2 = Config.reset(root_path=str(cfg1.project_root))
    assert cfg2.data["settings"]["system"]["debug"]["mode"] == before


def test_find_config_utility(isolated_config: Config):  # noqa: D103
    person = isolated_config.find_config("personas", "default")
    # YAML defines "Name" with capital N
    assert person.get("Name") or person.get("name")

    with pytest.raises(FileNotFoundError):
        isolated_config.find_config("prompts", "does-not-exist") 