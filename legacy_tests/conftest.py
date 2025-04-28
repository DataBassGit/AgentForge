# Fake ChromaDB stub and pytest fixtures for AgentForge test suite migration.
# This file is automatically discovered by pytest and provides project-wide fixtures
# that replace the real Chroma dependency, create an isolated `.agentforge/` folder
# per-test, and silence noisy output (print/logging).

from __future__ import annotations

import logging
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest
from types import ModuleType

# Ensure the repository's `src/` directory is on the Python path so that
# `import agentforge` works when the project is not installed in editable mode.
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

# Guarantee a '.agentforge' directory exists at repo root so Config can initialize
DEFAULT_AGENTFORGE_DIR = REPO_ROOT / ".agentforge"
if not DEFAULT_AGENTFORGE_DIR.exists():
    setup_src_dir = SRC_PATH / "agentforge" / "setup_files"
    # Use shutil.copytree with dirs_exist_ok for Python 3.11
    shutil.copytree(setup_src_dir, DEFAULT_AGENTFORGE_DIR, dirs_exist_ok=True)

from agentforge.config import Config

###############################################################################
# Section 1: Minimal in-memory fake of the ChromaStorage public surface
###############################################################################

class _FakeCollection:
    """A trivially in-memory collection that stores documents & metadata by id."""

    def __init__(self) -> None:
        self._docs: Dict[str, str] = {}
        self._metas: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # CRUD helpers (ChromaStorage delegates to `upsert`, `get`, `delete`, …)
    # ------------------------------------------------------------------
    def upsert(self, *, documents: List[str], metadatas: List[dict], ids: List[str]) -> None:  # type: ignore[override]
        for _id, doc, meta in zip(ids, documents, metadatas):
            self._docs[_id] = doc
            self._metas[_id] = meta or {}

    def get(self, **kwargs) -> Dict[str, List[Any]]:  # noqa: D401 – match Chroma's shape
        ids = kwargs.get("ids")
        if ids is None:
            ids = list(self._docs.keys())
        ids = list(map(str, ids))
        return {
            "ids": ids,
            "documents": [self._docs[i] for i in ids if i in self._docs],
            "metadatas": [self._metas.get(i, {}) for i in ids],
        }

    def delete(self, ids: Optional[List[str]] = None) -> None:  # noqa: D401 – API compatibility
        if ids is None:
            ids = list(self._docs.keys())
        for _id in ids:
            self._docs.pop(_id, None)
            self._metas.pop(_id, None)

    # ------------------------------------------------------------------
    # Convenience wrappers used by AgentForge memory helpers
    # ------------------------------------------------------------------
    def count(self) -> int:  # pragma: no cover – trivial
        return len(self._docs)

    def query(self, *, query: Optional[str | List[str]] = None, num_results: int = 1, **_) -> Dict[str, Any]:  # type: ignore[override]
        """Very naive full-text matcher – suffices for unit tests."""
        if not self._docs:
            return {}
        ids = list(self._docs.keys())[:num_results]
        return {
            "documents": [self._docs[i] for i in ids],
            "metadatas": [self._metas[i] for i in ids],
            "ids": ids,
            "distances": [0.0] * len(ids),
        }

###############################################################################
# Public stub mirroring agentforge.storage.chroma_storage.ChromaStorage API
###############################################################################

class FakeChromaStorage:  # noqa: D101 – Docstring omitted for brevity
    _registry: Dict[str, "FakeChromaStorage"] = {}

    # ChromaStorage keeps a global client & collection attributes – we mimic them
    def __init__(self, storage_id: str | None = None):
        # Accept optional storage_id for compatibility with legacy tests that
        # instantiate `ChromaStorage()` without arguments.
        if storage_id is None:
            storage_id = "default"
        self.storage_id = storage_id
        self._collections: Dict[str, _FakeCollection] = {}
        self.collection: Optional[_FakeCollection] = None

    # ---------------------------- class helpers -----------------------------
    @classmethod
    def get_or_create(cls, storage_id: str):  # noqa: D401 – API compatibility
        if storage_id not in cls._registry:
            cls._registry[storage_id] = cls(storage_id)
        return cls._registry[storage_id]

    @classmethod
    def clear_registry(cls):  # pragma: no cover – rarely used
        cls._registry.clear()

    # ----------------------- collection management -------------------------
    def select_collection(self, collection_name: str):
        self.collection = self._collections.setdefault(collection_name, _FakeCollection())
        return self.collection

    def delete_collection(self, collection_name: str):
        self._collections.pop(collection_name, None)
        if self.collection and collection_name == self.collection:  # type: ignore[comparison-overlap]
            self.collection = None

    def count_collection(self, collection_name: str) -> int:
        return self._collections.get(collection_name, _FakeCollection()).count()

    # ---------------------------- high-level API ---------------------------
    def save_to_storage(
        self,
        *,
        collection_name: str,
        data: List[str] | str,
        ids: Optional[List[str]] = None,
        metadata: Optional[List[dict]] = None,
    ) -> None:  # noqa: D401 – compliance with real signature
        data = [data] if isinstance(data, str) else list(data)
        if ids is None:
            ids = [str(i) for i in range(1, len(data) + 1)]
        if metadata is None:
            metadata = [{} for _ in data]
        self.select_collection(collection_name).upsert(documents=data, metadatas=metadata, ids=ids)

    def query_storage(
        self,
        *,
        collection_name: str,
        query: Optional[str | List[str]] = None,
        num_results: int = 1,
        **__,
    ) -> Dict[str, Any]:  # noqa: D401 – mimic return shape
        return self.select_collection(collection_name).query(query=query, num_results=num_results)

    def delete_from_storage(self, collection_name: str, ids: List[str] | str):
        if not isinstance(ids, list):
            ids = [ids]  # type: ignore[list-item]
        self.select_collection(collection_name).delete(ids)

    def reset_storage(self):  # pragma: no cover
        self._collections.clear()
        self.collection = None

    # ------------------------------------------------------------------
    # Legacy ChromaStorage API wrappers used in existing unittest suite
    # ------------------------------------------------------------------

    # The original ChromaStorage lazily creates a client on connect(); our stub
    # is in-memory so connect/disconnect are no-ops.
    def connect(self):  # noqa: D401
        return None

    def disconnect(self):  # noqa: D401
        return None

    # Collection helpers --------------------------------------------------
    def create_collection(self, name: str):
        self.select_collection(name)

    # Note: tests expect `delete_collection` already defined above.

    # CRUD helpers --------------------------------------------------------
    def insert(self, collection_name: str, ids: list[str], data: list[str]):
        # No metadata parameter in tests, pass empty dicts.
        self.save_to_storage(collection_name=collection_name, data=data, ids=ids, metadata=[{}] * len(ids))

    def update(self, collection_name: str, ids: list[str], new_data: list[str]):
        self.save_to_storage(collection_name=collection_name, data=new_data, ids=ids, metadata=[{}] * len(ids))

    def query(self, *, collection_name: str, ids: list[str]):  # noqa: D401
        coll = self.select_collection(collection_name)
        return coll.get(ids=ids)

    def count(self, collection_name: str):
        return self.count_collection(collection_name)

    def delete(self, collection_name: str, ids: list[str]):
        self.delete_from_storage(collection_name, ids)

    # The following helpers are used by Memory classes – keep minimal
    def load_collection(self, collection_name: str, **__) -> Dict[str, Any]:
        return self.select_collection(collection_name).get()

###############################################################################
# Section 2: Pytest fixtures
###############################################################################

@pytest.fixture(autouse=True)
def _silence_logging_and_print(monkeypatch):
    """Disable logging & monkey-patch print to keep test output clean."""
    logging.disable(logging.CRITICAL)
    monkeypatch.setattr("builtins.print", lambda *_, **__: None)
    yield
    logging.disable(logging.NOTSET)


@pytest.fixture(autouse=True)
def _patch_chroma_storage(monkeypatch):
    """Redirect any ChromaStorage look-ups to our in-memory stub."""

    # Patch both the canonical module and the copy imported inside Memory.
    import agentforge.storage.chroma_storage as cs_mod
    import agentforge.storage.memory as mem_mod

    monkeypatch.setattr(cs_mod, "ChromaStorage", FakeChromaStorage, raising=True)
    monkeypatch.setattr(mem_mod, "ChromaStorage", FakeChromaStorage, raising=True)
    yield
    # Registry & patch will disappear after fixture teardown automatically.


@pytest.fixture()
def isolated_config(tmp_path) -> Config:
    """Provide a *fresh* Config instance pointing at a temp `.agentforge` dir."""

    # Copy bundled defaults into an isolated temp directory
    project_root = tmp_path
    setup_src = Path(__file__).resolve().parent.parent / "src" / "agentforge" / "setup_files"
    shutil.copytree(setup_src, project_root / ".agentforge")

    # Reset the singleton so each test gets a brand-new config context
    cfg = Config.reset(root_path=str(project_root))
    yield cfg
    # Clean up after test – ensure no cross-contamination
    Config._instance = None

# ---------------------------------------------------------------------------
# Safety patch: Older Cog tests provide no `response_format`; upstream code had
# a `.lower()` call that crashes on `None`. We patch the helper to guard.
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _patch_cog_response_format(monkeypatch):
    from agentforge.cog import Cog

    def _safe_get(self: Cog, agent_def):  # type: ignore[override]
        resp = agent_def.get("response_format", self.default_response_format)
        if resp is None:
            return None
        return resp.lower()

    monkeypatch.setattr(Cog, "_get_response_format_for_agent", _safe_get, raising=True)
    yield

# ---------------------------------------------------------------------------
# Early monkeypatch: Make `agentforge.storage.chroma_storage.ChromaStorage` 
# resolve to our in-memory stub *before* tests (and their imports) run.
# ---------------------------------------------------------------------------

import types as _types

_stub_mod = _types.ModuleType("agentforge.storage.chroma_storage")
_stub_mod.ChromaStorage = None  # will be replaced after FakeChromaStorage defined
sys.modules["agentforge.storage.chroma_storage"] = _stub_mod 