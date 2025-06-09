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
    person = isolated_config.find_config("personas", "default_assistant")
    # With persona v2, Name can be in static or retrieval sections
    if 'static' in person:
        assert person['static'].get('name') or person['static'].get('Name'), "Name not found in static section"
    elif 'retrieval' in person:
        assert person['retrieval'].get('name') or person['retrieval'].get('Name'), "Name not found in retrieval section"
    else:
        # Legacy format check
        assert person.get("name") or person.get("Name"), "Name not found in persona"

    with pytest.raises(FileNotFoundError):
        isolated_config.find_config("prompts", "does-not-exist")


def test_config_resolve_class(isolated_config: Config):
    """Test the Config.resolve_class method for dynamic class resolution."""
    from agentforge.agent import Agent
    
    # Test with default class when path is empty
    cls = Config.resolve_class('', default_class=Agent, context='test default')
    assert cls == Agent
    
    # Test with valid class path
    cls = Config.resolve_class('agentforge.agent.Agent', context='test agent')
    assert cls == Agent
    
    # Test error handling for invalid format
    with pytest.raises(ValueError, match="Invalid type format"):
        Config.resolve_class('InvalidFormat', context='test invalid')
    
    # Test error handling for non-existent module
    with pytest.raises(ImportError, match="Module .* not found"):
        Config.resolve_class('nonexistent.module.Class', context='test nonexistent')
    
    # Test error handling for missing class in valid module  
    with pytest.raises(ImportError, match="Class .* not found"):
        Config.resolve_class('agentforge.agent.NonExistentClass', context='test missing class')
    
    # Test error when no path and no default
    with pytest.raises(ValueError, match="No class path provided"):
        Config.resolve_class('', context='test no default') 