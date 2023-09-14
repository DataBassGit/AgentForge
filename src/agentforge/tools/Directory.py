import os


class DirectoryTool:
    def __init__(self, path="."):
        """
        Initialize the DirectoryTool with the given directory path.
        If no path is provided, it defaults to the current directory.
        """
        self.path = path
        self.excluded_file_types = ['.exe', '.dll']
        self.excluded_files = ['__pycache__']

    def set_excluded_file_types(self, file_types):
        """
        Set the list of file types to be excluded.
        """
        self.excluded_file_types = file_types

    def set_excluded_files(self, files):
        """
        Set the list of files or directories to be excluded.
        """
        self.excluded_files = files

    def list_directory(self, path=None):
        """
        List the directory structure excluding the specified file types and files.
        """
        if path is None:
            path = self.path

        dir_structure = {}

        for item in os.listdir(path):
            if item in self.excluded_files:
                continue

            full_path = os.path.join(path, item)

            if os.path.splitext(item)[1] in self.excluded_file_types:
                continue

            if os.path.isdir(full_path):
                dir_structure[item] = self.list_directory(full_path)
            else:
                dir_structure[item] = None

        return dir_structure

    def print_directory(self, directory, indent=0, max_depth=5):
        if indent >= max_depth:
            padding = '|   ' * (indent - 1)
            print(f"{padding}| ... More Files ... ")
            return

        for name, sub_structure in directory.items():
            padding = '|   ' * (indent - 1)
            if indent > 0:
                padding += '|-- '

            if sub_structure is not None:
                print(f"{padding}{name}/")
                if sub_structure:
                    self.print_directory(sub_structure, indent + 1, max_depth)
            else:
                print(f"{padding}{name}")


dir_tool = DirectoryTool('../../../src')
dir_tool.set_excluded_file_types(['.exe', '.dll', '.pyc', '.pyd', '.pth'])
dir_tool.set_excluded_files(['__init__.py', '__pycache__'])
dir_structure = dir_tool.list_directory()
dir_tool.print_directory(dir_structure)
