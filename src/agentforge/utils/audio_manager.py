from __future__ import annotations

"""Audio utilities for saving / playing TTS output.

This module centralises all logic previously embedded in ``Agent._route_audio_save``.
"""

import datetime
import os
import pathlib
import platform
import subprocess
import tempfile
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from agentforge.config_structs.agent_config_structs import AgentConfig
    from agentforge.utils.logger import Logger

__all__ = ["AudioManager"]


class AudioManager:
    """Encapsulate audio-file persistence and optional auto-play behaviour."""

    def __init__(self, agent_config: "AgentConfig", logger: "Logger") -> None:
        self.agent_config = agent_config
        self.logger = logger

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def save_tts_bytes(self, blob: bytes, fmt: str = "wav") -> str:
        """Persist *blob* to disk according to system audio settings.

        The returned value is the absolute path to the written file.
        """
        cfg_sys = self.agent_config.settings.system
        audio_cfg = getattr(cfg_sys, "audio", None)

        # Determine whether to save outside tmp
        save_enabled: bool = getattr(audio_cfg, "save_files", False) if audio_cfg else False

        # Resolve fallback directory from `paths.audio` when explicit save_dir missing
        cfg_paths = getattr(cfg_sys, "paths", {})
        default_dir = (
            cfg_paths.get("audio") if isinstance(cfg_paths, dict) else getattr(cfg_paths, "audio", None)
        )

        base_dir: str
        if save_enabled:
            base_dir = (getattr(audio_cfg, "save_dir", "") or default_dir or tempfile.gettempdir())
        else:
            # Always need to write *somewhere* to give the caller a path
            base_dir = tempfile.gettempdir()

        pathlib.Path(base_dir).mkdir(parents=True, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        file_path = os.path.join(base_dir, f"tts_{timestamp}.{fmt}")

        with open(file_path, "wb") as fp:
            fp.write(blob)

        if getattr(audio_cfg, "autoplay", False):
            self._autoplay(file_path)

        return file_path

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _autoplay(self, file_path: str) -> None:
        """Attempt to play the audio in a non-blocking way using platform tools."""
        try:
            system = platform.system()
            if system == "Darwin":
                subprocess.Popen(["afplay", file_path])
            elif system == "Linux":
                for cmd in (
                    ["paplay", file_path],
                    ["aplay", file_path],
                    ["ffplay", "-nodisp", "-autoexit", file_path],
                ):
                    try:
                        subprocess.Popen(cmd)
                        break
                    except FileNotFoundError:
                        continue
            # Windows / unknown — no-op
        except Exception as exc:  # pragma: no cover – best-effort only
            self.logger.warning(f"Auto-play failed: {exc}") 