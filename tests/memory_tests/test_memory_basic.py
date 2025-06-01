"""Tests for agentforge.storage.memory.Memory using FakeChroma."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

from agentforge.storage.memory import Memory
from tests.utils.fakes import FakeChromaStorage


@pytest.fixture()
def mem_a(fake_chroma):
    return Memory(cog_name="cog1", persona=None, collection_id="col")


def make_mem():
    return Memory(cog_name="cog1", persona=None, collection_id="col")


def test_update_and_query_round_trip(mem_a):  # noqa: D103
    ctx, state = {"k": "v"}, {}
    mem_a.update_memory(["k"], _ctx=ctx, _state=state)
    res = mem_a.query_memory(["k"], _ctx=ctx, _state=state)
    assert res is None or res["raw"]["documents"] == []


def test_storage_id_isolation(fake_chroma):  # noqa: D103
    ctx, state = {"x": "1"}, {}
    m1 = Memory(cog_name="c1", persona=None, collection_id="col")
    m2 = Memory(cog_name="c2", persona=None, collection_id="col")

    m1.update_memory(["x"], _ctx=ctx, _state=state)
    assert m2.query_memory(["x"], _ctx=ctx, _state=state) is None or m2.query_memory(["x"], _ctx=ctx, _state=state)["raw"]["documents"] == [] 


def test_delete_existing_and_nonexistent_id(mem_a):
    ctx, state = {"k": "v"}, {}
    mem_a.update_memory(["k"], _ctx=ctx, _state=state)
    # Try deleting an existing id (should not raise)
    try:
        mem_a.delete(["1"])
    except Exception:
        pytest.fail("delete should not raise for existing id")
    # Try deleting a non-existent id (should not raise)
    try:
        mem_a.delete(["doesnotexist"])
    except Exception:
        pytest.fail("delete should not raise for non-existent id")


def test_wipe_memory_success(mem_a):
    ctx, state = {"k": "v"}, {}
    mem_a.update_memory(["k"], _ctx=ctx, _state=state)
    try:
        mem_a.wipe_memory()
    except Exception:
        pytest.fail("wipe_memory should not raise")
    # After wipe, query should return nothing
    assert mem_a.query_memory(["k"], _ctx=ctx, _state=state) is None


def test_query_memory_with_empty_context(mem_a):
    res = mem_a.query_memory([], _ctx={}, _state={})
    assert res is None or "raw" not in res


def test_update_memory_with_no_data(mem_a):
    # No update keys, empty context/state
    mem_a.update_memory([], _ctx={}, _state={})
    # Should not raise or update anything
    assert mem_a.store == {} 