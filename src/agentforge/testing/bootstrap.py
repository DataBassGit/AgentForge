from __future__ import annotations

"""Reusable test-environment bootstrapper.

This helper centralises the one-off environment side-effects that used to live
at *tests/conftest.py*.  Call ``bootstrap_test_env`` early in your script or
fixture to reproduce the same path manipulations, config patches, and optional
in-memory fakes.
"""

import atexit
import logging
import os
import shutil
import sys
from pathlib import Path
from types import ModuleType
import builtins
from typing import Optional

__all__ = ["bootstrap_test_env"]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _discover_repo_root() -> Path:
    """Walk up the filesystem until we find a directory that looks like the
    project root (contains both *src* and *tests* directories).  Fallback to
    ``Path.cwd()`` if we run out of parents.
    """
    cur = Path(__file__).resolve()
    for parent in cur.parents:
        if (parent / "src").is_dir() and (parent / "tests").is_dir():
            return parent
    return Path.cwd()


def _ensure_src_on_path(repo_root: Path) -> None:
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


# ---------------------------------------------------------------------------
# Public bootstrap
# ---------------------------------------------------------------------------

def bootstrap_test_env(
    *,
    use_fakes: bool = True,
    silence_output: bool = True,
    cleanup_on_exit: bool = True,
) -> None:
    """Replicate the critical test harness tweaks on demand.

    Parameters
    ----------
    use_fakes
        When *True*, replace ChromaStorage back-ends with the in-memory
        ``FakeChromaStorage`` implementation and stub out ``Agent.run`` so no
        network / LLM calls occur.  When *False*, leave production behaviour
        untouched.

    silence_output
        When *True*, disable *logging* below *CRITICAL* and monkey-patch the
        built-in ``print`` to a no-op.  Restored automatically at process
        exit.

    cleanup_on_exit
        Delete the *repo-root/.agentforge* directory that this helper creates
        (only if we created it) when the interpreter shuts down.
    """

    # Early exit if we have already bootstrapped in the desired mode ------------
    if getattr(bootstrap_test_env, "_has_run", False):  # type: ignore[attr-defined]
        # Second call may request stricter settings (e.g. silence_output=True)
        # – honour those upgrades, but never downgrade (once silenced, stay
        # silenced; once fakes are active, stay faked).
        prev_use_fakes = getattr(bootstrap_test_env, "_use_fakes", False)  # type: ignore[attr-defined]
        prev_silence_output = getattr(bootstrap_test_env, "_silence", False)  # type: ignore[attr-defined]
        if use_fakes and not prev_use_fakes:
            raise RuntimeError("bootstrap_test_env(): fakes were previously disabled; cannot enable them later")
        if silence_output and not prev_silence_output:
            _silence_stdout()
            setattr(bootstrap_test_env, "_silence", True)  # type: ignore[attr-defined]
        return

    # ---------------------------------------------------------------------
    repo_root = _discover_repo_root()
    os.chdir(repo_root)
    _ensure_src_on_path(repo_root)

    # Patch Config root resolution so tests & scripts load config relative to repo
    try:
        import agentforge.config as _afcfg  # pylint: disable=import-error

        def _fixed_find_project_root(self, _root_path: Optional[str] = None):  # noqa: D401
            return repo_root

        _afcfg.Config.find_project_root = _fixed_find_project_root  # type: ignore[assignment]
    except ImportError:
        # AgentForge not importable yet – ignore; caller is likely installing
        # dependencies.
        pass

    # Ensure a .agentforge directory exists at repo root -------------------
    default_af = repo_root / ".agentforge"
    created_dot_agentforge = False
    if not default_af.exists():
        setup_src = repo_root / "src" / "agentforge" / "setup_files"
        shutil.copytree(setup_src, default_af)
        created_dot_agentforge = True

    # Activate fakes --------------------------------------------------------
    if use_fakes:
        try:
            from tests.utils.fakes import FakeChromaStorage  # type: ignore
            import agentforge.storage.chroma_storage as cs_mod  # noqa: E402
            import agentforge.storage.memory as mem_mod  # noqa: E402

            cs_mod.ChromaStorage = FakeChromaStorage  # type: ignore[attr-defined]
            mem_mod.ChromaStorage = FakeChromaStorage  # type: ignore[attr-defined]

            # Convenience alias expected by some tests
            setattr(FakeChromaStorage, "create_collection", FakeChromaStorage.select_collection)

            # Stub Agent.run so no LLM calls hit external services ------------
            from agentforge.agent import Agent  # noqa: E402

            _orig_run = Agent.run  # type: ignore[assignment]
            _decisions = ("approve", "reject", "other")

            def _fake_run(self: "Agent", **context):  # type: ignore[override]
                # Allow opt-out via debug flag
                if getattr(self, "settings", {}).get("system", {}).get("debug", {}).get("mode", False):
                    return _orig_run(self, **context)

                if hasattr(self, "_cog") and hasattr(self._cog, "branch_call_counts"):
                    self._cog.branch_call_counts[self.agent_name] = (
                        self._cog.branch_call_counts.get(self.agent_name, 0) + 1
                    )

                name_l = self.agent_name.lower()
                if "analyze" in name_l:
                    return {"analysis": "stub-analysis"}
                if "decide" in name_l:
                    idx = getattr(self, "_call_idx", 0)
                    self._call_idx = idx + 1
                    return {"choice": _decisions[idx % len(_decisions)], "rationale": "stub"}
                if "response" in name_l or "respond" in name_l:
                    return "FINAL RESPONSE"
                if "understand" in name_l:
                    return {
                        "insights": "User is asking about programming topics",
                        "user_intent": "Seeking information or help",
                        "relevant_topics": ["programming", "learning"],
                        "persona_relevant": "User shows interest in technical topics",
                    }
                if "test" in name_l:
                    return _orig_run(self, **context)
                return f"Simulated response from {self.agent_name}"

            Agent.run = _fake_run  # type: ignore[assignment]
        except Exception:  # pragma: no cover – tests will surface issues
            if use_fakes:
                raise

    # Silence output if requested -----------------------------------------
    if silence_output:
        _silence_stdout()

    # Register cleanup -----------------------------------------------------
    if cleanup_on_exit:
        def _cleanup():  # noqa: D401
            if silence_output:
                logging.disable(logging.NOTSET)
                if hasattr(builtins, "__orig_print"):
                    builtins.print = builtins.__orig_print  # type: ignore[attr-defined]
                    del builtins.__orig_print  # type: ignore[attr-defined]
            if created_dot_agentforge and default_af.exists():
                shutil.rmtree(default_af, ignore_errors=True)
        atexit.register(_cleanup)

    # Record that we have run so subsequent calls don't redo work ----------
    setattr(bootstrap_test_env, "_has_run", True)  # type: ignore[attr-defined]
    setattr(bootstrap_test_env, "_use_fakes", use_fakes)  # type: ignore[attr-defined]
    setattr(bootstrap_test_env, "_silence", silence_output)  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _silence_stdout() -> None:  # noqa: D401 – helper, not public API
    logging.disable(logging.CRITICAL)
    if not hasattr(builtins, "__orig_print"):
        builtins.__orig_print = builtins.print  # type: ignore[attr-defined]
    builtins.print = lambda *args, **kwargs: None


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    bootstrap_test_env(use_fakes=True, silence_output=True, cleanup_on_exit=True) 