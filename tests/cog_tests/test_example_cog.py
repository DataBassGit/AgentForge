from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

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

    def fake_decide(self: Agent, **_):
        return {decision_key: "yes"}

    monkeypatch.setattr(Agent, "run", fake_decide, raising=False)

    # modify YAML transition key inside tmp .agentforge
    yaml_path = Path(isolated_config.project_root) / ".agentforge" / "cogs" / "ExampleCog.yaml"
    text = yaml_path.read_text()
    text = text.replace("choice:", f"{decision_key}:")
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
    yaml_path = Path(isolated_config.project_root) / ".agentforge" / "cogs" / "ExampleCog.yaml"
    text = yaml_path.read_text().replace("yes: respond", "yes: UNKNOWN")
    yaml_path.write_text(text)

    from agentforge.cog import Cog
    cog = Cog("ExampleCog")
    with pytest.raises(Exception):
        cog.run(user_input="bad")


def test_concurrent_cogs_isolated(fake_chroma, isolated_config):
    from agentforge.cog import Cog

    def run_one(idx: int):
        c = Cog("ExampleCog")
        return c.run(user_input=str(idx))

    with ThreadPoolExecutor(2) as pool:
        futures = list(pool.map(run_one, [1, 2]))

    assert all("FINAL" in str(r) for r in futures) 