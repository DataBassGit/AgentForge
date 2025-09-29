#!/usr/bin/env python3
"""Interactive script for testing Text-to-Speech with AgentForge.

Runs the *tts_agent* (defined in prompts/audio_agents/tts_agent.yaml) which
wraps the OpenAI TTS endpoint.  Provide text via --text or type interactively.
The agent returns the path where the generated WAV is saved.
"""

from agentforge.testing.bootstrap import bootstrap_test_env
# Ensure repo-root config and paths are patched before importing AgentForge
bootstrap_test_env(use_fakes=False, silence_output=False, cleanup_on_exit=True)

from dotenv import load_dotenv
load_dotenv()

from agentforge.agent import Agent  # noqa: E402 (after bootstrap)

import argparse

DEFAULT_SENTENCE = (
    "Hello from AgentForge! This sentence demonstrates the Text to Speech "
    "capabilities of the platform."
)


def main() -> None:  # noqa: D401
    parser = argparse.ArgumentParser(description="AgentForge TTS demo")
    parser.add_argument(
        "--text", metavar="STRING", help="Text to synthesise on first run"
    )
    args = parser.parse_args()

    tts_agent = Agent(agent_name="tts_agent")

    print(
        "TTS Agent ready – press <enter> for default text or type your own. "
        "Type 'quit' to exit."
    )

    while True:
        # Use --text only on first iteration
        if args.text is not None:
            text_input = args.text
            args.text = None
        else:
            user_in = input("Text to speak: ").strip()
            if user_in.lower() == "quit":
                print("Chao!")
                break
            text_input = user_in or DEFAULT_SENTENCE

        try:
            audio_path = tts_agent.run(text=text_input)
        except Exception as exc:
            print("ERROR:", exc)
            continue

        print("---------")
        print("Audio saved to:", audio_path)
        print("---------")


if __name__ == "__main__":
    main() 