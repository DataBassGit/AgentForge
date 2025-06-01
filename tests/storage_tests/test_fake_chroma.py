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


def test_save_invalid_lengths_raises(chroma):
    chroma.create_collection("col2")
    # Mismatched data and ids
    with pytest.raises(ValueError):
        chroma.save_to_storage(collection_name="col2", data=["a", "b"], ids=["1"], metadata=[{}])
    # Mismatched data and metadata
    with pytest.raises(ValueError):
        chroma.save_to_storage(collection_name="col2", data=["a"], ids=["1"], metadata=[{}, {}])


def test_query_with_filter_and_embedding(chroma):
    chroma.create_collection("col3")
    chroma.save_to_storage(collection_name="col3", data=["foo"], ids=["1"], metadata=[{"type": "test"}])
    # Simulate a filter query (FakeChromaStorage should support this)
    result = chroma.query_storage(collection_name="col3", filter_condition={"type": "test"}, num_results=1)
    assert result["documents"] == ["foo"]


def test_delete_nonexistent_document(chroma):
    chroma.create_collection("col4")
    # Should not raise
    chroma.delete_from_storage(collection_name="col4", ids=["doesnotexist"])
    # Still empty
    assert chroma.count_collection("col4") == 0


def test_peek_and_count_collection(chroma):
    chroma.create_collection("col5")
    chroma.save_to_storage(collection_name="col5", data=["peek"], ids=["1"], metadata=[{}])
    assert chroma.count_collection("col5") == 1
    peeked = chroma.peek("col5")
    assert "documents" in peeked or peeked == {"documents": "No Results!"}


def test_select_collection_invalid_name_raises(chroma):
    # Simulate invalid collection name (e.g., empty string)
    with pytest.raises(Exception):
        chroma.create_collection("") 