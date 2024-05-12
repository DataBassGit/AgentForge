import os


class WriteFile:

    def __init__(self):
        pass

    @staticmethod
    def ensure_folder_exists(folder):
        """Ensure the folder exists, or attempt to create it."""
        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
            except PermissionError:
                return False, f"Permission denied: Unable to create the folder {folder}."
            except Exception as e:
                return False, f"An error occurred while creating the folder: {str(e)}"
        return True, None

    @staticmethod
    def write_to_file(folder, file, text, mode):
        """Write the given text to the specified file."""
        try:
            with open(os.path.join(folder, file), mode, encoding="utf-8") as f:
                f.write(text)
            return True, "Successfully wrote to the file."
        except Exception as e:
            return False, f"An error occurred while writing to the file: {str(e)}"

    @staticmethod
    def generate_message(file, folder, text):
        """Generate a message with a preview of the file's content."""
        content_preview = "\n".join(text.splitlines()[:12])
        if len(text.splitlines()) > 10:
            content_preview += "\n... (more content below)"
        return f"The {file} has successfully been created in '{folder}':\n\n'{content_preview}'"

    def write_file(self, folder, file, text, mode='a'):
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
