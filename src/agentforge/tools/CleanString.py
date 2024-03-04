import unicodedata

class Strip:
    def __init__(self):
        pass

    @staticmethod
    def strip_invalid_chars(text):
        """
        Strips invalid characters from a string, allowing only characters suitable for YAML.

        Args:
            text (str): The input string.

        Returns:
            str: The string with invalid characters replaced with underscores.
        """
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.!@#$%^&*()[]{};'" + chr(10) + chr(13) + " ")  # Add spaces
        clean_text = []
        for char in text:
            if char in allowed_chars:
                clean_text.append(char)
            else:
                clean_text.append('_')  # Replace invalid characters with underscores
        return ''.join(clean_text)
