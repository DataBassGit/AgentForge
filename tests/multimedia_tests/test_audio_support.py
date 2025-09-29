import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

# Ensure src/ is on path – conftest.bootstrap already does this, but add
SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from agentforge.apis.base_api import BaseModel, UnsupportedModalityError  # noqa: E402
from agentforge.apis.mixins.audio_input_mixin import AudioInputMixin  # noqa: E402
from agentforge.apis.mixins.audio_output_mixin import AudioOutputMixin  # noqa: E402
from agentforge.apis.openai_api import STT, TTS  # noqa: E402
from agentforge.agent import Agent  # noqa: E402
from agentforge.config import Config  # noqa: E402
from agentforge.core.config_manager import ConfigManager  # noqa: E402

###############################################################################
# 1. Mix-in capability flags
###############################################################################


def test_audio_mixins_flags():
    class DummyIn(AudioInputMixin, BaseModel):
        pass

    class DummyOut(AudioOutputMixin, BaseModel):
        pass

    assert DummyIn("m").supported_modalities == {"text", "audio"}
    assert DummyOut("m").supported_modalities == {"text", "audio"}

###############################################################################
# 2. BaseModel rejects audio when unsupported
###############################################################################


def test_base_model_rejects_audio(monkeypatch):
    model = BaseModel("test-model")

    # Avoid needing a real prompt
    monkeypatch.setattr(model, "_prepare_prompt", lambda mp: [])

    with pytest.raises(UnsupportedModalityError):
        model.generate({}, audio=b"1234")

###############################################################################
# 3. STT wrapper (mocked OpenAI Whisper)
###############################################################################


def test_stt_wrapper(monkeypatch):
    """STT.generate should return the transcription string when backend succeeds."""

    # Prepare fake response object
    dummy_resp = SimpleNamespace(text="hello world")

    # Patch OpenAI client method used by STT
    import agentforge.apis.openai_api as oai  # noqa: WPS433 – test import

    # Ensure .audio.transcriptions.create exists & returns dummy_resp
    audio_ns = SimpleNamespace(transcriptions=SimpleNamespace(create=MagicMock(return_value=dummy_resp)))
    monkeypatch.setattr(oai.client, "audio", audio_ns, raising=True)

    stt = STT("whisper-1")
    out = stt.generate({"system": "", "user": ""}, audio=b"\x00\x01")
    assert out == "hello world"
    audio_ns.transcriptions.create.assert_called_once()

###############################################################################
# 4. TTS wrapper (mocked OpenAI TTS)
###############################################################################


def test_tts_wrapper(monkeypatch):
    """TTS.generate should return raw bytes when backend succeeds."""

    fake_bytes = b"FAKEBYTES"
    dummy_resp = SimpleNamespace(content=fake_bytes)

    import agentforge.apis.openai_api as oai  # noqa: WPS433 – test import

    speech_ns = SimpleNamespace(create=MagicMock(return_value=dummy_resp))
    audio_ns = SimpleNamespace(speech=speech_ns)
    monkeypatch.setattr(oai.client, "audio", audio_ns, raising=True)

    tts = TTS("tts-1")
    out = tts.generate({"system": "", "user": "hello"})

    assert isinstance(out, (bytes, bytearray))
    assert out == fake_bytes
    speech_ns.create.assert_called_once()

###############################################################################
# 5. Agent helper for saving audio
###############################################################################


def _build_dummy_agent_config(isolated_config: Config):
    """Return minimal AgentConfig with debug enabled."""
    cm = ConfigManager()
    raw = {
        "name": "AudioAgent",
        "params": {},
        "prompts": {"system": "", "user": ""},
        "model": object(),
        "settings": isolated_config.data["settings"].copy(),
        "simulated_response": "SIMULATED",
    }
    raw["settings"]["system"]["debug"]["mode"] = True
    return cm.build_agent_config(raw)


@pytest.mark.usefixtures("isolated_config")
def test_audio_manager_save(tmp_path, monkeypatch, isolated_config):
    """AudioManager.save_tts_bytes should persist bytes and return path."""

    dummy_cfg = _build_dummy_agent_config(isolated_config)

    # Patch Config.load_agent_data so Agent init is lightweight
    monkeypatch.setattr(Config, "load_agent_data", lambda _self, _name: dummy_cfg, raising=True)

    agent = Agent("AudioAgent")

    # Configure audio settings for this test
    dummy_cfg.settings.system.audio.save_files = True
    dummy_cfg.settings.system.audio.save_dir = str(tmp_path)
    dummy_cfg.settings.system.audio.autoplay = False

    file_path = agent.audio_manager.save_tts_bytes(b"12345", fmt="wav")
    assert Path(file_path).exists(), "Audio file was not written"
    assert Path(file_path).read_bytes() == b"12345"

    # Clean up
    Path(file_path).unlink(missing_ok=True) 