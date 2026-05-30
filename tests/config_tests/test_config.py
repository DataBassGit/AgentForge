"""High-level behaviour of agentforge.config.Config.

These tests rely only on the public interface and the default YAML shipped in
`src/agentforge/setup_files`. They are intentionally isolated from the rest of
AgentForge (no model import, no Chroma, etc.) and use the `isolated_config`
fixture defined in `tests/conftest.py` which copies the setup files into a
temporary directory and resets the global singleton.
"""

from __future__ import annotations

from pathlib import Path

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


def test_session5_provider_defaults_are_current_and_codex_is_configurable(isolated_config: Config):
    """Session 5 setup defaults should keep provider params and Codex config current."""
    models = isolated_config.data["settings"]["models"]["model_library"]

    openai_gpt = models["openai_api"]["GPT"]
    assert "max_tokens" not in openai_gpt["params"]
    assert openai_gpt["params"]["max_completion_tokens"] == 10000
    assert openai_gpt["models"]["gpt55_model"]["identifier"] == "gpt-5.5"
    assert openai_gpt["models"]["gpt55_pro_model"]["identifier"] == "gpt-5.5-pro"
    assert openai_gpt["models"]["gpt4o_model"]["params"]["max_completion_tokens"] == 15000
    for deprecated_model in ("gpt4_model", "gpt4_turbo_model", "gpt35_model"):
        assert deprecated_model not in openai_gpt["models"]

    o_series_models = models["openai_api"]["O1Series"]["models"]
    assert o_series_models["o3"]["identifier"] == "o3"
    for deprecated_model in ("o1", "o1_preview", "o1_mini", "o4-mini", "o3-mini"):
        assert deprecated_model not in o_series_models

    assert "Codex" in models["openai_api"]
    codex_models = models["openai_api"]["Codex"]["models"]
    assert codex_models["codex_gpt55"]["identifier"] == "gpt-5.5"
    assert codex_models["codex_gpt53_codex"]["identifier"] == "gpt-5.3-codex"
    for deprecated_model in (
        "codex_gpt52_codex",
        "codex_gpt52",
        "codex_gpt51_codex_max",
        "codex_gpt51_codex",
        "codex_gpt51_codex_mini",
    ):
        assert deprecated_model not in codex_models

    anthropic_models = models["anthropic_api"]["Claude"]["models"]
    assert anthropic_models["claude_opus_4_8"]["identifier"] == "claude-opus-4-8"
    assert anthropic_models["claude_opus_4_7"]["identifier"] == "claude-opus-4-7"
    assert anthropic_models["claude_opus_4_6"]["identifier"] == "claude-opus-4-6"
    assert anthropic_models["claude_opus_4_5"]["identifier"] == "claude-opus-4-5-20251101"
    assert anthropic_models["claude4_1opus"]["identifier"] == "claude-opus-4-1-20250805"
    assert anthropic_models["claude_sonnet_4_6"]["identifier"] == "claude-sonnet-4-6"
    assert anthropic_models["claude_sonnet_4_5"]["identifier"] == "claude-sonnet-4-5-20250929"
    assert anthropic_models["claude_haiku_4_5"]["identifier"] == "claude-haiku-4-5-20251001"
    assert models["anthropic_api"]["Claude"]["params"] == {"max_tokens": 10000}
    for deprecated_model in (
        "claude3opus",
        "claude4opus",
        "claude4sonnet",
        "claude3.7sonnet",
        "claude3.5haiku",
        "claude3.7haiku",
    ):
        assert deprecated_model not in anthropic_models

    gemini_models = models["gemini_api"]["Gemini"]["models"]
    assert gemini_models["gemini_flash"]["identifier"] == "gemini-3.5-flash"
    assert gemini_models["gemini_pro"]["identifier"] == "gemini-3.1-pro-preview"
    assert gemini_models["gemini_3_flash_preview"]["identifier"] == "gemini-3-flash-preview"
    assert gemini_models["gemini_flash_lite"]["identifier"] == "gemini-3.1-flash-lite"
    assert models["gemini_api"]["Gemini"]["params"]["temperature"] == 1.0
    assert "gemini_exp" not in gemini_models
    assert models["litellm_api"]["LiteLLM"]["models"]["gemini_flash"]["identifier"] == "gemini-3.5-flash"

    assert models["ollama_api"]["Ollama"]["params"]["num_predict"] == 10000
    assert "max_tokens" not in models["ollama_api"]["Ollama"]["params"]

    groq = models["groq_api"]["GroqAPI"]
    assert groq["params"]["max_completion_tokens"] == 10000
    assert "max_tokens" not in groq["params"]
    assert "seed" not in groq["params"]
    assert groq["models"]["llama33_70b"]["identifier"] == "llama-3.3-70b-versatile"
    assert groq["models"]["llama31_8b"]["identifier"] == "llama-3.1-8b-instant"
    assert groq["models"]["gpt_oss_120b"]["identifier"] == "openai/gpt-oss-120b"


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
    assert person is not None
    # With persona v2, Name can be in static or retrieval sections
    if "static" in person:
        assert person["static"].get("name") or person["static"].get("Name"), "Name not found in static section"
    elif "retrieval" in person:
        assert person["retrieval"].get("name") or person["retrieval"].get("Name"), "Name not found in retrieval section"
    else:
        # Legacy format check
        assert person.get("name") or person.get("Name"), "Name not found in persona"

    with pytest.raises(FileNotFoundError):
        isolated_config.find_config("prompts", "does-not-exist")


def test_config_resolve_class(isolated_config: Config):
    """Test the Config.resolve_class method for dynamic class resolution."""
    from agentforge.agent import Agent

    # Test with default class when path is empty
    cls = Config.resolve_class("", default_class=Agent, context="test default")
    assert cls == Agent

    # Test with valid class path
    cls = Config.resolve_class("agentforge.agent.Agent", context="test agent")
    assert cls == Agent

    # Test error handling for invalid format
    with pytest.raises(ValueError, match="Invalid type format"):
        Config.resolve_class("InvalidFormat", context="test invalid")

    # Test error handling for non-existent module
    with pytest.raises(ImportError, match="Module .* not found"):
        Config.resolve_class("nonexistent.module.Class", context="test nonexistent")

    # Test error handling for missing class in valid module
    with pytest.raises(ImportError, match="Class .* not found"):
        Config.resolve_class("agentforge.agent.NonExistentClass", context="test missing class")

    # Test error when no path and no default
    with pytest.raises(ValueError, match="No class path provided"):
        Config.resolve_class("", context="test no default")
