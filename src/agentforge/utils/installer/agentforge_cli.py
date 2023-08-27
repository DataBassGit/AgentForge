# agentforge_cli.py

import os
import shutil
import argparse
import pkg_resources

def copy_files():
    os.makedirs(".agentforge", exist_ok=True)
    os.makedirs("Logs", exist_ok=True)

    with open(os.path.join("Logs", "results.txt"), "w") as f:
        f.write("Results log file\n")

    files_to_copy = [
        "actions.json",
        "config.ini",
        "default.json",
        "tools.json",
    ]

    for file_name in files_to_copy:
        src_path = pkg_resources.resource_filename("agentforge.utils.installer", file_name)
        dest_path = os.path.join(".agentforge", file_name)
        shutil.copyfile(src_path, dest_path)

def copy_salience():
    src_path = pkg_resources.resource_filename("agentforge.utils.installer", "salience.py")
    shutil.copyfile(src_path, "salience.py")

def main():
    parser = argparse.ArgumentParser(description="AgentForge CLI")
    parser.add_argument("command", choices=["init"], help="The command to run")
    args = parser.parse_args()

    if args.command == "init":
        copy_files()
    if args.command == "salience":
        copy_salience()

if __name__ == "__main__":
    main()
