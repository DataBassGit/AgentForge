import os

class DirectoryNode:
    """
    Represents a node in the directory tree.

    Attributes:
        name (str): The name of the file or directory.
        is_dir (bool): True if the node is a directory, False if it's a file.
        children (list): List of child DirectoryNode objects.
        depth (int): The depth of the node in the directory tree.
    """

    def __init__(self, name, is_dir, depth=0):
        self.name = name
        self.is_dir = is_dir
        self.children = []
        self.depth = depth

    def add_child(self, child):
        """
        Add a child node to this node.

        Args:
            child (DirectoryNode): The child node to add.
        """
        self.children.append(child)


class Directory:
    """
    A class for building and representing directory trees.

    This class provides methods to build a directory tree, exclude certain files or file types,
    and pretty print the directory structure.

    Attributes:
        root (DirectoryNode): The root node of the directory tree.
        excluded_files (set): Set of file names to exclude from the tree.
        excluded_file_types (set): Set of file extensions to exclude from the tree.
    """

    def __init__(self):
        """
        Initialize the Directory object.
        """
        self.root = None
        self.excluded_files = set()
        self.excluded_file_types = set()

    def build_tree(self, node=None, max_depth=None):
        """
        Recursively build the directory tree.

        Args:
            node (DirectoryNode, optional): The current node being processed. Defaults to None.
            max_depth (int, optional): The maximum depth to traverse. Defaults to None.

        Raises:
            ValueError: If the root node is not set.
        """
        if node is None:
            if self.root is None:
                raise ValueError("Root node is not set. Call read_directory() first.")
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
            node.add_child(DirectoryNode('Permission denied', False, node.depth + 1))
        except Exception as e:
            node.add_child(DirectoryNode(f'Error: {str(e)}', False, node.depth + 1))

    def pretty_print(self, node=None, indent=""):
        """
        Generate a pretty-printed string representation of the directory tree.

        Args:
            node (DirectoryNode, optional): The current node being processed. Defaults to None.
            indent (str, optional): The indentation string. Defaults to "".

        Returns:
            str: A string representation of the directory tree.

        Raises:
            ValueError: If the root node is not set.
        """
        if node is None:
            if self.root is None:
                raise ValueError("Root node is not set. Call read_directory() first.")
            node = self.root

        directory_str = ""
        if node.is_dir:
            directory_str += f"{indent}{os.path.basename(node.name)}/\n"
        else:
            directory_str += f"{indent}{os.path.basename(node.name)}\n"
        indent += "    "
        for child in node.children:
            directory_str += self.pretty_print(child, indent)
        return directory_str

    def read_directory(self, directory_paths, max_depth=None):
        """
        Read the specified directories and build the directory tree.

        Args:
            directory_paths (str or list): A single directory path or a list of directory paths.
            max_depth (int, optional): The maximum depth to traverse. Defaults to None.

        Returns:
            str: A string representation of the directory tree(s).

        Raises:
            ValueError: If the input is not a string or a list of strings.
            OSError: If there's an error creating or accessing a directory.
        """
        if isinstance(directory_paths, str):
            directory_paths = [directory_paths]
        elif not isinstance(directory_paths, list) or not all(isinstance(path, str) for path in directory_paths):
            raise ValueError("directory_paths must be a string or a list of strings")

        output = ""
        for directory_path in directory_paths:
            try:
                if not os.path.exists(directory_path):
                    os.makedirs(directory_path, exist_ok=True)
                    output += f"Created '{directory_path}'\n"
                    continue

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
            except OSError as e:
                output += f"OS error occurred: {str(e)}\n"
            except Exception as e:
                output += f"An unexpected error occurred: {str(e)}\n"

        return output.strip()

# Usage example (commented out)
# if __name__ == "__main__":
#     dir_tree = Directory()
#     dir_tree.excluded_file_types = {'.exe', '.dll'}
#     dir_tree.excluded_files = {'__pycache__', '__init__.py'}
#
#     try:
#         # Test with a single path
#         single_path = '../../.agentforge'  # Replace with a valid directory path
#         print("---- Single Path Test ----")
#         print(dir_tree.read_directory(single_path, max_depth=2))
#         print("\n")
#
#         # Test with multiple paths
#         multiple_paths = [
#             '../../.agentforge/agents',  # Replace with a valid directory path
#             '../../.agentforge/settings'  # Replace with another valid directory path
#         ]
#         print("---- Multiple Paths Test ----")
#         print(dir_tree.read_directory(multiple_paths, max_depth=2))
#     except Exception as e:
#         print(f"Error: {str(e)}")
