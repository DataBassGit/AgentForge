import re
import yaml
from typing import Optional, Dict, Any
from .Logger import Logger


class ParsingUtils:

    def __init__(self):
        """
        Initializes the ParsingUtils class with a Logger instance.
        """
        self.logger = Logger(name=self.__class__.__name__)

    def extract_yaml_block(self, text: str) -> Optional[str]:
        """
        Extracts a YAML block from a string, typically used to parse YAML content from larger text blocks or files.
        If no specific YAML block is found, attempts to extract from a generic code block or returns the entire text.

        Parameters:
            text (str): The text containing the YAML block.

        Returns:
            Optional[str]: The extracted YAML block as a string, or None if no valid YAML content is found.
        """
        try:
            # Regex pattern to capture content between ```yaml and ```
            yaml_pattern = r"```yaml(.*?)```"
            match = re.search(yaml_pattern, text, re.DOTALL)

            if match:
                return match.group(1).strip()

            # If no specific YAML block is found, try to capture content between generic code block ```
            code_block_pattern = r"```(.*?)```"
            match = re.search(code_block_pattern, text, re.DOTALL)

            if match:
                return match.group(1).strip()

            # If no code block is found, return the entire text
            return text.strip()
        except Exception as e:
            self.logger.log(f"Regex Error Extracting YAML Block: {e}", 'error')
            return None

    def parse_yaml_content(self, yaml_string: str) -> Optional[Dict[str, Any]]:
        """
        Parses a YAML-formatted string into a Python dictionary.

        Parameters:
            yaml_string (str): The YAML string to parse.

        Returns:
            Optional[Dict[str, Any]]: The parsed YAML content as a dictionary, or None if parsing fails.
        """
        try:
            cleaned_string = self.extract_yaml_block(yaml_string)
            if cleaned_string:
                return yaml.safe_load(cleaned_string)
            return None
        except yaml.YAMLError as e:
            self.logger.parsing_error(yaml_string, e)
            return None

    @staticmethod
    def format_metadata(metadata_list):
        """
        Formats metadata to ensure values are strings, converting lists into comma-separated strings.

        Parameters:
            metadata_list (list): A list of dictionaries, each representing metadata.

        Returns:
            list: The formatted metadata list.
        """
        # Check if the input is a list
        if not isinstance(metadata_list, list):
            raise TypeError("Expected a list of dictionaries")

        # Iterate through each dictionary in the list
        for metadata in metadata_list:
            # Ensure each item in the list is a dictionary
            if not isinstance(metadata, dict):
                raise TypeError("Each item in the list should be a dictionary")

            # Format each dictionary
            for key, value in metadata.items():
                # Check if the value is a list (array)
                if isinstance(value, list):
                    # Convert list elements into a comma-separated string
                    # Update the dictionary with the formatted string
                    metadata[key] = ', '.join(map(str, value))

        return metadata_list