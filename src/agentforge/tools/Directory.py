import os


class DirectoryNode:
    def __init__(self, name, is_dir, depth=0):
        self.name = name
        self.is_dir = is_dir
        self.children = []
        self.depth = depth

    def add_child(self, child):
        self.children.append(child)


class Directory:
    def __init__(self):
        self.root = None
        self.excluded_files = set()
        self.excluded_file_types = set()

    def build_tree(self, node=None, max_depth=None):
        if node is None:
            node = self.root
        if max_depth is not None and node.depth >= max_depth:
            node.add_child(DirectoryNode('... more files ...', False, node.depth + 1))
            return

        try:
            for item in os.listdir(node.name):
                if item in self.excluded_files:
                    continue

                full_path = os.path.join(node.name, item)
                if os.path.isdir(full_path):
                    child_node = DirectoryNode(full_path, True, node.depth + 1)
                    node.add_child(child_node)
                    self.build_tree(child_node, max_depth)
                elif os.path.splitext(item)[1] not in self.excluded_file_types:
                    child_node = DirectoryNode(full_path, False, node.depth + 1)
                    node.add_child(child_node)
        except PermissionError:
            pass  # Ignore directories for which the user has no access

    def pretty_print(self, node=None, indent=""):
        directory_str = ""
        if node is None:
            node = self.root
        if node.is_dir:
            directory_str += f"{indent}{os.path.basename(node.name)}/\n"
        else:
            directory_str += f"{indent}{os.path.basename(node.name)}\n"
        indent += "    "
        for child in node.children:
            directory_str += self.pretty_print(child, indent)
        return directory_str

    def read_directory(self, directory_paths, max_depth):
        if isinstance(directory_paths, str):
            # If it's a single path, make it a list
            directory_paths = [directory_paths]

        output = ""
        for directory_path in directory_paths:
            try:
                # Check if the path exists
                if not os.path.exists(directory_path):
                    # Create the directory if it doesn't exist
                    os.makedirs(directory_path, exist_ok=True)
                    output += f"Created '{directory_path}'\n"
                    continue

                # Check if the directory is empty
                if not os.listdir(directory_path):
                    output += f"The directory at '{directory_path}' is empty.\n"
                    continue

                self.root = DirectoryNode(directory_path, True)
                self.build_tree(self.root, max_depth)
                output += self.pretty_print() + "\n"

            except PermissionError:
                output += f"Permission denied: Unable to access '{directory_path}'.\n"
            except FileNotFoundError:
                output += f"File not found: The path '{directory_path}' does not exist.\n"
            except Exception as e:
                output += f"An error occurred: {str(e)}\n"

        return output.strip()


# # Usage Example
# dir_tree = Directory()
# dir_tree.excluded_file_types = {'.exe', '.dll'}
# dir_tree.excluded_files = {'__pycache__', '__init__.py'}
#
# # Test with a single path
# single_path = '../../.agentforge'  # Replace with a valid directory path
# print("---- Single Path Test ----")
# print(dir_tree.read_directory(single_path, max_depth=2))
# print("\n")
#
# # Test with multiple paths
# multiple_paths = [
#     '../../.agentforge/agents',  # Replace with a valid directory path
#     '../../.agentforge/settings'  # Replace with another valid directory path
# ]
# print("---- Multiple Paths Test ----")
# print(dir_tree.read_directory(multiple_paths, max_depth=2))
