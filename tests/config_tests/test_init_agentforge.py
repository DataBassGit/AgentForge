"""Tests for scaffolding a consumer project from packaged setup files."""

from __future__ import annotations

import importlib.machinery
import shutil
from pathlib import Path

import pytest

from agentforge import init_agentforge
from agentforge.config import Config


SETUP_SRC = Path(__file__).resolve().parents[2] / "src" / "agentforge" / "setup_files"


def _yaml_paths(root: Path) -> set[str]:
    return {path.relative_to(root).as_posix() for pattern in ("*.yaml", "*.yml") for path in root.rglob(pattern)}


EXPECTED_YAML_PATHS = _yaml_paths(SETUP_SRC)


def _project_yaml_paths(project_root: Path) -> set[str]:
    return _yaml_paths(project_root / ".agentforge")


def _use_fake_installed_package(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    package_root = tmp_path / "site-packages" / "agentforge"
    shutil.copytree(SETUP_SRC, package_root / "setup_files")
    spec = importlib.machinery.ModuleSpec("agentforge", loader=None, is_package=True)
    spec.submodule_search_locations = [str(package_root)]

    def find_spec(name: str, package: str | None = None) -> importlib.machinery.ModuleSpec | None:
        return spec if name == "agentforge" else None

    monkeypatch.setattr(init_agentforge.importlib.util, "find_spec", find_spec)
    return package_root


def test_setup_agentforge_scaffolds_packaged_yaml_and_root_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """The project scaffold should come from the installed package location."""
    _use_fake_installed_package(tmp_path, monkeypatch)
    project_root = tmp_path / "consumer_project"
    project_root.mkdir()
    monkeypatch.chdir(project_root)

    init_agentforge.setup_agentforge()

    assert len(EXPECTED_YAML_PATHS) == 42
    assert _project_yaml_paths(project_root) == EXPECTED_YAML_PATHS
    for relative_path in (
        "settings/system.yaml",
        "settings/models.yaml",
        "cogs/beginner_summary_cog.yaml",
        "prompts/beginner_response_agent.yaml",
        "prompts/beginner_summary_agent.yaml",
        "prompts/hello_agent.yaml",
        "prompts/response_agent.yaml",
        "cogs/example_cog.yaml",
        "tools/read_file.yaml",
        "actions/web_search.yaml",
        "personas/default_assistant.yaml",
    ):
        assert (project_root / ".agentforge" / relative_path).is_file()

    cfg = Config.reset(root_path=str(project_root))
    assert cfg.project_root == project_root
    assert cfg.find_config("cogs", "beginner_summary_cog")
    assert cfg.find_config("prompts", "hello_agent")
    assert cfg.find_config("prompts", "response_agent")

    monkeypatch.setenv("AGENTFORGE_ROOT", str(project_root))
    env_cfg = Config.reset()
    assert env_cfg.project_root == project_root
    assert env_cfg.find_config("cogs", "example_cog")


def test_setup_agentforge_rerun_skips_identical_files_without_prompt(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Running the scaffold command again should not prompt or rewrite identical files."""
    _use_fake_installed_package(tmp_path, monkeypatch)
    project_root = tmp_path / "consumer_project"
    project_root.mkdir()
    monkeypatch.chdir(project_root)

    init_agentforge.setup_agentforge()

    def fail_input(prompt: str = "") -> str:
        raise AssertionError("identical setup files should not prompt")

    def fail_copy2(src: str, dst: str) -> None:
        raise AssertionError("identical setup files should not be copied again")

    monkeypatch.setattr("builtins.input", fail_input)
    monkeypatch.setattr(init_agentforge.shutil, "copy2", fail_copy2)

    init_agentforge.setup_agentforge()

    assert _project_yaml_paths(project_root) == EXPECTED_YAML_PATHS
