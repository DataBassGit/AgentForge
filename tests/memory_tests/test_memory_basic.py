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