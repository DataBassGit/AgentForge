"""Focused tests for AgentForge logging configuration and compatibility facade."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

import pytest
import yaml

from agentforge.config import Config
from agentforge.utils.logger import BaseLogger, Logger


CALLER_NAMES = {
    "RootOne",
    "RootTwo",
    "CwdAudit",
    "RepeatedName",
    "CategoryAudit",
    "ModelAudit",
    "DuplicateAudit",
    "DisabledAudit",
    "InvalidAudit",
}


@pytest.fixture(autouse=True)
def reset_logger_state():
    """Keep logger state isolated because Python logging is process-global."""
    logging.disable(logging.NOTSET)
    _clear_agentforge_logging_state()
    yield
    _clear_agentforge_logging_state()
    Config._instance = None
    logging.disable(logging.NOTSET)


def test_same_log_file_uses_active_project_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Two project roots using the same category should write to separate files."""
    root_one = _copy_agentforge_root(tmp_path, "project_one")
    root_two = _copy_agentforge_root(tmp_path, "project_two")

    monkeypatch.chdir(root_one)
    Config.reset(root_path=str(root_one))
    Logger("RootOne", "agentforge").warning("root-one warning")

    monkeypatch.chdir(root_two)
    Config.reset(root_path=str(root_two))
    Logger("RootTwo", "agentforge").warning("root-two warning")

    _flush_log_handlers()

    first_log = _read_log(root_one, "agentforge")
    second_log = _read_log(root_two, "agentforge")
    assert "root-one warning" in first_log
    assert "root-two warning" not in first_log
    assert "root-two warning" in second_log
    assert "root-one warning" not in second_log


def test_relative_log_folder_resolves_against_project_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """A relative logging.folder should be rooted at Config.project_root, not CWD."""
    root = _copy_agentforge_root(tmp_path, "project_root")
    runner_dir = tmp_path / "runner"
    runner_dir.mkdir()
    monkeypatch.chdir(runner_dir)

    Config.reset(root_path=str(root))
    Logger("CwdAudit", "agentforge").warning("root-relative warning")
    _flush_log_handlers()

    assert "root-relative warning" in _read_log(root, "agentforge")
    assert not (runner_dir / "logs" / "agentforge.log").exists()


def test_repeated_construction_does_not_ignore_default_logger(tmp_path: Path):
    """A repeated caller name can still use a different configured default logger."""
    root = _copy_agentforge_root(tmp_path, "project_root")
    _update_logging_settings(
        root, files={"agentforge": "debug", "model_io": "debug", "first_file": "debug", "second_file": "debug"}
    )
    Config.reset(root_path=str(root))

    first = Logger("RepeatedName", "first_file")
    second = Logger("RepeatedName", "second_file")
    first.warning("first-target warning")
    second.warning("second-target warning")
    _flush_log_handlers()

    first_log = _read_log(root, "first_file")
    second_log = _read_log(root, "second_file")
    assert "first-target warning" in first_log
    assert "second-target warning" not in first_log
    assert "second-target warning" in second_log


def test_unconfigured_category_falls_back_without_mutating_system_yaml(tmp_path: Path):
    """Unknown categories should use the fallback logger and leave consumer config untouched."""
    root = _copy_agentforge_root(tmp_path, "project_root")
    Config.reset(root_path=str(root))
    system_yaml = root / ".agentforge" / "settings" / "system.yaml"
    before = system_yaml.read_text(encoding="utf-8")

    Logger("CategoryAudit", "agentforge").log("flow debug survives", "debug", "Flow")
    _flush_log_handlers()

    assert system_yaml.read_text(encoding="utf-8") == before
    assert "flow debug survives" in _read_log(root, "agentforge")
    assert not (root / "logs" / "Flow.log").exists()


def test_configured_category_and_model_io_helpers_write_expected_files(tmp_path: Path):
    """Configured categories, prompt logging, and response logging remain supported."""
    root = _copy_agentforge_root(tmp_path, "project_root")
    Config.reset(root_path=str(root))
    logger = Logger("ModelAudit", "agentforge")

    logger.debug("agentforge debug message")
    logger.log_prompt({"system": "system prompt", "user": "user prompt"})
    logger.log_response("model response")
    _flush_log_handlers()

    assert "agentforge debug message" in _read_log(root, "agentforge")
    model_io_log = _read_log(root, "model_io")
    assert "system prompt" in model_io_log
    assert "user prompt" in model_io_log
    assert "model response" in model_io_log


def test_repeated_construction_does_not_duplicate_log_lines(tmp_path: Path):
    """Reusing the same facade should not attach duplicate handlers."""
    root = _copy_agentforge_root(tmp_path, "project_root")
    Config.reset(root_path=str(root))

    Logger("DuplicateAudit", "agentforge")
    Logger("DuplicateAudit", "agentforge").warning("single duplicate check")
    _flush_log_handlers()

    assert _read_log(root, "agentforge").count("single duplicate check") == 1


def test_disabled_logging_creates_no_log_files(tmp_path: Path):
    """When system logging is disabled, the facade should emit nothing."""
    root = _copy_agentforge_root(tmp_path, "project_root")
    _update_logging_settings(root, enabled=False)
    Config.reset(root_path=str(root))
    logger = Logger("DisabledAudit", "agentforge")

    logger.warning("disabled warning")
    logger.log_prompt({"system": "hidden", "user": "hidden"})
    _flush_log_handlers()

    log_dir = root / "logs"
    assert not log_dir.exists() or not list(log_dir.iterdir())


def test_invalid_log_level_raises_value_error(tmp_path: Path):
    """Invalid levels should fail at the logging boundary instead of becoming INFO."""
    root = _copy_agentforge_root(tmp_path, "project_root")
    Config.reset(root_path=str(root))
    logger = Logger("InvalidAudit", "agentforge")

    with pytest.raises(ValueError, match="Unsupported log level"):
        logger.log("bad level", level="verbose")


def _copy_agentforge_root(tmp_path: Path, name: str) -> Path:
    root = tmp_path / name
    setup_src = Path.cwd() / "src" / "agentforge" / "setup_files"
    shutil.copytree(setup_src, root / ".agentforge")
    return root


def _update_logging_settings(
    root: Path, *, enabled: bool | None = None, folder: str | None = None, files: dict[str, str] | None = None
) -> None:
    system_yaml = root / ".agentforge" / "settings" / "system.yaml"
    data = yaml.safe_load(system_yaml.read_text(encoding="utf-8"))
    logging_settings = data["logging"]
    if enabled is not None:
        logging_settings["enabled"] = enabled
    if folder is not None:
        logging_settings["folder"] = folder
    if files is not None:
        logging_settings["files"] = files
    system_yaml.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _read_log(root: Path, category: str) -> str:
    return (root / "logs" / f"{category}.log").read_text(encoding="utf-8")


def _flush_log_handlers() -> None:
    for logger in _iter_managed_loggers():
        for handler in logger.handlers:
            handler.flush()


def _clear_agentforge_logging_state() -> None:
    for handler in list(getattr(BaseLogger, "file_handlers", {}).values()):
        handler.close()
    for handler in list(getattr(BaseLogger, "console_handlers", {}).values()):
        handler.close()
    getattr(BaseLogger, "file_handlers", {}).clear()
    getattr(BaseLogger, "console_handlers", {}).clear()
    getattr(Logger, "_instances", {}).clear()

    for logger in _iter_managed_loggers():
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            handler.close()
        logger.setLevel(logging.NOTSET)
        logger.propagate = True


def _iter_managed_loggers() -> list[logging.Logger]:
    managed: list[logging.Logger] = []
    for name, value in logging.Logger.manager.loggerDict.items():
        if isinstance(value, logging.Logger) and _is_managed_logger(name):
            managed.append(value)
    return managed


def _is_managed_logger(name: str) -> bool:
    return name.startswith("agentforge") or any(caller_name in name for caller_name in CALLER_NAMES)
