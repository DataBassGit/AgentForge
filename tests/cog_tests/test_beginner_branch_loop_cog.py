from pathlib import Path

from agentforge.cog import Cog


EXPECTED_FINAL_RESPONSE = (
    "AgentForge helps you turn prompts into small agent workflows. "
    "This branch/loop Cog drafted, reviewed, revised, and finished through its fallback after max_visits."
)


def _enable_debug_mode(isolated_config):
    system_path = Path(isolated_config.project_root) / ".agentforge" / "settings" / "system.yaml"
    system_text = system_path.read_text()
    system_path.write_text(system_text.replace("mode: false", "mode: true", 1))
    isolated_config.load_all_configurations()


def test_beginner_branch_loop_cog_debug_flow_uses_loop_guard(isolated_config, monkeypatch):
    """The beginner branch/loop Cog should run deterministically through max_visits fallback."""
    _enable_debug_mode(isolated_config)

    from agentforge.agent import Agent

    def fake_run(self: Agent, **_):
        agent_name = self.agent_name
        if agent_name == "beginner_draft_agent":
            return "AgentForge helps you compose prompts and agents into repeatable workflows."
        if agent_name == "beginner_review_agent":
            return {"choice": "revise", "rationale": "Make the reply more concrete for a beginner."}
        if agent_name == "beginner_revise_agent":
            return "AgentForge lets you define prompt files, wire them into Cogs, and run the workflow from Python."
        if agent_name == "beginner_final_agent":
            return EXPECTED_FINAL_RESPONSE
        raise AssertionError(f"Unexpected agent: {agent_name}")

    monkeypatch.setattr(Agent, "run", fake_run, raising=True)
    cog = Cog("beginner_branch_loop_cog")

    result = cog.run(user_input="Explain AgentForge in one sentence.")
    trail = cog.get_track_flow_trail()

    assert result == EXPECTED_FINAL_RESPONSE
    assert cog.mem_mgr.memory_nodes == {}
    assert [entry.agent_id for entry in trail] == [
        "draft",
        "review",
        "revise",
        "review",
        "revise",
        "review",
        "final",
    ]
