from __future__ import annotations

import filecmp
import importlib.util
import os
import shutil
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
    valid_choices = {"y", "n", "a", "z"}
    if response in valid_choices:
        return response
    print("Invalid option. Skipping this file by default.")
    return ""


def should_copy_file(
    src_file: str | Path, dst_file: str | Path, skip_all: bool, override_all: bool
) -> tuple[bool, bool, bool]:
    """
    Determines whether to copy a file from src_file to dst_file based on existing
    state flags and user decision. Returns a tuple of three booleans in the form:
      (copy_this_file, new_skip_all, new_override_all).
    """
    src_path = Path(src_file)
    dst_path = Path(dst_file)

    if skip_all:
        return False, skip_all, override_all

    if not dst_path.exists():
        return True, skip_all, override_all

    if filecmp.cmp(src_path, dst_path, shallow=False):
        return False, skip_all, override_all

    if override_all:
        return True, skip_all, override_all

    decision = user_decision_prompt(os.path.relpath(dst_path))
    if decision == "a":
        return True, skip_all, True
    if decision == "z":
        return False, True, override_all
    if decision == "n":
        return False, skip_all, override_all
    if decision == "y":
        return True, skip_all, override_all

    return False, skip_all, override_all


def copy_directory(root: Path, src: Path, override_all: bool = False, skip_all: bool = False) -> None:
    """
    Recursively copies files from 'src' to 'root', skipping __pycache__ and __init__.py
    or .pyc files, while respecting user choices about overwriting.
    """
    for current_dir, dirs, files in os.walk(src):
        dirs[:] = [directory for directory in dirs if directory != "__pycache__"]
        current_path = Path(current_dir)
        dst_dir = root / current_path.relative_to(src)
        if not dst_dir.exists():
            dst_dir.mkdir(parents=True)
            print(f"Created directory '{os.path.relpath(dst_dir, start=root)}'.")

        for file_ in files:
            if file_ == "__init__.py" or file_.endswith(".pyc"):
                continue

            src_file = current_path / file_
            dst_file = dst_dir / file_
            relative_src_path = src_file.relative_to(src)
            relative_dst_path = dst_file.relative_to(root)

            do_copy, skip_all, override_all = should_copy_file(src_file, dst_file, skip_all, override_all)

            if not do_copy:
                print(f"Skipped '{relative_dst_path}'.")
                continue

            shutil.copy2(src_file, dst_file)
            print(f"Copied '{relative_src_path}' to '{relative_dst_path}'.")


def setup_agentforge() -> None:
    """
    Locates the AgentForge package, copies its 'setup_files' directory into
    the current working directory, and provides feedback on the process.
    """
    package_name = "agentforge"
    try:
        spec = importlib.util.find_spec(package_name)
        if spec is None:
            print(f"{package_name} is not installed.")
            return

        package_locations = list(spec.submodule_search_locations or [])
        if not package_locations:
            print(f"{package_name} package location could not be resolved.")
            return

        agentforge_path = Path(package_locations[0])
        print(f"Found {package_name} at {agentforge_path}")
        installer_path = agentforge_path / "setup_files"
        project_root = Path.cwd() / ".agentforge"
        if not project_root.exists():
            project_root.mkdir()
            print(f"Created project template directory: {project_root}")
        copy_directory(project_root, installer_path)
        print("AgentForge setup is complete.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    setup_agentforge()
