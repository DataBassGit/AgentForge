#!/usr/bin/env python3
"""Simple chat script for testing Audio with installed AgentForge."""

from agentforge.testing.bootstrap import bootstrap_test_env
import argparse
import pathlib
import tempfile
import urllib.request

from dotenv import load_dotenv
from agentforge.agent import Agent
import os

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fetch_sample_audio() -> str:
    """Return the path to the bundled sample *voice-sample.wav*.

    The file lives in ``tests/real_tests/audio_samples`` so the repo can run
    fully offline.  Raises *FileNotFoundError* if the clip cannot be located.
    """

    sample_path = pathlib.Path(__file__).parent / "audio_samples" / "voice-sample.wav"
    if not sample_path.exists():
        raise FileNotFoundError(
            "Bundled audio sample not found at " f"{sample_path}. Please add a WAV file or use --file."
        )
    return str(sample_path)

# ---------------------------------------------------------------------------

# Ensure the repo-root config and paths are in place *before* importing AgentForge
bootstrap_test_env(use_fakes=False, silence_output=False, cleanup_on_exit=True)

# Load environment variables from .env file (for OPENAI_API_KEY, etc.)
load_dotenv()

def main() -> None:  # noqa: D401
    """Interactive CLI for testing Speech-to-Text via *audio_agent*."""

    parser = argparse.ArgumentParser(description="AgentForge STT demo")
    parser.add_argument(
        "--file",
        metavar="PATH",
        help="Path to an audio file to transcribe (default: download sample)",
    )
    args = parser.parse_args()

    audio_agent = Agent(agent_name="stt_agent")

    print("STT Agent is ready - press <enter> to use the bundled sample clip or provide a file path. Type 'quit' to exit.")

    while True:
        # Consume any --file value only on first loop ----------------------
        if args.file:
            audio_path = args.file
            args.file = None  # use only once
        else:
            user_in = input("STT Agent: Audio path (blank for sample): ").strip()
            if user_in.lower() == "quit":
                print("Chao!")
                break
            audio_path = user_in or _fetch_sample_audio()

        # Run STT ----------------------------------------------------------
        try:
            transcript = audio_agent.run(audio=audio_path)
        except Exception as exc:
            print("ERROR:", exc)
            transcript = None

        print("---------")
        print("Transcription:", transcript)
        print("---------")

if __name__ == "__main__":
    main()