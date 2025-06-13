from __future__ import annotations

import logging
import shutil
import sys
from pathlib import Path

import pytest

from agentforge.testing.bootstrap import bootstrap_test_env
bootstrap_test_env(use_fakes=True, silence_output=True, cleanup_on_exit=False)

# Because bootstrap switched CWD to the repo root and placed `src/` on the
# import path, we can now cleanly reference repository-local resources.
REPO_ROOT = Path.cwd()
SRC_PATH = REPO_ROOT / "src"

from agentforge.config import Config  # noqa: E402 – path fixed above
from tests.utils.fakes import FakeChromaStorage

###############################################################################
# Generic helpers & fixtures
###############################################################################

@pytest.fixture(autouse=True)
def _silence_print_and_logging(monkeypatch):
    """Keep test output clean by silencing print and lowering logging."""
    logging.disable(logging.CRITICAL)
    monkeypatch.setattr("builtins.print", lambda *args, **kwargs: None)
    yield
    logging.disable(logging.NOTSET)


@pytest.fixture()
def isolated_config(tmp_path) -> Config:
    """Return a fresh Config instance bound to an isolated temporary .agentforge."""
    # Copy default setup files into the tmp directory
    setup_src = SRC_PATH / "agentforge" / "setup_files"
    shutil.copytree(setup_src, tmp_path / ".agentforge")

    # Store the original YAML content for ExampleCog
    example_cog_path = tmp_path / ".agentforge" / "cogs" / "example_cog.yaml"
    original_yaml = example_cog_path.read_text()

    # Create the Config instance
    cfg = Config.reset(root_path=str(tmp_path))
    
    # Provide the config to the test
    yield cfg

    # After the test completes, restore the original YAML
    # This ensures that changes made by one test don't affect others
    example_cog_path.write_text(original_yaml)
    
    # Ensure singleton cleaned up for next test
    Config._instance = None


@pytest.fixture()
def clean_yaml_after_test():
    """Fixture to ensure that ExampleCog.yaml is restored to its original state after each test."""
    # Get the path to the repo's .agentforge directory
    agentforge_dir = REPO_ROOT / ".agentforge"
    example_cog_path = agentforge_dir / "cogs" / "example_cog.yaml"
    
    # Save the original content
    original_content = None
    if example_cog_path.exists():
        original_content = example_cog_path.read_text()
    
    # Let the test run
    yield
    
    # After the test, restore the original content
    if original_content is not None:
        example_cog_path.write_text(original_content)

# Apply the clean_yaml_after_test fixture to all tests in the cog_tests directory
@pytest.fixture(autouse=True, scope="function")
def auto_clean_yaml(request):
    """Automatically apply clean_yaml_after_test to all tests in cog_tests."""
    if "cog_tests" in request.module.__name__:
        request.getfixturevalue("clean_yaml_after_test")


@pytest.fixture()
def fake_chroma():
    """Return the FakeChromaStorage class and clear registry after test."""
    yield FakeChromaStorage
    FakeChromaStorage.clear_registry()


# ---------------------------------------------------------------------------
# Cog / Agent stubs
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def stubbed_agents(monkeypatch):
    """Monkey-patch Agent.run for ExampleCog agents so no model work happens."""

    from agentforge.agent import Agent

    original_run = Agent.run
    decision_values = ["approve", "reject", "other"]

    def fake_run(self: Agent, **context):  # type: ignore[override]
        # Check if this agent has debug mode enabled and should use original behavior
        if hasattr(self, 'settings') and self.settings.get('system', {}).get('debug', {}).get('mode', False):
            # Let debug mode handle this agent normally
            return original_run(self, **context)
        # Increment branch_call_counts if self._cog is present
        if hasattr(self, '_cog') and hasattr(self._cog, 'branch_call_counts'):
            self._cog.branch_call_counts[self.agent_name] = self._cog.branch_call_counts.get(self.agent_name, 0) + 1
        name_l = self.agent_name.lower()
        
        # Handle specific agent types with their expected outputs
        if "analyze" in name_l:
            return {"analysis": "stub-analysis"}
        elif "decide" in name_l:
            idx = getattr(self, "_call_idx", 0)
            self._call_idx = idx + 1
            val = decision_values[idx % len(decision_values)]
            return {"choice": val, "rationale": "stub"}
        elif "response" in name_l or "respond" in name_l:
            return "FINAL RESPONSE"
        elif "understand" in name_l:
            return {
                "insights": "User is asking about programming topics",
                "user_intent": "Seeking information or help",
                "relevant_topics": ["programming", "learning"],
                "persona_relevant": "User shows interest in technical topics"
            }
        else:
            # For any other agent, check if it's a known test agent that should use original behavior
            if "test" in name_l:
                return original_run(self, **context)
            # Otherwise provide a generic response for cog agents
            return f"Simulated response from {self.agent_name}"

    monkeypatch.setattr(Agent, "run", fake_run, raising=True)

    # Note: _get_response_format_for_agent method was removed during Cog refactor
    # Response format handling is now done by individual agents
    yield


@pytest.fixture()
def example_cog(isolated_config):
    from agentforge.cog import Cog
    return Cog("example_cog")


@pytest.fixture(autouse=True, scope="session")
def cleanup_root_dot_agentforge():
    """Clean up any .agentforge directory at the repo root after all tests have run."""
    # Let the tests run
    yield
    
    # After all tests, clean up any .agentforge directory at the repo root
    root_dot_agentforge = REPO_ROOT / ".agentforge"
    if root_dot_agentforge.exists() and root_dot_agentforge.is_dir():
        try:
            shutil.rmtree(root_dot_agentforge)
            print(f"Cleaned up {root_dot_agentforge}")
        except Exception as e:
            print(f"Failed to clean up {root_dot_agentforge}: {e}") 