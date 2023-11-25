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

    def read_directory(self, directory_path, max_depth):
        self.root = DirectoryNode(directory_path, True)
        self.build_tree(self.root, max_depth)
        return self.pretty_print()


# Usage Example
# dir_tree = DirectoryTree()
# dir_tree.excluded_file_types = {'.exe', '.dll'}
# dir_tree.excluded_files = {'__pycache__'}
# dir_tree.read_directory('../../agentforge', 3)  # Replace with your directory path and desired depth
