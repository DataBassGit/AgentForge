from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys

import pytest

from agentforge.storage.memory import Memory


@pytest.mark.timeout(1)
def test_example_cog_runs_and_creates_memory(example_cog):
    """Test that ExampleCog executes successfully and creates memory entries."""
    ctx = example_cog.run(user_input="hello")

    # Keys produced by stub agents
    assert any(k in str(ctx).lower() for k in ("analysis", "rationale", "final"))

    # memory interaction – general_memory collection should exist
    mem: Memory = next(iter(example_cog.mem_mgr.memory_nodes.values()))["instance"]  # type: ignore[index]
    assert mem.store is not None


@pytest.mark.parametrize("decision_key", ["choice", "conclusion", "foo"])
def test_decision_key_flexibility(monkeypatch, tmp_path, isolated_config, decision_key):
    """Test that cogs support flexible decision key names in transitions."""
    # monkeypatch DecideAgent stub to emit desired key
    from agentforge.agent import Agent

    # Save previously stubbed run method to use for non-decision agents
    original_run = Agent.run

    def fake_run(self: Agent, **_):
        # Only override for the decide_agent
        if "decide" in self.agent_name.lower():
            return {decision_key: "approve"}
        # Delegate to original stub for other agents
        return original_run(self, **_)

    monkeypatch.setattr(Agent, "run", fake_run, raising=True)

    # modify YAML transition key inside tmp .agentforge
    yaml_path = Path(isolated_config.project_root) / ".agentforge" / "cogs" / "example_cog.yaml"
    text = yaml_path.read_text()
    # Replace the entire decision structure, not just the key name
    old_structure = """
      choice:
        approve: respond
        reject: analyze
"""
    new_structure = f"""
      {decision_key}:
        approve: respond
        reject: analyze
"""
    text = text.replace(old_structure, new_structure)
    yaml_path.write_text(text)

    from agentforge.cog import Cog

    cog = Cog("example_cog")
    out = cog.run(user_input="hi")
    assert "FINAL" in str(out)


@pytest.mark.timeout(2)
def test_max_visits_protection_prevents_infinite_loops(monkeypatch, example_cog):
    """Test that max_visits setting prevents infinite loops in cog execution."""
    # Patch decide to always say no – loop until max_visits then default
    from agentforge.agent import Agent

    monkeypatch.setattr(Agent, "run", lambda self, **_: {"choice": "no"} if "decide" in self.agent_name.lower() else {}, raising=False)

    with pytest.raises(Exception):
        example_cog.run(user_input="hi")


@pytest.mark.parametrize("failure_type,setup_function", [
    ("invalid_agent", lambda yaml_path: yaml_path.write_text(yaml_path.read_text().replace("approve: respond", "approve: NONEXISTENT_AGENT"))),
    ("missing_decision_key", lambda yaml_path: None)  # Will be handled in agent mock
])
def test_cog_fallback_mechanisms(monkeypatch, tmp_path, isolated_config, failure_type, setup_function):
    """Test that cogs gracefully handle various failure conditions using fallback mechanisms."""
    yaml_path = Path(isolated_config.project_root) / ".agentforge" / "cogs" / "example_cog.yaml"
    
    # Setup the failure condition
    if setup_function:
        setup_function(yaml_path)
    
    from agentforge.agent import Agent
    original_run = Agent.run
    
    def failing_run(self: Agent, **_):
        agent_name = self.agent_name.lower()
        
        if failure_type == "missing_decision_key" and "decide" in agent_name:
            return {"some_other_key": "value"}  # No expected decision key
        elif failure_type == "invalid_agent" and "decide" in agent_name:
            return {"choice": "approve"}  # Will trigger invalid transition
        
        # Default stubbed behavior for other agents
        return original_run(self, **_)
    
    monkeypatch.setattr(Agent, "run", failing_run, raising=True)

    # Create and run the cog - it should handle failures gracefully
    from agentforge.cog import Cog
    cog = Cog("example_cog")
    result = cog.run(user_input="test")
    
    # Verify that execution completed without hanging or crashing
    assert result is not None, f"Cog should complete execution despite {failure_type}"


def test_concurrent_cog_execution_isolation(fake_chroma, isolated_config):
    """Test that concurrent cog executions are properly isolated from each other."""
    from agentforge.cog import Cog
    
    def run_one(idx: int):
        c = Cog("example_cog")
        return c.run(user_input=str(idx))

    with ThreadPoolExecutor(2) as pool:
        futures = list(pool.map(run_one, [1, 2]))

    assert all("FINAL" in str(r) for r in futures)


# Removed redundant tests:
# - test_bad_transition_raises: Merged into test_cog_fallback_mechanisms 
# - test_max_visits_without_fallback: Redundant with test_max_visits_protection_prevents_infinite_loops
# - test_invalid_transition_uses_fallback: Merged into test_cog_fallback_mechanisms
# - test_no_decision_key_uses_fallback: Merged into test_cog_fallback_mechanisms 

def test_dot_notated_end_returns_nested_value(tmp_path, isolated_config, monkeypatch):
    """Test that a dot-notated end value returns the correct nested field from agent output."""
    import yaml
    from agentforge.cog import Cog
    from agentforge.agent import Agent
    from pathlib import Path

    # Create a test cog config with dot-notated end
    cog_config = {
        "cog": {
            "agents": [
                {"id": "generate", "template_file": "test_template"}
            ],
            "flow": {
                "start": "generate",
                "transitions": {
                    "generate": {"end": "generate.final_response"}
                }
            }
        }
    }
    cog_path = Path(isolated_config.project_root) / ".agentforge" / "cogs" / "DotEndCog.yaml"
    with open(cog_path, 'w') as f:
        yaml.dump(cog_config, f)

    # Create a minimal agent template
    template_config = {
        "prompts": {"system": "Test system prompt", "user": "Test user prompt"},
        "settings": {"system": {"debug": {"mode": True}}},
        "simulated_response": "Test simulated response"
    }
    template_path = Path(isolated_config.project_root) / ".agentforge" / "prompts" / "test_template.yaml"
    with open(template_path, 'w') as f:
        yaml.dump(template_config, f)

    # Reload configuration after writing new files
    isolated_config.load_all_configurations()

    # Monkeypatch the agent to return a dict with a nested field
    def fake_run(self, **_):
        return {
            "introspection": "not the value you want",
            "final_response": "THIS IS THE NESTED VALUE"
        }
    monkeypatch.setattr(Agent, "run", fake_run, raising=True)

    # Run the cog and check the result
    cog = Cog("DotEndCog")
    result = cog.run(user_input="test")
    assert result == "THIS IS THE NESTED VALUE", f"Expected only the nested value, got: {result}" 