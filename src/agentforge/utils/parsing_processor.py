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
    DEFAULT_CODE_FENCES = ["```", "~~~"]

    def __init__(self):
        self.logger = Logger(name=self.__class__.__name__, default_logger=self.__class__.__name__.lower())
        self.default_code_fences = self.DEFAULT_CODE_FENCES
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

    def get_code_fences(self, code_fences: Optional[List[str]] = None) -> List[str]:
        return code_fences if code_fences is not None else self.default_code_fences

    def extract_code_block(self, text: str, code_fences: Optional[List[str]] = None) -> Tuple[Optional[str], str]:
        code_fences = self.get_code_fences(code_fences)
        for fence in code_fences:
            escaped_fence = re.escape(fence)
            # Look for an optional language specifier, a newline, then everything until the closing fence.
            pattern = fr"{escaped_fence}([a-zA-Z]*)\r?\n([\s\S]*?){escaped_fence}"
            match = re.search(pattern, text, re.DOTALL)
            if match:
                language = match.group(1).strip() or None
                content = match.group(2).strip()
                return language, content
        return None, text.strip()

    def parse_content(self, content_string: str, parser_func: Callable[[str], Any],
                      expected_language: str, code_fences: Optional[List[str]] = None) -> Any:
        code_fences = self.get_code_fences(code_fences)
        language, cleaned_string = self.extract_code_block(content_string, code_fences)
        if language and language.lower() != expected_language.lower():
            self.logger.log(f"Expected {expected_language.upper()} code block, but found '{language}'", 'warning')
        if cleaned_string:
            try:
                return parser_func(cleaned_string)
            except Exception as e:
                self.logger.log(f"Parsing error: {e}\nContent: {content_string}", 'error')
                raise ParsingError(e) from e
        return None

    def parse_by_format(self, content_string: str, parser_type: str, code_fences: Optional[List[str]] = None) -> Any:
        code_fences = self.get_code_fences(code_fences)
        parser = self.parsers.get(parser_type.lower())
        if parser:
            return parser(content_string, code_fences)
        self.logger.log(f"No parser method found for type '{parser_type}'", 'error')
        raise ParsingError(f"No parser method found for type '{parser_type}'")

    def auto_parse_content(self, text: str, code_fences: Optional[List[str]] = None) -> Any:
        code_fences = self.get_code_fences(code_fences)
        language, content = self.extract_code_block(text, code_fences)
        if language and language.lower() in self.list_supported_formats():
            return self.parse_by_format(content, language, code_fences=code_fences)
        self.logger.log("No valid language detected for automatic parsing, returning raw text instead.", "warning")
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
    def parse_markdown_to_dict(markdown_text: str, min_heading_level=2, max_heading_level=6) -> Optional[Dict[str, Any]]:
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



# import re
# import json
# import yaml
# from typing import Optional, Dict, Any, Callable, Type, List, Tuple
# from agentforge.utils.logger import Logger
# import xmltodict
# import configparser
# import csv
# from io import StringIO
#
# class ParsingProcessor:
#
#     def __init__(self):
#         """
#         Initializes the ParsingProcessor class.
#         """
#         name = self.__class__.__name__.__str__()
#         self.logger = Logger(name=name, default_logger=name)
#
#     def auto_parse_content(self, text: str, code_fences: Optional[List[str]] = None) -> Any:
#         if code_fences is None:
#             code_fences = ["```", "~~~"]
#         language, content = self.extract_code_block(text, code_fences=code_fences)
#         if language and language.lower() in self.list_supported_formats():
#             return self.parse_by_format(content, language, code_fences=code_fences)
#
#         self.logger.log("No valid language detected for automatic parsing, returning raw text instead.", "warning")
#         return text
#
#     def extract_code_block(self, text: str, code_fences: Optional[List[str]] = None) -> Optional[Tuple[Optional[str], str]]:
#         """
#         Extracts a code block from a string using one of the specified code fence delimiters.
#         Iterates through the provided list of code fences (defaulting to ["```"]) and returns the first matching
#         code block along with its language specifier. If no code block is found, returns the original text.
#         """
#         if code_fences is None:
#             code_fences = ["```", "~~~"]
#         try:
#             for fence in code_fences:
#                 escaped_fence = re.escape(fence)
#                 code_block_pattern = fr"{escaped_fence}([a-zA-Z]*)\r?\n([\s\S]*?){escaped_fence}"
#                 match = re.search(code_block_pattern, text, re.DOTALL)
#                 if match:
#                     language = match.group(1).strip() or None
#                     content = match.group(2).strip()
#                     return language, content
#             return None, text.strip()
#         except Exception as e:
#             self.logger.log(f"Regex Error Extracting Code Block: {e}", 'error')
#             return None
#
#     def parse_content(self, content_string: str, parser_func: Callable[[str], Any],
#                       expected_language: str, exception_class: Type[Exception],
#                       code_fences: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
#         """
#         A generic method to parse content using a specified parser function.
#         """
#         if code_fences is None:
#             code_fences = ["```", "~~~"]
#         try:
#             language, cleaned_string = self.extract_code_block(content_string, code_fences=code_fences)
#             if language and language.lower() != expected_language.lower():
#                 self.logger.log(f"Expected {expected_language.upper()} code block, but found '{language}'", 'warning')
#
#             if cleaned_string:
#                 return parser_func(cleaned_string)
#             return None
#         except exception_class as e:
#             self.logger.log(f"Parsing error: {e}\n"
#                             f"Content: {content_string}", 'error')
#             return None
#         except Exception as e:
#             self.logger.log(f"Unexpected error parsing {expected_language.upper()} content: {e}", 'error')
#             return None
#
#     def parse_by_format(self, content_string: str, parser_type: str, code_fences: Optional[List[str]] = None) -> Any:
#         if code_fences is None:
#             code_fences = ["```", "~~~"]
#         parser_method_name = f"parse_{parser_type.lower()}_content"
#         parser_method = getattr(self, parser_method_name, None)
#         if callable(parser_method):
#             return parser_method(content_string, code_fences=code_fences)
#         else:
#             self.logger.log(f"No parser method found for type '{parser_type}'", 'error')
#             return None
#
#     def parse_markdown_content(self, markdown_string: str, min_heading_level=2, max_heading_level=6, code_fences: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
#         """
#         Parses a Markdown-formatted string into a Python dictionary.
#         """
#         def parser_func(s):
#             return self.parse_markdown_to_dict(s, min_heading_level, max_heading_level)
#
#         return self.parse_content(
#             content_string=markdown_string,
#             parser_func=parser_func,
#             expected_language='markdown',
#             exception_class=Exception,
#             code_fences=code_fences
#         )
#
#     def parse_yaml_content(self, yaml_string: str, code_fences: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
#         """
#         Parses a YAML-formatted string into a Python dictionary.
#         """
#         return self.parse_content(
#             content_string=yaml_string,
#             parser_func=yaml.safe_load,
#             expected_language='yaml',
#             exception_class=yaml.YAMLError,
#             code_fences=code_fences
#         )
#
#     def parse_json_content(self, json_string: str, code_fences: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
#         """
#         Parses a JSON-formatted string into a Python dictionary.
#         """
#         return self.parse_content(
#             content_string=json_string,
#             parser_func=json.loads,
#             expected_language='json',
#             exception_class=json.JSONDecodeError,
#             code_fences=code_fences
#         )
#
#     def parse_xml_content(self, xml_string: str, code_fences: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
#         """
#         Parses an XML-formatted string into a Python dictionary.
#         """
#         return self.parse_content(
#             content_string=xml_string,
#             parser_func=xmltodict.parse,
#             expected_language='xml',
#             exception_class=Exception,
#             code_fences=code_fences
#         )
#
#     def parse_ini_content(self, ini_string: str, code_fences: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
#         """
#         Parses an INI-formatted string into a Python dictionary.
#         """
#         def parser_func(s):
#             parser = configparser.ConfigParser()
#             parser.read_string(s)
#             return {section: dict(parser.items(section)) for section in parser.sections()}
#
#         return self.parse_content(
#             content_string=ini_string,
#             parser_func=parser_func,
#             expected_language='ini',
#             exception_class=configparser.Error,
#             code_fences=code_fences
#         )
#
#     def parse_csv_content(self, csv_string: str, code_fences: Optional[List[str]] = None) -> Optional[List[Dict[str, Any]]]:
#         """
#         Parses a CSV-formatted string into a list of dictionaries.
#         """
#         def parser_func(s):
#             reader = csv.DictReader(StringIO(s))
#             return [row for row in reader]
#
#         return self.parse_content(
#             content_string=csv_string,
#             parser_func=parser_func,
#             expected_language='csv',
#             exception_class=csv.Error,
#             code_fences=code_fences
#         )
#
#     @staticmethod
#     def list_supported_formats():
#         return ['xml', 'json', 'yaml', 'ini', 'csv', 'markdown']
#
#     @staticmethod
#     def parse_markdown_to_dict(markdown_text: str, min_heading_level=2, max_heading_level=6) -> Optional[Dict[str, Any]]:
#         """
#         Parses a markdown-formatted string into a dictionary, mapping each heading to its corresponding content.
#         """
#         parsed_dict = {}
#         current_heading = None
#         content_lines = []
#
#         heading_pattern = re.compile(r'^(#{%d,%d})\s+(.*)' % (min_heading_level, max_heading_level))
#
#         lines = markdown_text.split('\n')
#         for line in lines:
#             match = heading_pattern.match(line)
#             if match:
#                 if current_heading is not None:
#                     parsed_dict[current_heading] = '\n'.join(content_lines).strip()
#                     content_lines = []
#                 current_heading = match.group(2).strip()
#             else:
#                 if current_heading is not None:
#                     content_lines.append(line)
#         if current_heading is not None:
#             parsed_dict[current_heading] = '\n'.join(content_lines).strip()
#
#         return parsed_dict if parsed_dict else None


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