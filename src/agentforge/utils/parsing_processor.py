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
    """
    A robust parsing processor that supports multiple serialization formats with two-stage parsing.
    
    The ParsingProcessor implements a two-stage parsing approach for all supported formats:
    1. Code-fenced parsing: First attempts to extract and parse content from code blocks
    2. Bare parsing fallback: If code-fenced parsing fails, attempts to parse the entire content
    
    Supported formats: JSON, YAML, XML, INI, CSV, Markdown
    
    Features:
    - Robust error handling with detailed logging
    - Support for both fenced and unfenced agent outputs
    - Format-specific preprocessing (e.g., YAML sanitization)
    - Comprehensive debug logging for troubleshooting
    - Default code fence extraction using triple backticks (['```'])
    """
    
    # Default code fences to use for extraction - can be overridden by passing code_fences parameter
    DEFAULT_CODE_FENCES = ['```']
    
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

    def extract_code_block(self, text: str, code_fences: Optional[List[str]] = None) -> Tuple[Optional[str], str]:
        """
        Extract the first code block from text, returning the language and content.
        
        This method is used in the first stage of the two-stage parsing approach.
        If no code fences are found, returns the entire stripped text for fallback parsing.
        
        Args:
            text: The text containing potential code blocks
            code_fences: List of fence markers to use. If None, uses DEFAULT_CODE_FENCES (['```']).
                        Pass an empty list [] to disable code fence extraction and return full text.
            
        Returns:
            Tuple of (language, content) where:
            - language: The detected language specifier (or None if not found/specified)
            - content: The extracted code block content or stripped full text if no fence found
        """
        # Use default code fences if None provided, otherwise use the provided list (including empty list)
        if code_fences is None:
            code_fences = self.DEFAULT_CODE_FENCES
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
            self.logger.warning("Removed outer code blocks in YAML content")
        
        return content.strip()

    @staticmethod
    def preprocess_json_string(s: str) -> str:
        """
        Preprocess a string to increase the chance of successful JSON parsing from LLM outputs.
        - Trims whitespace
        - Extracts the first JSON object if stray text is present
        - Removes trailing commas in objects/arrays
        - Double-escapes backslashes not already escaped (for LaTeX/math)
        """
        import re
        s = s.strip()
        # Extract the first JSON object (handles stray text)
        match = re.search(r'(\{.*\})', s, re.DOTALL)
        if match:
            s = match.group(1)
        # Remove trailing commas in objects/arrays
        s = re.sub(r',([ \t\r\n]*[}\]])', r'\1', s)
        # Double-escape backslashes that are not already double-escaped
        s = re.sub(r'(?<!\\)\\(?![\\/\"bfnrtu])', r'\\\\', s)
        return s

    def parse_content(self, content_string: str, parser_func: Callable[[str], Any],
                      expected_language: str, code_fences: Optional[List[str]] = None) -> Any:
        """
        Parse content using a two-stage approach: code-fenced first, then bare parsing fallback.
        
        Args:
            content_string: The input string to parse
            parser_func: The function to use for parsing (e.g., json.loads, yaml.safe_load)
            expected_language: The expected language/format type
            code_fences: List of fence markers to look for. If None, uses DEFAULT_CODE_FENCES (['```']).
                        Pass an empty list [] to disable code fence extraction and parse full content.
            
        Returns:
            Parsed content or None if parsing fails
        """
        # Use default code fences if None provided
        if code_fences is None:
            code_fences = self.DEFAULT_CODE_FENCES
        
        # Stage 1: Try code-fenced parsing
        language, extracted_content = self.extract_code_block(content_string, code_fences)
        
        # Log the code-fenced extraction attempt
        if language is not None:
            self.logger.debug(f"Code-fenced block detected with language '{language}' for {expected_language.upper()} parsing")
        elif code_fences:
            self.logger.debug(f"No code-fenced block found using fences {code_fences}, extracted content length: {len(extracted_content)}")
        else:
            self.logger.debug(f"No code fences specified, proceeding with full content for {expected_language.upper()} parsing")
        
        # Check language match and warn if different
        if language and language.lower() != expected_language.lower():
            self.logger.warning(f"Expected {expected_language.upper()} code block, but found '{language}'")
        
        # Attempt to parse the extracted (code-fenced) content
        if extracted_content:
            try:
                processed_content = extracted_content
                if expected_language.lower() == 'yaml':
                    processed_content = self.sanitize_yaml_content(extracted_content)
                if expected_language.lower() == 'json':
                    processed_content = self.preprocess_json_string(processed_content)
                    self.logger.debug(f"Cleaned JSON string before parsing (first 500 chars): {processed_content[:500]}")
                self.logger.debug(f"Attempting code-fenced {expected_language.upper()} parsing on content of length {len(processed_content)}")
                result = parser_func(processed_content)
                self.logger.debug(f"Code-fenced {expected_language.upper()} parsing succeeded")
                return result
                
            except Exception as e:
                # Log the code-fenced parsing failure
                preview = processed_content[:100] + ('...' if len(processed_content) > 100 else '')
                self.logger.warning(f"Code-fenced {expected_language.upper()} parsing failed: {str(e)}")
                self.logger.debug(f"Failed content preview: {preview}")
                if expected_language.lower() == 'json':
                    self.logger.error(f"Cleaned JSON string on failure (first 500 chars): {processed_content[:500]}")
                
                # Stage 2: Fallback to bare parsing if code-fenced parsing failed
                # Only attempt if we had extracted a code block and it failed
                if language is not None or code_fences:
                    return self._attempt_bare_parsing(content_string, parser_func, expected_language)
                else:
                    # If no code fences were specified, don't try again
                    raise ParsingError(f"Failed to parse {expected_language}: {e}") from e
        
        # If no content was extracted, attempt bare parsing
        return self._attempt_bare_parsing(content_string, parser_func, expected_language)
    
    def _attempt_bare_parsing(self, content_string: str, parser_func: Callable[[str], Any], 
                            expected_language: str) -> Any:
        """
        Attempt to parse the entire content string as the expected format (bare parsing).
        
        Args:
            content_string: The full input string
            parser_func: The parsing function to use
            expected_language: The expected format type
            
        Returns:
            Parsed content or raises ParsingError if parsing fails
        """
        
        stripped_content = content_string.strip()
        self.logger.info(f"Attempting bare {expected_language.upper()} parsing fallback on full content (length: {len(stripped_content)})")
        
        try:
            # Apply format-specific preprocessing for bare content too
            processed_content = stripped_content
            if expected_language.lower() == 'yaml':
                processed_content = self.sanitize_yaml_content(stripped_content)
            
            result = parser_func(processed_content)
            self.logger.info(f"Bare {expected_language.upper()} parsing fallback succeeded")
            return result
            
        except Exception as e:
            # Log the bare parsing failure
            preview = processed_content[:100] + ('...' if len(processed_content) > 100 else '')
            self.logger.error(f"Bare {expected_language.upper()} parsing fallback failed: {str(e)}")
            self.logger.debug(f"Failed content preview: {preview}")
            self.logger.error(f"Content type: {expected_language}, Content length: {len(processed_content)}")
            
            # Special handling for YAML auto-cleanup (keeping existing behavior as requested)
            if expected_language.lower() == 'yaml':
                try:
                    # More aggressive YAML cleanup as a last resort
                    cleaned_content = re.sub(r'[`~]', '', processed_content)  # Remove any remaining backticks
                    self.logger.info("Attempting alternative YAML parsing after aggressive cleanup")
                    result = parser_func(cleaned_content)
                    self.logger.info("Alternative YAML parsing succeeded")
                    return result
                except Exception as e2:
                    self.logger.error(f"Alternative YAML parsing also failed: {e2}")
            
            raise ParsingError(f"Failed to parse {expected_language}: {e}") from e

    def parse_by_format(self, content_string: str, parser_type: Optional[str], code_fences: Optional[List[str]] = None) -> Any:
        """
        Parse content using the specified format with two-stage parsing approach.
        
        This method uses the two-stage parsing approach:
        1. First attempts to extract and parse content from code blocks (using DEFAULT_CODE_FENCES by default)
        2. Falls back to parsing the entire content as the specified format if stage 1 fails
        
        Args:
            content_string: The input string to parse
            parser_type: The format type to parse (json, yaml, xml, ini, csv, markdown), or None to return content unchanged
            code_fences: List of fence markers to look for. If None, uses DEFAULT_CODE_FENCES (['```']).
                        Pass an empty list [] to disable code fence extraction and parse full content.
            
        Returns:
            Parsed content in the appropriate Python data structure, or the original content_string if parser_type is None
            
        Raises:
            ParsingError: If the format is unsupported or parsing fails completely
        """
        # If parser_type is None or empty, return the content unchanged
        if not parser_type:
            return content_string
            
        # Explicitly set default code fences when None is provided
        if code_fences is None:
            code_fences = self.DEFAULT_CODE_FENCES
            
        parser = self.parsers.get(parser_type.lower())
        if parser:
            return parser(content_string, code_fences)
        self.logger.error(f"No parser method found for type '{parser_type}'")
        raise ParsingError(f"No parser method found for type '{parser_type}'")

    def auto_parse_content(self, text: str, code_fences: Optional[List[str]] = None) -> Any:
        """
        Automatically parse content by detecting the language from code fences.
        
        Args:
            text: The input text to parse
            code_fences: List of fence markers to look for. If None, uses DEFAULT_CODE_FENCES (['```']).
                        Pass an empty list [] to disable code fence extraction.
                        
        Returns:
            Parsed content if a supported language is detected, otherwise returns the raw text.
        """
        # Explicitly set default code fences when None is provided
        if code_fences is None:
            code_fences = self.DEFAULT_CODE_FENCES
            
        language, content = self.extract_code_block(text, code_fences)
        if language and language.lower() in self.list_supported_formats():
            return self.parse_by_format(content, language, code_fences=code_fences)
        self.logger.debug("No valid language detected for automatic parsing, returning raw text instead.")
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
    def get_dot_notated(source: dict, key: str):
        """
        Helper to get a value from a dict using dot notation (e.g., 'foo.bar.baz').
        Returns None if any part of the path is missing.
        
        Args:
            source: Source dictionary
            key: Dot-notated key string
            
        Returns:
            Value at the specified path, or None if not found
        """
        if not isinstance(source, dict):
            return None
        parts = key.split('.')
        current = source
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current

    @staticmethod
    def flatten_dict(d: dict, parent_key: str = '', sep: str = '.') -> dict:
        """
        Flattens a nested dictionary.

        Args:
            d (dict): The dictionary to flatten.
            parent_key (str): The parent key (used for recursion).
            sep (str): The separator to use between keys.

        Returns:
            dict: The flattened dictionary.
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(ParsingProcessor.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

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

        self.logger.debug(f"Formatting string:\n{input_str}")
        # Remove leading and trailing whitespace
        input_str = input_str.strip()
        self.logger.debug(f"Remove leading and trailing whitespace:\n{input_str}")

        # Replace non-alphanumeric, non-underscore, non-hyphen characters with underscores
        input_str = re.sub("[^a-zA-Z0-9_-]", "_", input_str)
        self.logger.debug(f"Replacing non-alphanumeric:\n{input_str}")

        # Replace consecutive periods with a single period
        while ".." in input_str:
            input_str = input_str.replace("..", ".")
            self.logger.debug(f"Replacing consecutive periods:\n{input_str}")

        # Ensure it's not a valid IPv4 address
        if re.match(r'^\d+\.\d+\.\d+\.\d+$', input_str):
            input_str = "a" + input_str
            self.logger.debug(f"Ensuring not a valid IPv4:\n{input_str}")

        # Ensure it starts and ends with an alphanumeric character
        if not input_str[0].isalnum():
            input_str = "a" + input_str[1:]
            self.logger.debug(f"Ensure it starts with an alphanumeric character:\n{input_str}")
        if not input_str[-1].isalnum():
            input_str = input_str[:-1] + "a"
            self.logger.debug(f"Ensure it ends with an alphanumeric character:\n{input_str}")

        # Ensure length is between 3 and 64 characters
        while len(input_str) < 3:
            input_str += input_str
            self.logger.debug(f"Ensure length is at least 3 characters:\n{input_str}")
        if len(input_str) > 63:
            input_str = input_str[:63]
            self.logger.debug(f"Ensure length is not more than 64 characters:\n{input_str}")

        input_str = input_str.lower()
        self.logger.debug(f"Lower casing string:\n{input_str}")

        return input_str

    @staticmethod
    def flatten_to_string_list(data) -> list[str]:
        """
        Recursively flattens any dict or list into a list of 'key: value' strings, where keys are dot/bracket notated paths.
        This is used to serialize memory updates for ChromaDB, ensuring all data is stored as flat strings.
        Example: {'a': {'b': [1, 2]}} -> ['a.b[0]: 1', 'a.b[1]: 2']
        """
        def _flatten(obj, parent_key=''):
            items = []
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_key = f"{parent_key}.{k}" if parent_key else k
                    items.extend(_flatten(v, new_key))
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    new_key = f"{parent_key}[{i}]"
                    items.extend(_flatten(v, new_key))
            else:
                items.append((parent_key, obj))
            return items

        flat = _flatten(data)
        return [f"{k}: {v}" for k, v in flat]
