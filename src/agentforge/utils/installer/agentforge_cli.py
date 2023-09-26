# agentforge_cli.py

import os
import shutil
import argparse
import pkg_resources
import glob


def copy_files():

    # Create directories
    os.makedirs(".agentforge", exist_ok=True)
    os.makedirs(".agentforge/agents", exist_ok=True)
    os.makedirs(".agentforge/personas", exist_ok=True)
    os.makedirs("customagents", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs(".agentforge/actions", exist_ok=True)
    os.makedirs(".agentforge/tools", exist_ok=True)

    # Create infrastructure files
    with open(os.path.join("logs", "results.txt"), "w") as f:
        f.write("Results log file\n")
    with open(os.path.join("customagents", "__init__.py"), "w") as f:
        f.write("Results log file\n")

    # Define core config files
    files_to_copy = [
        "config.json",
    ]

    # Copy core config files to .agentforge
    for file_name in files_to_copy:
        src_path = pkg_resources.resource_filename("agentforge.utils.installer", file_name)
        dest_path = os.path.join(".agentforge", file_name)
        shutil.copyfile(src_path, dest_path)

    # Copy all files from the agents subfolder in src_path to .agentforge/agents
    def copy_files_from_src_to_dest(src_folder, dest_folder):
        src_path = pkg_resources.resource_filename("agentforge.utils.installer", f"{src_folder}/*")
        for file_path in glob.glob(src_path):
            file_name = os.path.basename(file_path)
            dest_path = os.path.join(".agentforge", dest_folder, file_name)
            shutil.copyfile(file_path, dest_path)

    # Copy from the tools subfolder
    copy_files_from_src_to_dest("tools", "tools")

    # Copy from the actions subfolder
    copy_files_from_src_to_dest("actions", "actions")

    # Copy from the agents subfolder
    copy_files_from_src_to_dest("agents", "agents")

    # Copy personas/persona.json to .agentforge/personas
    personas_src_path = pkg_resources.resource_filename("agentforge.utils.installer", "personas/persona.json")
    personas_dest_path = os.path.join(".agentforge", "personas", "persona.json")
    shutil.copyfile(personas_src_path, personas_dest_path)

def copy_salience():
    src_path = pkg_resources.resource_filename("agentforge.utils.installer", "dyn.py")
    shutil.copyfile(src_path, "salience.py")

def main():
    parser = argparse.ArgumentParser(description="AgentForge CLI")
    parser.add_argument("command", choices=["init","salience"], help="The command to run")
    args = parser.parse_args()

    if args.command == "init":
        copy_files()
    elif args.command == "salience":
        copy_salience()

if __name__ == "__main__":
    main()
