from agentforge.cog import Cog


def test_beginner_summary_cog_runs_as_no_memory_two_step_flow(isolated_config):
    """The beginner Cog should run summarize -> respond without memory nodes."""
    cog = Cog("beginner_summary_cog")

    result = cog.run(user_input="What can AgentForge help me build?")
    trail = cog.get_track_flow_trail()

    assert result == "FINAL RESPONSE"
    assert cog.mem_mgr.memory_nodes == {}
    assert [entry.agent_id for entry in trail] == ["summarize", "respond"]
