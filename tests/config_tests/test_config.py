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

from agentforge.config import Config, load_yaml_file

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


def test_hello_agent_quickstart_prompt_is_loaded(isolated_config: Config):
    """The shipped beginner prompt should support the no-credential quickstart."""
    hello_agent = isolated_config.find_config("prompts", "hello_agent")

    assert hello_agent["prompts"]["user"] == "Say hello to {user_input}.\n"
    assert hello_agent["simulated_response"] == "Hello from AgentForge debug mode."


def test_beginner_summary_cog_resources_are_loaded(isolated_config: Config):
    """The shipped beginner Cog resources should support the no-memory walkthrough."""
    beginner_cog = isolated_config.find_config("cogs", "beginner_summary_cog")["cog"]
    summary_prompt = isolated_config.find_config("prompts", "beginner_summary_agent")
    response_prompt = isolated_config.find_config("prompts", "beginner_response_agent")

    assert beginner_cog["chat_memory_enabled"] is False
    assert beginner_cog["flow"]["start"] == "summarize"
    assert beginner_cog["flow"]["transitions"]["summarize"] == "respond"
    assert beginner_cog["flow"]["transitions"]["respond"] == {"end": True}
    assert beginner_cog["agents"] == [
        {"id": "summarize", "template_file": "beginner_summary_agent"},
        {"id": "respond", "template_file": "beginner_response_agent"},
    ]

    assert "{_ctx.user_input}" in summary_prompt["prompts"]["user"]
    assert summary_prompt["simulated_response"] == (
        "The user wants a short, friendly explanation of what AgentForge can do."
    )
    assert "{_ctx.user_input}" in response_prompt["prompts"]["user"]
    assert "{_state.summarize}" in response_prompt["prompts"]["user"]
    assert response_prompt["simulated_response"] == (
        "AgentForge helps you compose agents into small workflows. "
        "This beginner Cog ran summarize -> respond and returned this final reply."
    )


def test_beginner_branch_loop_cog_resources_are_loaded(isolated_config: Config):
    """The shipped branch/loop Cog resources should support the beginner walkthrough."""
    branch_cog = isolated_config.find_config("cogs", "beginner_branch_loop_cog")["cog"]
    draft_prompt = isolated_config.find_config("prompts", "beginner_draft_agent")
    review_prompt = isolated_config.find_config("prompts", "beginner_review_agent")
    revise_prompt = isolated_config.find_config("prompts", "beginner_revise_agent")
    final_prompt = isolated_config.find_config("prompts", "beginner_final_agent")

    assert branch_cog["chat_memory_enabled"] is False
    assert branch_cog["flow"]["start"] == "draft"
    assert branch_cog["flow"]["transitions"]["draft"] == "review"
    assert branch_cog["flow"]["transitions"]["review"] == {
        "choice": {"approve": "final", "revise": "revise"},
        "fallback": "final",
        "max_visits": 2,
    }
    assert branch_cog["flow"]["transitions"]["revise"] == "review"
    assert branch_cog["flow"]["transitions"]["final"] == {"end": True}
    assert branch_cog["agents"] == [
        {"id": "draft", "template_file": "beginner_draft_agent"},
        {"id": "review", "template_file": "beginner_review_agent"},
        {"id": "revise", "template_file": "beginner_revise_agent"},
        {"id": "final", "template_file": "beginner_final_agent"},
    ]

    assert "{_ctx.user_input}" in draft_prompt["prompts"]["user"]
    assert "{_state.draft}" in review_prompt["prompts"]["user"]["draft"]
    assert "{_state.revise}" in review_prompt["prompts"]["user"]["revision"]
    assert review_prompt["parse_response_as"] == "json"
    assert review_prompt["simulated_response"] == (
        '{"choice": "revise", "rationale": "Make the reply more concrete for a beginner."}'
    )
    assert "{_state.review.rationale}" in revise_prompt["prompts"]["user"]
    assert "{_state.review.rationale}" in final_prompt["prompts"]["user"]["review"]
    assert final_prompt["simulated_response"] == (
        "AgentForge helps you turn prompts into small agent workflows. "
        "This branch/loop Cog drafted, reviewed, revised, and finished through its fallback after max_visits."
    )


def test_packaged_example_cog_response_prompt_matches_decision_node(isolated_config: Config):
    """The legacy packaged example should reference its real decision node ID."""
    response_prompt = isolated_config.find_config("prompts", "cog_response_agent")
    rationale_prompt = response_prompt["prompts"]["user"]["rationale"]

    assert "{_state.decision.rationale}" in rationale_prompt
    assert "{_state.decide.rationale}" not in rationale_prompt


def test_empty_yaml_file_loads_as_empty_dict(tmp_path: Path):
    """Empty YAML should normalize to an empty dictionary through both loader entrypoints."""
    empty_yaml = tmp_path / "empty.yaml"
    empty_yaml.write_text("")

    assert load_yaml_file(str(empty_yaml)) == {}
    assert Config.load_yaml_file(str(empty_yaml)) == {}


def test_reload_removes_deleted_yaml_from_loaded_data(isolated_config: Config):
    """Reloading should rebuild config data instead of retaining deleted YAML entries."""
    prompt_path = Path(isolated_config.config_path) / "prompts" / "TemporaryReloadAgent.yaml"
    prompt_path.write_text(
        """
prompts:
  user: "Hello"
"""
    )

    isolated_config.load_all_configurations()
    loaded_prompt = isolated_config.find_config("prompts", "TemporaryReloadAgent")
    assert loaded_prompt is not None
    assert loaded_prompt["prompts"]["user"] == "Hello"

    prompt_path.unlink()
    isolated_config.load_all_configurations()

    with pytest.raises(FileNotFoundError):
        isolated_config.find_config("prompts", "TemporaryReloadAgent")


def test_provider_defaults_are_current_and_codex_is_default(isolated_config: Config):
    """Setup defaults should keep provider params current and choose Codex for real calls."""
    model_settings = isolated_config.data["settings"]["models"]
    assert model_settings["default_model"] == {"api": "openai_api", "model": "codex_gpt55"}

    models = model_settings["model_library"]

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
