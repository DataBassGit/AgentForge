from __future__ import annotations

import logging
import shutil
import sys
from pathlib import Path

import pytest

# Ensure `src/` is importable without installing the package
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

# Ensure a .agentforge directory exists at repo root for eager imports that
# instantiate Config() before fixtures have a chance to run.
DEFAULT_AF = REPO_ROOT / ".agentforge"
if not DEFAULT_AF.exists():
    setup_src = SRC_PATH / "agentforge" / "setup_files"
    shutil.copytree(setup_src, DEFAULT_AF)

from agentforge.config import Config  # noqa: E402 – path fixed above
from tests.utils.fakes import FakeChromaStorage

import agentforge.storage.chroma_storage as cs_mod
import agentforge.storage.memory as mem_mod

# Apply monkeypatch early so any import pulls the fake.
cs_mod.ChromaStorage = FakeChromaStorage  # type: ignore[attr-defined]
mem_mod.ChromaStorage = FakeChromaStorage  # type: ignore[attr-defined]

# Provide missing convenience API required by storage tests
setattr(FakeChromaStorage, "create_collection", FakeChromaStorage.select_collection)

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

    cfg = Config.reset(root_path=str(tmp_path))
    yield cfg

    # Ensure singleton cleaned up for next test
    Config._instance = None


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
    decision_values = ["yes", "no", "other"]

    def fake_run(self: Agent, **context):  # type: ignore[override]
        name_l = self.agent_name.lower()
        if any(k in name_l for k in ("analyze", "decide", "response")):
            if "analyze" in name_l:
                return {"analysis": "stub-analysis"}
            if "decide" in name_l:
                idx = getattr(self, "_call_idx", 0)
                self._call_idx = idx + 1
                val = decision_values[idx % len(decision_values)]
                return {"choice": val, "rationale": "stub"}
            if "response" in name_l:
                return "FINAL RESPONSE"
        # otherwise defer to original behavior (e.g., TestAgent in unit tests)
        return original_run(self, **context)

    monkeypatch.setattr(Agent, "run", fake_run, raising=True)

    # Patch Cog._get_response_format_for_agent to be None-safe
    from agentforge.cog import Cog

    def _safe_get(self: Cog, agent_def):  # type: ignore[override]
        rf = agent_def.get("response_format", self.default_response_format)
        return rf.lower() if isinstance(rf, str) else None

    monkeypatch.setattr(Cog, "_get_response_format_for_agent", _safe_get, raising=True)
    yield


@pytest.fixture()
def example_cog(isolated_config):
    from agentforge.cog import Cog
    return Cog("ExampleCog") 