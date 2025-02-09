import re
import json
import yaml
from typing import Optional, Dict, Any, Callable, Type, List, Tuple
from agentforge.utils.logger import Logger
import xmltodict
import configparser
import csv
from io import StringIO

class ParsingProcessor:

    def __init__(self):
        """
        Initializes the ParsingUtils class.
        """
        # Assuming Logger is defined elsewhere or replace with appropriate logging
        self.logger = Logger(name=self.__class__.__name__)

    def extract_code_block(self, text: str, code_fence: str = "```") -> Optional[Tuple[Optional[str], str]]:
        """
        Extracts a code block from a string using the specified code fence delimiter. The method returns the language specifier
        (if present) along with the code block's content. It supports code blocks with or without a language specifier.
        If multiple code blocks exist, it returns the first match. If no code block is found, the original text is returned
        with a None language specifier.

        Parameters:
            text (str): The text containing the code block.
            code_fence (str): The delimiter marking the boundaries of the code block. Defaults to triple backticks (```).

        Returns:
            Optional[Tuple[Optional[str], str]]: A tuple containing the language specifier (or None) and the extracted code block content.
        """
        try:
            # Escape the code fence to ensure that any special regex characters are treated literally.
            escaped_fence = re.escape(code_fence)
            # Build a regex pattern that uses the provided code fence for both the opening and closing parts of the code block.
            code_block_pattern = fr"{escaped_fence}([a-zA-Z]*)\r?\n([\s\S]*?){escaped_fence}"
            match = re.search(code_block_pattern, text, re.DOTALL)

            if match:
                language = match.group(1).strip() or None
                content = match.group(2).strip()
                return language, content

            # If no code block is found, return the original text and a None for the language.
            return None, text.strip()
        except Exception as e:
            self.logger.log(f"Regex Error Extracting Code Block: {e}", 'error')
            return None

    def parse_content(
        self,
        content_string: str,
        parser_func: Callable[[str], Any],
        expected_language: str,
        exception_class: Type[Exception]
    ) -> Optional[Dict[str, Any]]:
        """
        A generic method to parse content using a specified parser function.

        Parameters:
            content_string (str): The string containing the content to parse.
            parser_func (Callable[[str], Any]): The parsing function (e.g., json.loads, yaml.safe_load).
            expected_language (str): The expected language specifier (e.g., 'json', 'yaml').
            exception_class (Type[Exception]): The exception class to catch during parsing.

        Returns:
            Optional[Dict[str, Any]]: The parsed content as a dictionary, or None if parsing fails.
        """
        try:
            language, cleaned_string = self.extract_code_block(content_string)
            if language and language.lower() != expected_language.lower():
                self.logger.log(f"Expected {expected_language.upper()} code block, but found '{language}'", 'warning')

            if cleaned_string:
                return parser_func(cleaned_string)
            return None
        except exception_class as e:
            self.logger.log(f"Parsing error: {e}", 'error')
            return None
        except Exception as e:
            self.logger.log(f"Unexpected error parsing {expected_language.upper()} content: {e}", 'error')
            return None

    @staticmethod
    def parse_markdown_to_dict(markdown_text: str, min_heading_level=2, max_heading_level=6) -> Optional[Dict[str, Any]]:
        """
        Parses a markdown-formatted string into a dictionary, mapping each heading to its corresponding content.

        Parameters:
            markdown_text (str): The markdown-formatted text to parse.
            min_heading_level (int, optional): The minimum heading level to include (default is 2).
            max_heading_level (int, optional): The maximum heading level to include (default is 6).

        Returns:
            Optional[Dict[str, Any]]: A dictionary where each key is a heading and each value is the associated content.
        """
        parsed_dict = {}
        current_heading = None
        content_lines = []

        # Compile regex pattern for headings based on specified heading levels
        heading_pattern = re.compile(r'^(#{%d,%d})\s+(.*)' % (min_heading_level, max_heading_level))

        lines = markdown_text.split('\n')
        for line in lines:
            match = heading_pattern.match(line)
            if match:
                # Save content under the previous heading
                if current_heading is not None:
                    parsed_dict[current_heading] = '\n'.join(content_lines).strip()
                    content_lines = []
                # Update current heading
                current_heading = match.group(2).strip()
            else:
                if current_heading is not None:
                    content_lines.append(line)
        # Save content under the last heading
        if current_heading is not None:
            parsed_dict[current_heading] = '\n'.join(content_lines).strip()

        return parsed_dict if parsed_dict else None

    def parse_markdown_content(self, markdown_string: str, min_heading_level=2, max_heading_level=6) -> Optional[Dict[str, Any]]:
        """
        Parses a Markdown-formatted string into a Python dictionary.

        Parameters:
            markdown_string (str): The Markdown string to parse.
            min_heading_level (int, optional): The minimum heading level to include (default is 2).
            max_heading_level (int, optional): The maximum heading level to include (default is 6).

        Returns:
            Optional[Dict[str, Any]]: The parsed Markdown content as a dictionary, or None if parsing fails.
        """
        def parser_func(s):
            return self.parse_markdown_to_dict(s, min_heading_level, max_heading_level)

        return self.parse_content(
            content_string=markdown_string,
            parser_func=parser_func,
            expected_language='markdown',
            exception_class=Exception
        )

    def parse_yaml_content(self, yaml_string: str) -> Optional[Dict[str, Any]]:
        """
        Parses a YAML-formatted string into a Python dictionary.

        Parameters:
            yaml_string (str): The YAML string to parse.

        Returns:
            Optional[Dict[str, Any]]: The parsed YAML content as a dictionary, or None if parsing fails.
        """
        return self.parse_content(
            content_string=yaml_string,
            parser_func=yaml.safe_load,
            expected_language='yaml',
            exception_class=yaml.YAMLError
        )

    def parse_json_content(self, json_string: str) -> Optional[Dict[str, Any]]:
        """
        Parses a JSON-formatted string into a Python dictionary.

        Parameters:
            json_string (str): The JSON string to parse.

        Returns:
            Optional[Dict[str, Any]]: The parsed JSON content as a dictionary, or None if parsing fails.
        """
        return self.parse_content(
            content_string=json_string,
            parser_func=json.loads,
            expected_language='json',
            exception_class=json.JSONDecodeError
        )

    def parse_xml_content(self, xml_string: str) -> Optional[Dict[str, Any]]:
        """
        Parses an XML-formatted string into a Python dictionary.

        Parameters:
            xml_string (str): The XML string to parse.

        Returns:
            Optional[Dict[str, Any]]: The parsed XML content as a dictionary, or None if parsing fails.
        """
        return self.parse_content(
            content_string=xml_string,
            parser_func=xmltodict.parse,
            expected_language='xml',
            exception_class=Exception  # Replace with a more specific exception if available
        )

    def parse_ini_content(self, ini_string: str) -> Optional[Dict[str, Any]]:
        """
        Parses an INI-formatted string into a Python dictionary.

        Parameters:
            ini_string (str): The INI string to parse.

        Returns:
            Optional[Dict[str, Any]]: The parsed INI content as a dictionary, or None if parsing fails.
        """
        def parser_func(s):
            parser = configparser.ConfigParser()
            parser.read_string(s)
            return {section: dict(parser.items(section)) for section in parser.sections()}

        return self.parse_content(
            content_string=ini_string,
            parser_func=parser_func,
            expected_language='ini',
            exception_class=configparser.Error
        )

    def parse_csv_content(self, csv_string: str) -> Optional[List[Dict[str, Any]]]:
        """
        Parses a CSV-formatted string into a list of dictionaries.

        Parameters:
            csv_string (str): The CSV string to parse.

        Returns:
            Optional[List[Dict[str, Any]]]: The parsed CSV content as a list of dictionaries, or None if parsing fails.
        """
        def parser_func(s):
            reader = csv.DictReader(StringIO(s))
            return [row for row in reader]

        return self.parse_content(
            content_string=csv_string,
            parser_func=parser_func,
            expected_language='csv',
            exception_class=csv.Error
        )
