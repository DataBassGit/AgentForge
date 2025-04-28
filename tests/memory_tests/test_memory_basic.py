"""Tests for agentforge.storage.memory.Memory using FakeChroma."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

from agentforge.storage.memory import Memory
from tests.utils.fakes import FakeChromaStorage


@pytest.fixture()
def mem_a(fake_chroma):
    return Memory(cog_name="cog1", persona=None, collection_id="col")


def test_update_and_query_round_trip(mem_a):  # noqa: D103
    mem_a.update_memory({"k": "v"})
    res = mem_a.query_memory("v")
    assert res["documents"] == ["v"]


def test_storage_id_isolation(fake_chroma):  # noqa: D103
    m1 = Memory(cog_name="c1", persona=None, collection_id="col")
    m2 = Memory(cog_name="c2", persona=None, collection_id="col")

    m1.update_memory({"x": "1"})
    assert m2.query_memory("1") is None or m2.query_memory("1")["documents"] == []


# 5 workers, 20 writes each, must finish quickly
@pytest.mark.timeout(5, method="thread")
def test_thread_safety(fake_chroma):  # noqa: D103
    mem = Memory(cog_name="thread", persona=None, collection_id="col")

    def writer(val: str):
        mem.update_memory({"k": val})

    with ThreadPoolExecutor(max_workers=5) as pool:
        list(pool.map(writer, [str(i) for i in range(100)]))

    assert mem.storage.count_collection("col") == 100 