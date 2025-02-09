import os
import shutil
import filecmp
import importlib.util
from pathlib import Path


def user_decision_prompt(existing_file: str) -> str:
    """
    Interactively prompts the user about what to do with a file conflict.
    Returns one of the following single-character codes:
      - 'y' for overriding the file
      - 'n' for skipping this file
      - 'a' for overriding all existing files without asking again
      - 'z' for skipping all existing files without asking again
      - '' (empty) if the user input is invalid
    """
    print(f"\nFile '{existing_file}' already exists and is different from the source.")
    response = input(
        "Select an option:\n"
        "[Y] Override this file\n"
        "[N] Skip this file\n"
        "[A] Override all existing files without asking again\n"
        "[Z] Skip all existing files without asking again\n"
        "Enter your choice (Y/N/A/Z): "
    ).lower()
    valid_choices = {'y', 'n', 'a', 'z'}
    if response in valid_choices:
        return response
    print("Invalid option. Skipping this file by default.")
    return ''


def should_copy_file(
        src_file: str,
        dst_file: str,
        skip_all: bool,
        override_all: bool
) -> (bool, bool, bool):
    """
    Determines whether to copy a file from src_file to dst_file based on existing
    state flags and user decision. Returns a tuple of three booleans in the form:
      (copy_this_file, new_skip_all, new_override_all).
    """
    if skip_all:
        # We’re skipping all conflicts globally, no copy, just return the updated flags.
        return False, skip_all, override_all

    if not os.path.exists(dst_file):
        # If there's no existing file, proceed with the copy.
        return True, skip_all, override_all

    # If the files match, skip copying; there's no reason to replace it.
    if filecmp.cmp(src_file, dst_file, shallow=False):
        return False, skip_all, override_all

    # If we’re overriding all conflicts globally, skip user prompt and copy.
    if override_all:
        return True, skip_all, override_all

    # Otherwise, prompt the user for a decision.
    decision = user_decision_prompt(os.path.relpath(dst_file))
    if decision == 'a':
        # Override all from now on.
        return True, skip_all, True
    if decision == 'z':
        # Skip all from now on.
        return False, True, override_all
    if decision == 'n':
        # Skip just this file.
        return False, skip_all, override_all
    if decision == 'y':
        # Copy just this file.
        return True, skip_all, override_all

    # If user input is invalid or empty, skip the file by default.
    return False, skip_all, override_all


def copy_directory(
        root: Path,
        src: Path,
        override_all: bool = False,
        skip_all: bool = False
) -> None:
    """
    Recursively copies files from 'src' to 'root', skipping __pycache__ and __init__.py
    or .pyc files, while respecting user choices about overwriting.
    """
    for current_dir, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        dst_dir = current_dir.replace(str(src), str(root), 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
            print(f"Created directory '{os.path.relpath(dst_dir, start=root)}'.")

        for file_ in files:
            if file_ == '__init__.py' or file_.endswith('.pyc'):
                continue

            src_file_str = str(os.path.join(current_dir, file_))
            dst_file_str = str(os.path.join(dst_dir, file_))

            relative_src_path = os.path.relpath(src_file_str, start=src)
            relative_dst_path = os.path.relpath(dst_file_str, start=root)

            do_copy, skip_all, override_all = should_copy_file(
                src_file_str,
                dst_file_str,
                skip_all,
                override_all
            )

            if not do_copy:
                print(f"Skipped '{relative_dst_path}'.")
                continue

            shutil.copy2(src_file_str, dst_file_str)
            print(f"Copied '{relative_src_path}' to '{relative_dst_path}'.")


def setup_agentforge() -> None:
    """
    Locates the AgentForge package, copies its 'setup_files' directory into
    the current working directory, and provides feedback on the process.
    """
    package_name = 'agentforge'
    try:
        spec = importlib.util.find_spec(package_name)
        if spec is None:
            print(f"{package_name} is not installed.")
            return

        agentforge_path = spec.submodule_search_locations[0]
        print(f"Found {package_name} at {agentforge_path}")
        installer_path = os.path.join(agentforge_path, 'setup_files')
        project_root = Path.cwd() / ".agentforge"
        if not project_root.exists():
            project_root.mkdir()
            print(f"Created project template directory: {project_root}")
        copy_directory(project_root, Path(installer_path))
        print("AgentForge setup is complete.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    setup_agentforge()
