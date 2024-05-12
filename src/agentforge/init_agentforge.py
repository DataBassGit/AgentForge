import os
import shutil
import importlib.util
from pathlib import Path


def copy_directory(root, src, dst, override_all=False, skip_all=False):
    """
    Copies a directory from src to dst, including all subdirectories and files,
    with options to override or skip existing files.
    """
    for src_dir, dirs, files in os.walk(src):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']
        dst_dir = src_dir.replace(str(src), str(dst), 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
            print(f"Created directory {dst_dir}")

        for file_ in files:
            # Skip __init__.py files and any .pyc files
            if file_ == '__init__.py' or file_.endswith('.pyc'):
                continue

            src_file_path = os.path.join(src_dir, file_)
            dst_file_path = os.path.join(dst_dir, file_)

            # If the file exists, decide whether to override or skip based on user input
            if os.path.exists(dst_file_path):
                if not override_all and not skip_all:
                    print(f"The file {dst_file_path} already exists.")
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
                    elif response == 'n':
                        print(f"Skipping {dst_file_path}")
                        continue
                    elif response != 'y':
                        print("Invalid option. Skipping this file.")
                        continue

            if not skip_all:
                # Ensure the file paths are strings if they're not already
                src_file_str = str(src_file_path)
                dst_file_str = str(dst_file_path)

                shutil.copy2(src_file_str, dst_file_str)  # copy2 is used to preserve metadata

                # Extract just the filename
                filename = os.path.basename(src_file_str)
                project_root = os.path.basename(root)

                # Extract the relative destination path (assuming 'root' is the base directory)
                relative_dst_path = os.path.relpath(dst_file_str, start=root)
                print(f"Copied {filename} to {project_root}\\{relative_dst_path}")
            else:
                print(f"Skipped {src_file_path}")


def setup_agentforge():
    """
    Sets up the AgentForge project directory by copying the setup_files directory.
    """
    # Identify the AgentForge library path
    package_name = 'agentforge'
    try:
        spec = importlib.util.find_spec(package_name)
        if spec is None:
            print(f"{package_name} is not installed.")
            return

        agentforge_path = spec.submodule_search_locations[0]
        # agentforge_path = 'D:\\Github\\AgentForge\\src\\agentforge'

        print(f"Found {package_name} at {agentforge_path}")

        # Define source and destination paths
        installer_path = os.path.join(agentforge_path, 'setup_files')
        project_root = Path.cwd()
        destination_path = project_root / '.agentforge'

        # Copy the setup_files directory to the project directory
        copy_directory(project_root, installer_path, destination_path)

        print("AgentForge setup is complete.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    setup_agentforge()
