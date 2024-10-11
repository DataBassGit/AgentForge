import os
import shutil
import filecmp
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
            print(f"Created directory '{os.path.relpath(dst_dir, start=dst)}'.")

        for file_ in files:
            # Skip __init__.py files and any .pyc files
            if file_ == '__init__.py' or file_.endswith('.pyc'):
                continue

            src_file_path = os.path.join(src_dir, file_)
            dst_file_path = os.path.join(dst_dir, file_)

            # Ensure the file paths are strings if they're not already
            src_file_str = str(src_file_path)
            dst_file_str = str(dst_file_path)

            relative_src_path = os.path.relpath(src_file_str, start=src)
            relative_dst_path = os.path.relpath(dst_file_str, start=dst)

            if os.path.exists(dst_file_str):
                # Compare the files
                if filecmp.cmp(src_file_str, dst_file_str, shallow=False):
                    # Files are the same, skip copying
                    print(f"No changes detected in '{relative_dst_path}'. Skipping.")
                    continue
                else:
                    # Files are different
                    if skip_all:
                        print(f"Skipped '{relative_dst_path}' (skip all is enabled).")
                        continue
                    elif override_all:
                        # Proceed to copy
                        pass
                    else:
                        # Prompt the user for action
                        print(f"\nFile '{relative_dst_path}' already exists and is different from the source.")
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
                            # Proceed to copy
                        elif response == 'z':
                            skip_all = True
                            print(f"Skipped '{relative_dst_path}' (skip all is enabled).")
                            continue
                        elif response == 'n':
                            print(f"Skipped '{relative_dst_path}'.")
                            continue
                        elif response == 'y':
                            # Proceed to copy
                            pass
                        else:
                            print("Invalid option. Skipping this file.")
                            continue
            else:
                # Destination file does not exist, proceed to copy
                pass

            if skip_all:
                print(f"Skipped '{relative_dst_path}' (skip all is enabled).")
                continue

            # Proceed to copy the file
            shutil.copy2(src_file_str, dst_file_str)  # copy2 is used to preserve metadata

            print(f"Copied '{relative_src_path}' to '{relative_dst_path}'.")


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
