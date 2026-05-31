"""AgentForge logging facade backed by Python's standard logging module."""

from __future__ import annotations

import hashlib
import logging
import re
import threading
from pathlib import Path
from typing import Any, ClassVar

from agentforge.config import Config


LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}
VALID_LOGGER_NAME_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")
FILE_FORMAT = "%(asctime)s - %(levelname)s - %(message)s\n-------------------------------------------------------------"
CONSOLE_FORMAT = "%(levelname)s: %(message)s"


def encode_msg(msg: str) -> str:
    """Encode a message to UTF-8, replacing invalid characters."""
    return msg.encode("utf-8", "replace").decode("utf-8")


class ColoredFormatter(logging.Formatter):
    """Add ANSI colors to console logs by level."""

    COLOR_CODES: ClassVar[dict[int, str]] = {
        logging.DEBUG: "\033[36m",
        logging.INFO: "\033[32m",
        logging.WARNING: "\033[33m",
        logging.ERROR: "\033[31m",
        logging.CRITICAL: "\033[41m",
    }
    RESET_CODE = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color_code = self.COLOR_CODES.get(record.levelno, self.RESET_CODE)
        return f"{color_code}{super().format(record)}{self.RESET_CODE}"


class BaseLogger:
    """Compatibility wrapper that owns handler setup for one configured log category."""

    file_handlers: ClassVar[dict[Path, logging.FileHandler]] = {}
    console_handlers: ClassVar[dict[str, logging.StreamHandler]] = {}
    _handler_lock: ClassVar[threading.Lock] = threading.Lock()

    def __init__(self, name: str = "BaseLogger", log_file: str = "default.log", log_level: str = "error") -> None:
        self.config = Config()
        self.log_file = log_file
        category = Path(log_file).stem
        self.logger = logging.getLogger(_build_logger_name(self.config.project_root, name, category))
        self.logger.propagate = False

        logging_settings = self.config.settings.system.logging
        if not logging_settings.enabled:
            self.logger.disabled = True
            return

        self.logger.disabled = False
        file_level = _get_level_code(log_level)
        console_level = _get_level_code(logging_settings.console_level)
        self.logger.setLevel(min(file_level, console_level))
        log_file_path = _resolve_log_path(self.config.project_root, logging_settings.folder, log_file)
        self._setup_file_handler(log_file_path, file_level)
        self._setup_console_handler(console_level)

    @staticmethod
    def _get_level_code(level: str) -> int:
        """Return a standard logging level code or raise for invalid input."""
        return _get_level_code(level)

    def _setup_file_handler(self, log_file_path: Path, level: int) -> None:
        formatter = logging.Formatter(FILE_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
        resolved_path = log_file_path.resolve()

        with self._handler_lock:
            handler = self.file_handlers.get(resolved_path)
            if handler is None:
                resolved_path.parent.mkdir(parents=True, exist_ok=True)
                handler = logging.FileHandler(resolved_path, encoding="utf-8")
                self.file_handlers[resolved_path] = handler

            handler.setLevel(level)
            handler.setFormatter(formatter)
            if handler not in self.logger.handlers:
                self.logger.addHandler(handler)

    def _setup_console_handler(self, level: int) -> None:
        formatter = ColoredFormatter(CONSOLE_FORMAT)

        with self._handler_lock:
            handler = self.console_handlers.get(self.logger.name)
            if handler is None:
                handler = logging.StreamHandler()
                self.console_handlers[self.logger.name] = handler

            handler.setLevel(level)
            handler.setFormatter(formatter)
            if handler not in self.logger.handlers:
                self.logger.addHandler(handler)

    def log_msg(self, msg: str, level: str = "info") -> None:
        """Log a message at the requested level."""
        self.logger.log(self._get_level_code(level), msg)

    def set_level(self, level: str) -> None:
        """Set this logger and all attached handlers to the requested level."""
        level_code = self._get_level_code(level)
        self.logger.setLevel(level_code)
        for handler in self.logger.handlers:
            handler.setLevel(level_code)


class Logger:
    """Compatibility facade for AgentForge logging categories and model I/O helpers."""

    _instances: ClassVar[dict[tuple[str, str, str], "Logger"]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()
    VALID_LOGGER_NAME_PATTERN = VALID_LOGGER_NAME_PATTERN

    def __new__(cls, name: str, default_logger: str = "agentforge"):
        config = Config()
        normalized_default = default_logger or "agentforge"
        key = (str(config.project_root.resolve()), name, normalized_default)
        with cls._lock:
            instance = cls._instances.get(key)
            if instance is None:
                instance = super().__new__(cls)
                instance._initialized = False
                cls._instances[key] = instance
        return instance

    def __init__(self, name: str, default_logger: str = "agentforge") -> None:
        if self._initialized:
            return

        with self._lock:
            if self._initialized:
                return
            self.config = Config()
            self.caller_name = name
            self.default_logger = default_logger or "agentforge"
            self.logging_config: dict[str, str] = {}
            self.logging_enabled = True
            self.loggers: dict[str, BaseLogger] = {}
            self.load_logging_config()
            self.update_logger_config(self.default_logger)
            self.init_loggers()
            self._initialized = True

    def load_logging_config(self) -> None:
        """Load configured logging categories from system settings."""
        settings = self.config.settings.system.logging
        self.logging_enabled = settings.enabled
        self.logging_config = dict(settings.files or {})

    def update_logger_config(self, logger_file: str) -> None:
        """Validate a logger category without mutating consumer configuration."""
        _validate_logger_category(logger_file)

    def init_loggers(self) -> None:
        """Initialize standard loggers for configured categories only."""
        self.loggers = {}
        if not self.logging_enabled:
            return
        for logger_file, log_level in self.logging_config.items():
            self.create_logger(logger_file, log_level)

    def create_logger(self, logger_file: str, log_level: str = "warning") -> None:
        """Create or refresh a logger for a configured category."""
        _validate_logger_category(logger_file)
        self.loggers[logger_file] = BaseLogger(
            name=self.caller_name, log_file=f"{logger_file}.log", log_level=log_level
        )

    def log(self, msg: str, level: str = "info", logger_file: str | None = None) -> None:
        """Log a message through the requested category or configured fallback."""
        _get_level_code(level)
        if not self.logging_enabled:
            return

        target_logger = self._resolve_logger(logger_file)
        if target_logger is None:
            return

        msg_with_caller = f"[{self.caller_name}] {encode_msg(str(msg))}"
        target_logger.log_msg(msg_with_caller, level)

    def debug(self, msg: str, logger_file: str | None = None) -> None:
        """Log a debug message."""
        self.log(msg, level="debug", logger_file=logger_file)

    def info(self, msg: str, logger_file: str | None = None) -> None:
        """Log an info message."""
        self.log(msg, level="info", logger_file=logger_file)

    def warning(self, msg: str, logger_file: str | None = None) -> None:
        """Log a warning message."""
        self.log(msg, level="warning", logger_file=logger_file)

    def error(self, msg: str, logger_file: str | None = None) -> None:
        """Log an error message."""
        self.log(msg, level="error", logger_file=logger_file)

    def critical(self, msg: str, logger_file: str | None = None) -> None:
        """Log a critical message."""
        self.log(msg, level="critical", logger_file=logger_file)

    def log_prompt(self, model_prompt: dict[str, Any]) -> None:
        """Log a model prompt to the model I/O category."""
        system_prompt = model_prompt.get("system", "")
        user_prompt = model_prompt.get("user", "")
        msg = f"******\nSystem Prompt\n******\n{system_prompt}\n******\nUser Prompt\n******\n{user_prompt}\n******"
        self.debug(msg, logger_file="model_io")

    def log_response(self, response: str) -> None:
        """Log a model response to the model I/O category."""
        self.debug(f"******\nModel Response\n******\n{response}\n******", logger_file="model_io")

    def parsing_error(self, model_response: str, error: Exception) -> None:
        """Log parsing failures with the model response that failed to parse."""
        msg = (
            "Parsing Error - The model may not have responded in the required format.\n\n"
            f"Model Response:\n******\n{model_response}\n******\n\nError: {error}"
        )
        self.error(msg)

    def _resolve_logger(self, logger_file: str | None) -> BaseLogger | None:
        requested_logger = logger_file or self.default_logger
        _validate_logger_category(requested_logger)
        if requested_logger in self.loggers:
            return self.loggers[requested_logger]

        fallback_logger = self._fallback_logger_name()
        return self.loggers.get(fallback_logger) if fallback_logger else None

    def _fallback_logger_name(self) -> str | None:
        if self.default_logger in self.loggers:
            return self.default_logger
        if "agentforge" in self.loggers:
            return "agentforge"
        return next(iter(self.loggers), None)


def _get_level_code(level: str) -> int:
    normalized_level = level.lower()
    if normalized_level not in LOG_LEVELS:
        valid_levels = ", ".join(LOG_LEVELS)
        raise ValueError(f"Unsupported log level '{level}'. Expected one of: {valid_levels}.")
    return LOG_LEVELS[normalized_level]


def _validate_logger_category(logger_file: str) -> None:
    if not logger_file or not VALID_LOGGER_NAME_PATTERN.match(logger_file):
        raise ValueError(
            f"Invalid logger_file name: '{logger_file}'. Must match pattern: {VALID_LOGGER_NAME_PATTERN.pattern}"
        )


def _resolve_log_path(project_root: Path, log_folder: str, log_file: str) -> Path:
    folder_path = Path(log_folder).expanduser()
    if not folder_path.is_absolute():
        folder_path = project_root / folder_path
    return folder_path / log_file


def _build_logger_name(project_root: Path, caller_name: str, category: str) -> str:
    root_token = hashlib.sha1(str(project_root.resolve()).encode("utf-8")).hexdigest()[:12]
    return f"agentforge.{root_token}.{_safe_logger_segment(caller_name)}.{_safe_logger_segment(category)}"


def _safe_logger_segment(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", value).strip("._") or "unnamed"
