import re
import yaml
from typing import Optional, Dict, Any
from agentforge.utils.Logger import Logger


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
