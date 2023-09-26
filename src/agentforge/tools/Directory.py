import os


class Directory:
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

        path_structure = {}

        for item in os.listdir(path):
            if item in self.excluded_files:
                continue

            full_path = os.path.join(path, item)

            if os.path.splitext(item)[1] in self.excluded_file_types:
                continue

            if os.path.isdir(full_path):
                path_structure[item] = self.list_directory(full_path)
            else:
                path_structure[item] = None

        return path_structure

    def read_directory(self, directory_path, indent=0, max_depth=2):
        output = ""

        directory = self.list_directory(directory_path)
        if directory:
            return f"{directory_path}/"

        if indent >= max_depth:
            padding = '|   ' * (indent - 1)
            line = f"{padding}| ... More Files ... \n"
            output += line
            return output

        for name, sub_structure in directory.items():
            padding = '|   ' * (indent - 1)
            if indent > 0:
                padding += '|-- '

            if sub_structure is not None:
                line = f"{padding}{name}/\n"
                output += line
                if sub_structure:
                    output += self.read_directory(sub_structure, indent + 1, max_depth)
            else:
                line = f"{padding}{name}\n"
                output += line

        print(output)
        return output

# dir_tool = DirectoryTool('../../agentforge')
# dir_tool.set_excluded_file_types(['.dll', '.pyc', '.pyd', '.pth'])
# dir_tool.set_excluded_files(['__init__.py', '__pycache__'])
# dir_structure = dir_tool.list_directory()
# dir_tool.read_directory(dir_structure)
