"""Basic happy-path tests for agentforge.agent.Agent.

These do not hit network/model back-ends thanks to the debug mode present in
setup_files. They ensure that template rendering, deterministic `run` output
and idempotency work.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any
from unittest.mock import patch

import pytest

from agentforge.agent import Agent
from agentforge.config import Config
from agentforge.core.config_manager import ConfigManager


@pytest.fixture()
def dummy_agent_config(isolated_config: Config) -> 'ConfigManager.AgentConfig':  # noqa: D103
    # Create a ConfigManager instance to build structured config
    config_manager = ConfigManager()
    
    # Minimal agent data dict; ensure debug mode true
    raw_agent_data = {
        "name": "TestAgent",
        "params": {},
        "prompts": {
            "system": "Hello {name}",
            "user": "{message}",
        },
        "model": object(),
        "settings": isolated_config.data["settings"].copy(),
        "simulated_response": "SIMULATED",
    }
    raw_agent_data["settings"]["system"]["debug"]["mode"] = True
    
    # Use ConfigManager to build structured config object
    return config_manager.build_agent_config(raw_agent_data)


def test_run_returns_simulated(dummy_agent_config):  # noqa: D103
    with patch.object(Config, "load_agent_data", return_value=dummy_agent_config):
        agent = Agent("TestAgent")
        out = agent.run(name="Bob", message="ping")
        assert out == "SIMULATED" or out == "STUB"
        # Template variables stored
        assert agent.template_data["name"] == "Bob"
        assert agent.template_data["message"] == "ping"
        # Prompt rendered correctly
        assert agent.prompt == {"system": "Hello Bob", "user": "ping"}


def test_idempotent_run(dummy_agent_config):  # noqa: D103
    with patch.object(Config, "load_agent_data", return_value=dummy_agent_config):
        agent = Agent("TestAgent")
        first = agent.run(name="X", message="y")
        second = agent.run(name="X", message="y")
        assert first == second 