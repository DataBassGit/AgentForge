from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from agentforge.apis.base_api import BaseModel, UnsupportedModalityError
from agentforge.apis.mixins.audio_input_mixin import AudioInputMixin
from agentforge.apis.mixins.audio_output_mixin import AudioOutputMixin
from agentforge.apis.openai_api import STT, TTS
from agentforge.agent import Agent
from agentforge.config import Config
from agentforge.core.config_manager import ConfigManager
from agentforge.utils.discord.discord_voice import DiscordVoice

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

    with pytest.raises(UnsupportedModalityError, match="requested modality 'audio'.*Supported modalities: text"):
        model.generate({}, audio=b"1234")


###############################################################################
# 3. STT wrapper (mocked OpenAI Whisper)
###############################################################################


def test_stt_wrapper(monkeypatch):
    """STT.generate should return the transcription string when backend succeeds."""

    # Prepare fake response object
    dummy_resp = SimpleNamespace(text="hello world")

    # Patch runtime client factory used by STT
    audio_ns = SimpleNamespace(transcriptions=SimpleNamespace(create=MagicMock(return_value=dummy_resp)))
    client_ns = SimpleNamespace(audio=audio_ns)
    monkeypatch.setattr(
        "agentforge.apis.openai_runtime.OpenAIRuntime._get_sdk_client", lambda _self: client_ns, raising=True
    )

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

    speech_ns = SimpleNamespace(create=MagicMock(return_value=dummy_resp))
    audio_ns = SimpleNamespace(speech=speech_ns)
    client_ns = SimpleNamespace(audio=audio_ns)
    monkeypatch.setattr(
        "agentforge.apis.openai_runtime.OpenAIRuntime._get_sdk_client", lambda _self: client_ns, raising=True
    )

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
        "settings": isolated_config.data.get("settings", {}).copy(),
        "simulated_response": "SIMULATED",
    }
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

    assert agent.audio_manager is not None
    file_path = agent.audio_manager.save_tts_bytes(b"12345", fmt="wav")
    assert Path(file_path).exists(), "Audio file was not written"
    assert Path(file_path).read_bytes() == b"12345"

    # Clean up
    Path(file_path).unlink(missing_ok=True)


###############################################################################
# 6. Discord voice FFmpeg command
###############################################################################


def test_discord_voice_ffmpeg_command_preserves_conversion_args(monkeypatch):
    """DiscordVoice should pass the expected in-memory conversion command to FFmpeg."""
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return SimpleNamespace(stdout=b"WAV")

    monkeypatch.setattr("agentforge.utils.discord.discord_voice.subprocess.run", fake_run)

    wav_bytes = DiscordVoice.create_wav_from_pcm(b"PCM", src_rate=44100, src_channels=1)

    assert wav_bytes == b"WAV"
    assert calls == [
        (
            [
                "ffmpeg",
                "-y",
                "-loglevel",
                "error",
                "-f",
                "s16le",
                "-ar",
                "44100",
                "-ac",
                "1",
                "-i",
                "pipe:0",
                "-ar",
                "16000",
                "-ac",
                "1",
                "-f",
                "wav",
                "pipe:1",
            ],
            {"input": b"PCM", "capture_output": True, "check": True, "timeout": 10},
        )
    ]
