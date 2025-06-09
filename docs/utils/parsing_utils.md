# Parsing Processor Guide

In **AgentForge**, the `ParsingProcessor` class provides robust methods for extracting and parsing structured data from text. It supports YAML, JSON, XML, INI, CSV, and Markdown, with a focus on reliability and clear error handling.

---

## Overview

`ParsingProcessor` helps agents and system components interpret text that may contain structured data. It features:

1. **Code Block Extraction**: Locates code fences (optionally with a language specifier) and returns their contents.
2. **Multi-Format Parsing**: Converts YAML, JSON, XML, INI, CSV, and Markdown to Python data structures.
3. **Logging and Error Handling**: Uses a built-in logger to record parsing attempts, warnings, and failures.

---

## Main Methods

### 1. `extract_code_block(text: str, code_fences: Optional[List[str]] = None) -> Tuple[Optional[str], str]`

**Purpose**  
Extracts the first matching code block using the specified list of `code_fences` delimiters. Returns a tuple `(language, content)` or `(None, text.strip())` if no code block is found.

**Parameters**
- `text` (`str`): The input string containing potential code fences.
- `code_fences` (`Optional[List[str]]`): List of fence markers to use (default is triple backticks: ['```']).

**Example**:
~~~python
from agentforge.utils.parsing_processor import ParsingProcessor

processor = ParsingProcessor()
text_with_code = """
Here is some content.

```python
print("Hello, world!")
```
"""

lang, code = processor.extract_code_block(text_with_code)
print(lang)  # "python"
print(code)  # 'print("Hello, world!")'
~~~

---

### 2. `parse_by_format(content_string: str, parser_type: Optional[str], code_fences: Optional[List[str]] = None) -> Any`

**Purpose**  
Parses content using the specified format (e.g., 'json', 'yaml', 'xml', 'ini', 'csv', 'markdown') with a two-stage approach: code-fenced parsing first, then fallback to bare parsing.

**Parameters**
- `content_string` (`str`): The input string to parse.
- `parser_type` (`Optional[str]`): The format to parse ('json', 'yaml', etc.).
- `code_fences` (`Optional[List[str]]`): List of code fence markers (default is ['```']).

**Returns**
- Parsed content as a Python data structure, or the original string if `parser_type` is `None`.

**Raises**
- `ParsingError` if parsing fails and no fallback is possible.

**Example**:
~~~python
yaml_text = """
```yaml
name: AgentForge
version: 1.0
```
"""
parsed = processor.parse_by_format(yaml_text, 'yaml')
print(parsed)  # {'name': 'AgentForge', 'version': 1.0}
~~~

---

### 3. `auto_parse_content(text: str, code_fences: Optional[List[str]] = None) -> Any`

**Purpose**  
Automatically detects the language from code fences and parses the content if supported. Returns the parsed content or the raw text if no supported language is detected.

**Example**:
~~~python
json_text = """
```json
{"foo": 42}
```
"""
parsed = processor.auto_parse_content(json_text)
print(parsed)  # {'foo': 42}
~~~

---

### 4. `sanitize_yaml_content(content: str, primary_fence: str = None, alternate_fence: str = None) -> str`

**Purpose**  
Sanitizes YAML content by handling nested code blocks and removing outer code fences if present.

---

### 5. `preprocess_json_string(s: str) -> str`

**Purpose**  
Preprocesses a string to increase the chance of successful JSON parsing (trims whitespace, extracts first JSON object, removes trailing commas, double-escapes backslashes).

---

### 6. `flatten_dict(d: dict, parent_key: str = '', sep: str = '.') -> dict`

**Purpose**  
Flattens a nested dictionary into a single-level dict with dot-notated keys.

---

### 7. `flatten_to_string_list(data) -> List[str]`

**Purpose**  
Recursively flattens any dict or list into a list of 'key: value' strings, using dot/bracket notation for keys.

---

### 8. `get_dot_notated(source: dict, key: str)`

**Purpose**  
Retrieves a value from a dict using dot notation (e.g., 'foo.bar.baz'). Returns `None` if not found.

---

### 9. `format_string(input_str: str) -> str`

**Purpose**  
Formats a string to meet requirements for chroma collection names (removes whitespace, replaces non-alphanumeric chars, ensures length, etc.).

---

### 10. `parse_markdown_to_dict(markdown_text: str, min_heading_level=2, max_heading_level=6) -> Optional[Dict[str, Any]]`

**Purpose**  
Parses Markdown-formatted text, extracting headings and mapping each heading to its associated content in a dictionary.

---

## Error Handling

- If parsing fails, a `ParsingError` may be raised. All parsing attempts are logged for debugging.

---

## Usage Example

~~~python
from agentforge.utils.parsing_processor import ParsingProcessor, ParsingError

processor = ParsingProcessor()
json_text = """
```json
{"name": "AgentForge", "features": ["Custom Agents", "Utilities"]}
```
"""
try:
    parsed = processor.parse_by_format(json_text, 'json')
    print(parsed)
except ParsingError as e:
    print("Parsing failed:", e)
~~~
