import argparse
import sys
from setup import __version__

def main():
    """
    Main entry point for the AgentForge CLI.
    """
    parser = argparse.ArgumentParser(description="AgentForge CLI")
    parser.add_argument(
        "--version", "-v", action="store_true", help="Show the current version of AgentForge"
    )
    args = parser.parse_args()

    if args.version:
        print(f"AgentForge version {__version__}")
        sys.exit(0)
