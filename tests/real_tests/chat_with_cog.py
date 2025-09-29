#!/usr/bin/env python3
"""Simple chat script for testing PersonaMemory with installed AgentForge."""

from agentforge.testing.bootstrap import bootstrap_test_env
# Ensure the repo-root config and paths are in place *before* importing AgentForge
bootstrap_test_env(use_fakes=False, silence_output=False, cleanup_on_exit=True)

from dotenv import load_dotenv
from agentforge.cog import Cog
import os
# Load environment variables from .env file
load_dotenv()

def main():
    # cog_test = Cog('example_cog')
    # cog_test = Cog('example_cog_with_memory')
    cog_test = Cog('example_cog_with_chat_memory')
    # cog_test = Cog('example_cog_with_persona_memory')
    # cog_test = Cog('example_cog_with_scratchpad')
    # cog_test = Cog('example_cog_all_memories')
    
    print("Cog is awaiting your input...")
    while True:
        user_input: str = input("You: ")
        if user_input.lower() == 'quit':
            print("Chao!")
            break

        result = cog_test.run(user_input=user_input)
        flow = cog_test.get_track_flow_trail()
        print(f"---------")
        print(flow)
        print(f"---------")
        print(f"Assistant: {result}")
        print(f"---------")

if __name__ == "__main__":
    main()