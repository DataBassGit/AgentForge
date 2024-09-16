import unicodedata

class Strip:
    """
    A utility class for cleaning and sanitizing strings.

    This class provides static methods to strip invalid characters from strings,
    making them suitable for use in specific contexts like YAML.

    Raises:
        Exception: If any of the methods fail to process the input string.
    """

    @staticmethod
    def strip_invalid_chars(text):
        """
        Strips invalid characters from a string, allowing only characters suitable for YAML.

        Args:
            text (str): The input string.

        Returns:
            str: The string with invalid characters replaced with underscores.

        Raises:
            TypeError: If the input is not a string.
            Exception: If the string cleaning process fails.
        """
        if not isinstance(text, str):
            raise TypeError("Input must be a string")

        try:
            allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.!@#$%^&*()[]{};'" + chr(10) + chr(13) + " ")
            clean_text = []
            for char in text:
                if char in allowed_chars:
                    clean_text.append(char)
                else:
                    clean_text.append('_')  # Replace invalid characters with underscores
            return ''.join(clean_text)
        except Exception as e:
            raise Exception(f"Failed to strip invalid characters: {str(e)}") from e

    @staticmethod
    def normalize_unicode(text):
        """
        Normalizes Unicode characters in a string to their closest ASCII representation.

        Args:
            text (str): The input string containing Unicode characters.

        Returns:
            str: The normalized string with Unicode characters converted to ASCII.

        Raises:
            TypeError: If the input is not a string.
            Exception: If the Unicode normalization process fails.
        """
        if not isinstance(text, str):
            raise TypeError("Input must be a string")

        try:
            return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
        except Exception as e:
            raise Exception(f"Failed to normalize Unicode characters: {str(e)}") from e

    @staticmethod
    def remove_control_characters(text):
        """
        Removes control characters from a string.

        Args:
            text (str): The input string.

        Returns:
            str: The string with control characters removed.

        Raises:
            TypeError: If the input is not a string.
            Exception: If the control character removal process fails.
        """
        if not isinstance(text, str):
            raise TypeError("Input must be a string")

        try:
            return ''.join(char for char in text if unicodedata.category(char)[0] != 'C')
        except Exception as e:
            raise Exception(f"Failed to remove control characters: {str(e)}") from e
