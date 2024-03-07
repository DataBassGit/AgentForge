import os
import shutil
import argparse
import pkg_resources
# import subprocess
import sys

help_message = """
Available commands for AgentForge:

init       - Copy necessary files and set up directories.
salience   - Copy the salience.py file.
gui        - Launch the graphical user interface.

For more details on each command, use '.agentforge <command> -h'
"""


def display_custom_help():
    print(help_message)


def copy_yaml_files():
    try:
        src_base_path = pkg_resources.resource_filename(".agentforge.utils.installer", "")
        dest_base_path = ".agentforge"
        override_all = False
        skip_all = False

        for root, dirs, files in os.walk(src_base_path):
            for file in files:
                if file.endswith('.yaml'):
                    src_file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(root, src_base_path)
                    dest_directory = os.path.join(dest_base_path, relative_path)
                    os.makedirs(dest_directory, exist_ok=True)
                    dest_file_path = os.path.join(dest_directory, file)

                    # Check if the destination file already exists
                    if os.path.exists(dest_file_path) and not override_all and not skip_all:
                        print(f"The file {dest_file_path} already exists.")

                        response = input(
                            "Select an option:\n"
                            "[Y] Override this file\n"
                            "[N] Skip this file\n"
                            "[A] Override all existing files without asking again\n"
                            "[Z] Skip all existing files without asking again\n"
                            "Enter your choice (Y/N/A/Z): "
                        ).lower()

                        if response == 'a':
                            override_all = True
                        elif response == 'z':
                            skip_all = True
                        elif response == 'y':
                            pass
                        elif response == 'n':
                            print(f"Skipping {dest_file_path}")
                            continue
                        else:
                            print("Invalid option. Skipping this file.")
                            continue

                    if not skip_all:
                        shutil.copyfile(src_file_path, dest_file_path)
                        print(f"Copied {src_file_path} to {dest_file_path}")
                    else:
                        print(f"Skipped {src_file_path}")

    except Exception as e:
        print(f"Error copying YAML files: {e}")
        sys.exit(1)


def init_command():
    print("Starting initialization...")
    copy_yaml_files()
    print("Initialization complete: YAML files have been copied.")


# def copy_salience():
#     try:
#         print("Copying Salience...")
#         src_path = pkg_resources.resource_filename(".agentforge.utils.installer", "salience.py")
#         shutil.copyfile(src_path, "salience.py")
#         print("Salience.py has been successfully copied!\n")
#     except Exception as e:
#         print(f"Error copying salience.py: {e}")
#         sys.exit(1)


# def gui():
#     try:
#         print("Launching GUI...")
#         gui_path = pkg_resources.resource_filename(".agentforge.utils.guiutils", "gui.py")
#         subprocess.run(["python", gui_path])
#         print("GUI launched successfully.\n")
#     except Exception as e:
#         print(f"Error launching GUI: {e}")
#         sys.exit(1)


def main():
    if "help" in sys.argv:
        display_custom_help()
        return

    parser = argparse.ArgumentParser(description="AgentForge CLI", add_help=False)
    subparsers = parser.add_subparsers(title="Commands",
                                       description="Available commands for AgentForge CLI",
                                       dest="command")

    # Define sub-commands
    init_parser = subparsers.add_parser('init', help="Copy necessary files and set up directories.")
    # salience_parser = subparsers.add_parser('salience', help="Copy the salience.py file.")
    # gui_parser = subparsers.add_parser('gui', help="Launch the graphical user interface.")

    args = parser.parse_args()

    try:
        if args.command == "init":
            init_command()
        # elif args.command == "salience":
        #     copy_salience()
        # elif args.command == "gui":
        #     gui()
        else:
            display_custom_help()
    except Exception as e:
        print(f"An error occurred while executing the '{args.command}' command: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
