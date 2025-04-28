"""Contract tests for the in-memory FakeChromaStorage backend."""
from __future__ import annotations

import pytest

from tests.utils.fakes import FakeChromaStorage


@pytest.fixture()
def chroma():  # noqa: D401 – returns instance
    store = FakeChromaStorage.get_or_create("test_store")
    yield store
    FakeChromaStorage.clear_registry()


def test_basic_crud_cycle(chroma):  # noqa: D103
    chroma.create_collection("col1")
    chroma.save_to_storage(collection_name="col1", data=["hello"], ids=["1"], metadata=[{}])

    got = chroma.query_storage(collection_name="col1", num_results=1)
    assert got["documents"] == ["hello"]

    chroma.save_to_storage(collection_name="col1", data=["world"], ids=["1"], metadata=[{}])
    got2 = chroma.query_storage(collection_name="col1", num_results=1)
    assert got2["documents"] == ["world"]

    chroma.delete_from_storage(collection_name="col1", ids=["1"])
    assert chroma.count_collection("col1") == 0

    chroma.reset_storage()
    assert chroma.count_collection("col1") == 0


def test_collection_isolation(fake_chroma):  # noqa: D103
    s1 = fake_chroma.get_or_create("alpha")
    s2 = fake_chroma.get_or_create("beta")

    s1.save_to_storage(collection_name="c", data=["a"], ids=["1"], metadata=[{}])
    s2.save_to_storage(collection_name="c", data=["b"], ids=["1"], metadata=[{}])

    assert s1.query_storage(collection_name="c", num_results=1)["documents"] == ["a"]
    assert s2.query_storage(collection_name="c", num_results=1)["documents"] == ["b"]


def test_query_empty_returns_empty(chroma):  # noqa: D103
    chroma.create_collection("empty")
    assert chroma.query_storage(collection_name="empty", num_results=1) == {} 