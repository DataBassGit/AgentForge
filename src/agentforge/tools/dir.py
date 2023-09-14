import os
import yaml


def exclude_path(item, path):
    # Define exclusion patterns
    exclusion_patterns = [
        ".egg-info",
        "venv",
        os.path.join("../../../Examples", "DB"),
        "build",
    ]

    for pattern in exclusion_patterns:
        if pattern in os.path.join(path, item):
            return True
    return False


def get_structure(path):
    structure = {}
    for item in os.listdir(path):
        if item.startswith('.') or exclude_path(item, path):  # Apply exclusion logic
            continue

        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            structure[item] = get_structure(item_path)
        else:
            structure[item] = "file"  # Representing file with a string
    return structure


def main():
    current_directory = os.getcwd()
    structure = get_structure(current_directory)

    with open('outline.yaml', 'w') as file:
        yaml.dump(structure, file, default_flow_style=False)

    print("YAML outline generated successfully!")


if __name__ == "__main__":
    main()
