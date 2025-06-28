#!/usr/bin/env python3
"""Simple chat script for testing Audio with installed AgentForge."""

from agentforge.testing.bootstrap import bootstrap_test_env
# Ensure the repo-root config and paths are in place *before* importing AgentForge
bootstrap_test_env(use_fakes=False, silence_output=False, cleanup_on_exit=True)

from dotenv import load_dotenv
from agentforge.agent import Agent
import os
# Load environment variables from .env file
load_dotenv()

def main():
    audio_agent = Agent(agent_name='audio_agent')

    print("Audio Agent is awaiting your input...")
    while True:
        user_input: str = input("You: ")
        if user_input.lower() == 'quit':
            print("Chao!")
            break

        # result = audio_agent.run(audio=user_input)

        print(f"---------")
        # print(f"Audio Agent: {result}")
        print(f"---------")

if __name__ == "__main__":
    main()