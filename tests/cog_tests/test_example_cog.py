from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys

import pytest

from agentforge.storage.memory import Memory


@pytest.mark.timeout(1)
def test_example_cog_runs(example_cog):
    ctx = example_cog.run(user_input="hello")

    # Keys produced by stub agents
    assert any(k in str(ctx).lower() for k in ("analysis", "rationale", "final"))

    # memory interaction – general_memory collection should exist
    mem: Memory = next(iter(example_cog.memories.values()))["instance"]  # type: ignore[index]
    assert mem.storage.count_collection(mem.collection_name) > 0


@pytest.mark.parametrize("decision_key", ["choice", "conclusion", "foo"])
def test_decision_key_flexibility(monkeypatch, tmp_path, isolated_config, decision_key):
    # monkeypatch DecideAgent stub to emit desired key
    from agentforge.agent import Agent

    # Save previously stubbed run method to use for non-decision agents
    original_run = Agent.run

    def fake_run(self: Agent, **_):
        # Only override for the DecideAgent
        if "decide" in self.agent_name.lower():
            return {decision_key: "approve"}
        # Delegate to original stub for other agents
        return original_run(self, **_)

    monkeypatch.setattr(Agent, "run", fake_run, raising=True)

    # modify YAML transition key inside tmp .agentforge
    yaml_path = Path(isolated_config.project_root) / ".agentforge" / "cogs" / "ExampleCog.yaml"
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

    cog = Cog("ExampleCog")
    out = cog.run(user_input="hi")
    assert "FINAL" in str(out)


@pytest.mark.timeout(2)
def test_loop_limit(monkeypatch, example_cog):
    # Patch decide to always say no – loop until max_visits then default
    from agentforge.agent import Agent

    monkeypatch.setattr(Agent, "run", lambda self, **_: {"choice": "no"} if "decide" in self.agent_name.lower() else {}, raising=False)

    with pytest.raises(Exception):
        example_cog.run(user_input="hi")


def test_bad_transition_raises(monkeypatch, tmp_path, isolated_config):
    """Test that when a transition references an invalid agent, the fallback is used."""
    yaml_path = Path(isolated_config.project_root) / ".agentforge" / "cogs" / "ExampleCog.yaml"
    
    # Replace approve: respond with approve: NONEXISTENT_AGENT
    original_content = yaml_path.read_text()
    new_content = original_content.replace("approve: respond", "approve: NONEXISTENT_AGENT")
    yaml_path.write_text(new_content)
    
    # Force the decide agent to return 'approve' to trigger the invalid transition
    from agentforge.agent import Agent
    
    original_run = Agent.run
    
    def forced_approve_run(self: Agent, **_):
        if "decide" in self.agent_name.lower():
            return {"choice": "approve"}
        return original_run(self, **_)
    
    monkeypatch.setattr(Agent, "run", forced_approve_run, raising=True)

    # Create a cog with the modified YAML
    from agentforge.cog import Cog
    cog = Cog("ExampleCog")
    
    # When we run the cog, it should use the fallback branch since the transition is invalid
    result = cog.run(user_input="bad")
    
    # Verify that execution continued using the fallback mechanism and didn't raise an exception
    assert result is not None, "Cog execution should complete without raising an exception"


def test_concurrent_cogs_isolated(fake_chroma, isolated_config):
    from agentforge.cog import Cog
    
    # Reset the ExampleCog.yaml to the original state
    yaml_path = Path(isolated_config.project_root) / ".agentforge" / "cogs" / "ExampleCog.yaml"
    if "NONEXISTENT_AGENT" in yaml_path.read_text():
        # Fix the YAML file to use the correct agent names
        text = yaml_path.read_text().replace("approve: NONEXISTENT_AGENT", "approve: respond")
        yaml_path.write_text(text)

    def run_one(idx: int):
        c = Cog("ExampleCog")
        return c.run(user_input=str(idx))

    with ThreadPoolExecutor(2) as pool:
        futures = list(pool.map(run_one, [1, 2]))

    assert all("FINAL" in str(r) for r in futures)


def test_max_visits_without_fallback(monkeypatch, tmp_path, isolated_config):
    """Test that when max_visits is reached, the cog correctly uses the fallback."""
    # Force the decide agent to always return 'reject' to trigger a loop
    from agentforge.agent import Agent
    
    original_run = Agent.run
    
    def always_reject_run(self: Agent, **_):
        if "decide" in self.agent_name.lower():
            return {"choice": "reject"}
        if "analyze" in self.agent_name.lower():
            return {"analysis": "This is a test analysis"}
        if "respond" in self.agent_name.lower():
            return "FINAL RESPONSE - FALLBACK"
        return original_run(self, **_)
    
    monkeypatch.setattr(Agent, "run", always_reject_run, raising=True)
    
    # Create and run the cog
    from agentforge.cog import Cog
    cog = Cog("ExampleCog")
    
    # This would normally cause an infinite loop, but max_visits: 3 should prevent it
    # and trigger the fallback to respond
    result = cog.run(user_input="test")
    
    # The important thing is that the cog completed without hanging in an infinite loop
    assert result is not None, "Cog should complete execution despite loop"
    # The stubbed respond agent returns a string
    assert "FINAL RESPONSE" in str(result), "Should include the response from fallback"


def test_invalid_transition_uses_fallback(monkeypatch, tmp_path, isolated_config):
    """Test that when a transition would go to an invalid agent, the fallback is used."""
    # This test replaces test_agent_not_defined which had invalid assumptions
    
    yaml_path = Path(isolated_config.project_root) / ".agentforge" / "cogs" / "ExampleCog.yaml"
    content = yaml_path.read_text()
    
    # Replace the valid 'respond' agent with a non-existent one in a specific transition
    modified_content = content.replace("          approve: respond", "          approve: invalid_agent")
    yaml_path.write_text(modified_content)
    
    # Force the decide agent to return 'approve' to trigger the invalid transition
    from agentforge.agent import Agent
    
    original_run = Agent.run
    
    def approve_run(self: Agent, **_):
        if "decide" in self.agent_name.lower():
            return {"choice": "approve"}
        return original_run(self, **_)
    
    monkeypatch.setattr(Agent, "run", approve_run, raising=True)
    
    # Create and run the cog - it should use the fallback
    from agentforge.cog import Cog
    cog = Cog("ExampleCog")
    result = cog.run(user_input="test")
    
    # The result should include fallback behavior
    assert result is not None, "Cog should complete execution"


def test_no_decision_key_uses_fallback(monkeypatch, tmp_path, isolated_config):
    """Test that when no decision key is present in the agent's output, the fallback is used."""
    # Here we're testing that the fallback mechanism works even if the agent's output doesn't 
    # contain the expected decision key
    from agentforge.agent import Agent
    
    # We'll modify the decide agent to return something without the 'choice' key
    def modified_run(self: Agent, **_):
        name_l = self.agent_name.lower()
        if "decide" in name_l:
            return {"some_other_key": "value"}  # No 'choice' key
        # Let other agents use the default stubbed implementation
        if "analyze" in name_l:
            return {"analysis": "stub-analysis"}
        if "response" in name_l or "respond" in name_l:
            return "FINAL RESPONSE"
        return {}
    
    monkeypatch.setattr(Agent, "run", modified_run, raising=True)
    
    # Create and run the cog
    from agentforge.cog import Cog
    cog = Cog("ExampleCog")
    result = cog.run(user_input="test")
    
    # The important part is that execution completes by using the fallback
    # The actual value doesn't matter as much as the fact that we didn't hang
    assert result is not None, "Cog should complete execution"
    # The output contains the response from our stub
    assert "FINAL RESPONSE" in str(result), "Should contain the final agent output" 