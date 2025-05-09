import re
import json
import yaml
from typing import Optional, Dict, Any, Callable, List, Tuple
from agentforge.utils.logger import Logger
import xmltodict
import configparser
import csv
from io import StringIO


class ParsingError(Exception):
    """Custom exception for parsing errors."""
    pass


class ParsingProcessor:
    def __init__(self):
        self.logger = Logger(name=self.__class__.__name__, default_logger=self.__class__.__name__.lower())
        self._define_parsers()

    def _define_parsers(self):
        # Central parser dispatcher mapping format to a lambda that takes the content string and code fences.
        self.parsers: Dict[str, Callable[[str, Optional[List[str]]], Any]] = {
            'json': lambda s, fences: self.parse_content(s, json.loads, 'json', code_fences=fences),
            'yaml': lambda s, fences: self.parse_content(s, yaml.safe_load, 'yaml', code_fences=fences),
            'xml': lambda s, fences: self.parse_content(s, xmltodict.parse, 'xml', code_fences=fences),
            'ini': lambda s, fences: self.parse_content(s, self._parse_ini, 'ini', code_fences=fences),
            'csv': lambda s, fences: self.parse_content(s, self._parse_csv, 'csv', code_fences=fences),
            'markdown': lambda s, fences: self.parse_content(
                s, lambda t: self.parse_markdown_to_dict(t, 2, 6), 'markdown', code_fences=fences)
        }

    def extract_code_block(self, text: str, code_fences: List[str] = []) -> Tuple[Optional[str], str]:
        """
        Extract a code block from text, returning the language and content.
        
        Args:
            text: The text containing code blocks
            code_fences: List of fence markers to use (default: empty list)
            
        Returns:
            Tuple of (language, content)
        """
        # Early exit if no code fences provided
        if not code_fences:
            return None, text.strip()
        
        # First try standard fence pattern matching
        for fence in code_fences:
            escaped_fence = re.escape(fence)
            # Match fenced code blocks with language specifier
            pattern = fr"{escaped_fence}([a-zA-Z]*)[ \t]*\r?\n?([\s\S]*?){escaped_fence}"
            match = re.search(pattern, text, re.DOTALL)
            if match:
                language = match.group(1).strip() or None
                content = match.group(2).strip()
                return language, content

            # Also try handling no-language blocks with just the fence
            pattern = fr"{escaped_fence}\s*\r?\n([\s\S]*?){escaped_fence}"
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return None, match.group(1).strip()
        
        # No code blocks found with standard patterns
        return None, text.strip()

    def sanitize_yaml_content(self, content: str, 
                             primary_fence: str = None, 
                             alternate_fence: str = None) -> str:
        """
        Sanitize YAML content by handling nested code blocks.
        
        Args:
            content: The YAML content to sanitize
            primary_fence: The main fence to replace
            alternate_fence: The replacement fence
        """
        if not primary_fence or not alternate_fence:
            return content.strip()
        
        def replace_inner_fences(match):
            inner_block = match.group(0)
            return inner_block.replace(primary_fence, alternate_fence)
        
        # Pattern based on primary fence
        pattern = fr"{re.escape(primary_fence)}[a-zA-Z]*\s*\r?\n[\s\S]*?{re.escape(primary_fence)}"
        content = re.sub(pattern, replace_inner_fences, content)
        
        # Then handle any other sanitization
        if content.strip().startswith('```'):
            content = re.sub(r'^```.*?\n', '', content, flags=re.DOTALL)
            content = re.sub(r'```\s*$', '', content)
            self.logger.log("Removed outer code blocks in YAML content", 'warning')
        
        return content.strip()

    def parse_content(self, content_string: str, parser_func: Callable[[str], Any],
                      expected_language: str, code_fences: List[str] = []) -> Any:
        language, cleaned_string = self.extract_code_block(content_string, code_fences)
        
        if language and language.lower() != expected_language.lower():
            self.logger.log(f"Expected {expected_language.upper()} code block, but found '{language}'", 'warning')
            
        if cleaned_string:
            try:
                # Apply format-specific preprocessing
                if expected_language.lower() == 'yaml':
                    cleaned_string = self.sanitize_yaml_content(cleaned_string)
                
                return parser_func(cleaned_string)
            except Exception as e:
                # Log a more detailed error with a preview of the content
                preview = cleaned_string[:100] + ('...' if len(cleaned_string) > 100 else '')
                self.logger.log(f"Parsing error: {str(e)}\nContent preview: {preview}", 'error')
                self.logger.log(f"Content type: {expected_language}, Content length: {len(cleaned_string)}", 'error')

                # Try alternative parsing approaches for common error cases
                if expected_language.lower() == 'yaml':
                    try:
                        # More aggressive YAML cleanup as a last resort
                        cleaned_again = re.sub(r'[`~]', '', cleaned_string)  # Remove any remaining backticks
                        self.logger.log("Attempting alternative YAML parsing after aggressive cleanup", 'info')
                        return parser_func(cleaned_again)
                    except Exception as e2:
                        self.logger.log(f"Alternative parsing also failed: {e2}", 'error')

                raise ParsingError(f"Failed to parse {expected_language}: {e}") from e
        return None

    def parse_by_format(self, content_string: str, parser_type: str, code_fences: List[str] = []) -> Any:
        parser = self.parsers.get(parser_type.lower())
        if parser:
            return parser(content_string, code_fences)
        self.logger.log(f"No parser method found for type '{parser_type}'", 'error')
        raise ParsingError(f"No parser method found for type '{parser_type}'")

    def auto_parse_content(self, text: str, code_fences: List[str] = []) -> Any:
        language, content = self.extract_code_block(text, code_fences)
        if language and language.lower() in self.list_supported_formats():
            return self.parse_by_format(content, language, code_fences=code_fences)
        self.logger.log("No valid language detected for automatic parsing, returning raw text instead.", "debug")
        return text

    @staticmethod
    def _parse_ini(s: str) -> Dict[str, Any]:
        parser = configparser.ConfigParser()
        parser.read_string(s)
        return {section: dict(parser.items(section)) for section in parser.sections()}

    @staticmethod
    def _parse_csv(s: str) -> List[Dict[str, Any]]:
        reader = csv.DictReader(StringIO(s))
        return list(reader)

    @staticmethod
    def list_supported_formats():
        return ['xml', 'json', 'yaml', 'ini', 'csv', 'markdown']

    @staticmethod
    def parse_markdown_to_dict(markdown_text: str, min_heading_level=2, max_heading_level=6) -> Optional[
        Dict[str, Any]]:
        parsed_dict = {}
        current_heading = None
        content_lines = []
        heading_pattern = re.compile(r'^(#{%d,%d})\s+(.*)' % (min_heading_level, max_heading_level))
        for line in markdown_text.split('\n'):
            match = heading_pattern.match(line)
            if match:
                if current_heading is not None:
                    parsed_dict[current_heading] = '\n'.join(content_lines).strip()
                    content_lines = []
                current_heading = match.group(2).strip()
            else:
                if current_heading is not None:
                    content_lines.append(line)
        if current_heading is not None:
            parsed_dict[current_heading] = '\n'.join(content_lines).strip()
        return parsed_dict if parsed_dict else None

    def format_string(self, input_str):
        """
        Formats a string to meet requirements of chroma collection name. Performs the following steps in order:

        Remove leading and trailing whitespace
        Replace non-alphanumeric
        Replace consecutive periods
        Ensure not a valid IPv4
        Ensure it starts with an alphanumeric character
        Ensure it ends with an alphanumeric character
        Ensure length is at least 3 characters
        Ensure length is not more than 64 characters
        Lower casing string

        Parameters:
        - input_str (str): The string to format.

        Returns:
        - str: The formatted string.
        """

        self.logger.log(f"Formatting string:\n{input_str}", 'debug', 'Formatting')
        # Remove leading and trailing whitespace
        input_str = input_str.strip()
        self.logger.log(f"Remove leading and trailing whitespace:\n{input_str}", 'debug', 'Formatting')

        # Replace non-alphanumeric, non-underscore, non-hyphen characters with underscores
        input_str = re.sub("[^a-zA-Z0-9_-]", "_", input_str)
        self.logger.log(f"Replacing non-alphanumeric:\n{input_str}", 'debug', 'Formatting')

        # Replace consecutive periods with a single period
        while ".." in input_str:
            input_str = input_str.replace("..", ".")
            self.logger.log(f"Replacing consecutive periods:\n{input_str}", 'debug', 'Formatting')

        # Ensure it's not a valid IPv4 address
        if re.match(r'^\d+\.\d+\.\d+\.\d+$', input_str):
            input_str = "a" + input_str
            self.logger.log(f"Ensuring not a valid IPv4:\n{input_str}", 'debug', 'Formatting')

        # Ensure it starts and ends with an alphanumeric character
        if not input_str[0].isalnum():
            input_str = "a" + input_str[1:]
            self.logger.log(f"Ensure it starts with an alphanumeric character:\n{input_str}", 'debug', 'Formatting')
        if not input_str[-1].isalnum():
            input_str = input_str[:-1] + "a"
            self.logger.log(f"Ensure it ends with an alphanumeric character:\n{input_str}", 'debug', 'Formatting')

        # Ensure length is between 3 and 64 characters
        while len(input_str) < 3:
            input_str += input_str
            self.logger.log(f"Ensure length is at least 3 characters:\n{input_str}", 'debug', 'Formatting')
        if len(input_str) > 63:
            input_str = input_str[:63]
            self.logger.log(f"Ensure length is not more than 64 characters:\n{input_str}", 'debug', 'Formatting')

        input_str = input_str.lower()
        self.logger.log(f"Lower casing string:\n{input_str}", 'debug', 'Formatting')

        return input_str
