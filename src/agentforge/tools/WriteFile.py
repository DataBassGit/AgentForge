import os


class WriteFile:
    """
    A class for writing content to files and managing directories.

    This class provides methods to ensure folders exist, write content to files,
    and generate messages about the file creation process.
    """

    def __init__(self):
        """
        Initialize a WriteFile object.

        This method currently doesn't set up any attributes but is included for future extensibility.
        """
        pass

    @staticmethod
    def ensure_folder_exists(folder):
        """
        Ensure the folder exists, or attempt to create it.

        Args:
            folder (str): The path to the folder.

        Returns:
            tuple: A tuple containing (success, error_message).
                   success (bool): True if the folder exists or was created successfully, False otherwise.
                   error_message (str or None): An error message if the operation failed, None otherwise.

        Raises:
            ValueError: If the folder path is not a string or is empty.
        """
        if not isinstance(folder, str) or not folder.strip():
            raise ValueError("Folder path must be a non-empty string")

        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
            except PermissionError:
                return False, f"Permission denied: Unable to create the folder {folder}."
            except OSError as e:
                return False, f"An error occurred while creating the folder: {str(e)}"
        return True, None

    @staticmethod
    def write_to_file(folder, file, text, mode):
        """
        Write the given text to the specified file.

        Args:
            folder (str): The path to the folder containing the file.
            file (str): The name of the file.
            text (str): The content to write to the file.
            mode (str): The mode in which to open the file ('w' for write, 'a' for append).

        Returns:
            tuple: A tuple containing (success, message).
                   success (bool): True if the write operation was successful, False otherwise.
                   message (str): A success or error message.

        Raises:
            ValueError: If any of the input parameters are invalid.
        """
        if not isinstance(folder, str) or not folder.strip():
            raise ValueError("Folder path must be a non-empty string")
        if not isinstance(file, str) or not file.strip():
            raise ValueError("File name must be a non-empty string")
        if not isinstance(text, str):
            raise ValueError("Text must be a string")
        if mode not in ['w', 'a']:
            raise ValueError("Mode must be either 'w' or 'a'")

        try:
            with open(os.path.join(folder, file), mode, encoding="utf-8") as f:
                f.write(text)
            return True, "Successfully wrote to the file."
        except PermissionError:
            return False, f"Permission denied: Unable to write to the file {file}."
        except OSError as e:
            return False, f"An error occurred while writing to the file: {str(e)}"

    @staticmethod
    def generate_message(file, folder, text):
        """
        Generate a message with a preview of the file's content.

        Args:
            file (str): The name of the file.
            folder (str): The path to the folder containing the file.
            text (str): The content of the file.

        Returns:
            str: A formatted message containing file information and a content preview.

        Raises:
            ValueError: If any of the input parameters are invalid.
        """
        if not isinstance(file, str) or not file.strip():
            raise ValueError("File name must be a non-empty string")
        if not isinstance(folder, str) or not folder.strip():
            raise ValueError("Folder path must be a non-empty string")
        if not isinstance(text, str):
            raise ValueError("Text must be a string")

        content_preview = "\n".join(text.splitlines()[:12])
        if len(text.splitlines()) > 10:
            content_preview += "\n... (more content below)"
        return f"The {file} has successfully been created in '{folder}':\n\n'{content_preview}'"

    def write_file(self, folder, file, text, mode='a'):
        """
        Write content to a file, ensuring the folder exists.

        This method combines the functionality of ensure_folder_exists, write_to_file,
        and generate_message to provide a complete file writing process.

        Args:
            folder (str): The path to the folder containing the file.
            file (str): The name of the file.
            text (str): The content to write to the file.
            mode (str, optional): The mode in which to open the file ('w' for write, 'a' for append).
                                  Defaults to 'a'.

        Returns:
            str: A message indicating the result of the file writing process.

        Raises:
            ValueError: If any of the input parameters are invalid.
        """
        if not isinstance(folder, str) or not folder.strip():
            raise ValueError("Folder path must be a non-empty string")
        if not isinstance(file, str) or not file.strip():
            raise ValueError("File name must be a non-empty string")
        if not isinstance(text, str):
            raise ValueError("Text must be a string")
        if mode not in ['w', 'a']:
            raise ValueError("Mode must be either 'w' or 'a'")

        success, message = self.ensure_folder_exists(folder)
        if not success:
            return message

        success, message = self.write_to_file(folder, file, text, mode)
        if not success:
            return message

        return self.generate_message(file, folder, text)


# def read_file(file_path):
#     with open(file_path, 'r') as file:
#         text = file.read()
#     return text
