# agentforge_cli.py

import os
import shutil
import argparse
import pkg_resources
import glob
import subprocess
import sys


def display_custom_help():
    help_message = """
Available commands for AgentForge:

init       - Copy necessary files and set up directories.
salience   - Copy the salience.py file.
gui        - Launch the graphical user interface.

For more details on each command, use 'agentforge <command> -h'
"""
    print(help_message)


def copy_files():

    # Create directories
    os.makedirs(".agentforge", exist_ok=True)
    os.makedirs(".agentforge/agents", exist_ok=True)
    os.makedirs(".agentforge/agents/PredefinedAgents", exist_ok=True)
    os.makedirs(".agentforge/actions", exist_ok=True)
    os.makedirs(".agentforge/personas", exist_ok=True)
    os.makedirs(".agentforge/settings", exist_ok=True)
    os.makedirs(".agentforge/tools", exist_ok=True)
    os.makedirs("CustomAgents", exist_ok=True)
    os.makedirs("Logs", exist_ok=True)

    # Create infrastructure files
    with open(os.path.join("CustomAgents", "__init__.py"), "w") as f:
        f.write("")
    with open(os.path.join("Logs", "results.txt"), "w") as f:
        f.write("Results Log File:\n")


    print("All files have been successfully copied!")

    copy_files_from_src_to_dest("tools", "tools")
    copy_files_from_src_to_dest("actions", "actions")
    copy_files_from_src_to_dest("agents", "agents/PredefinedAgents")
    copy_files_from_src_to_dest("settings", "settings")

    # Copy personas/default.yaml to .agentforge/personas
    personas_src_path = pkg_resources.resource_filename("agentforge.utils.installer", "personas/default.yaml")
    personas_dest_path = os.path.join(".agentforge", "personas", "default.yaml")
    shutil.copyfile(personas_src_path, personas_dest_path)


# Copy all files from the agents subfolder in src_path to .agentforge/agents
def copy_files_from_src_to_dest(src_folder, dest_folder):
    src_path = pkg_resources.resource_filename("agentforge.utils.installer", f"{src_folder}/*")
    for file_path in glob.glob(src_path):
        file_name = os.path.basename(file_path)
        dest_path = os.path.join(".agentforge", dest_folder, file_name)
        shutil.copyfile(file_path, dest_path)


def copy_salience():
    src_path = pkg_resources.resource_filename("agentforge.utils.installer", "salience.py")
    shutil.copyfile(src_path, "salience.py")
    print("Salience.py has been successfully copied!\n")


def gui():
    gui_path = pkg_resources.resource_filename("agentforge.utils.guiutils", "gui.py")
    subprocess.run(["python", gui_path])
    print("Launching GUI...\n")


def main():
    if "help" in sys.argv:
        display_custom_help()
        return

    parser = argparse.ArgumentParser(description="AgentForge CLI", add_help=False)

    subparsers = parser.add_subparsers(title="Commands",
                                       description="Available commands for AgentForge CLI",
                                       dest="command")

    # Define sub-commands | Note Variables are not used but have been placed in case of further expansion
    init_parser = subparsers.add_parser('init', help="Copy necessary files and set up directories.")
    salience_parser = subparsers.add_parser('salience', help="Copy the salience.py file.")
    gui_parser = subparsers.add_parser('gui', help="Launch the graphical user interface.")

    args = parser.parse_args()

    try:
        if args.command == "init":
            copy_files()
        elif args.command == "salience":
            copy_salience()
        elif args.command == "gui":
            gui()

        print(f"'{args.command}' command executed successfully!\n")

    except Exception as e:
        # Catch any exception and print an error message
        print(f"An error occurred while executing the '{args.command}' command: {str(e)}\n")


if __name__ == "__main__":
    main()
