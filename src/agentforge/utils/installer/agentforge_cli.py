# agentforge_cli.py

import os
import shutil
import argparse

def copy_files():
    os.makedirs(".agentforge", exist_ok=True)
    src_path = os.path.join("src", "agentforge", "utils", "installer", "actions.py")
    dest_path = os.path.join(".agentforge", "actions.py")
    shutil.copyfile(src_path, dest_path)

def main():
    parser = argparse.ArgumentParser(description="AgentForge CLI")
    parser.add_argument("command", choices=["copy_files"], help="The command to run")
    args = parser.parse_args()

    if args.command == "init":
        copy_files()

if __name__ == "__main__":
    main()
