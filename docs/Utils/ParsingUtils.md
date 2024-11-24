# Parsing Utility Guide

## Introduction

The `ParsingUtils` class in **AgentForge** provides a suite of utility methods for parsing various types of structured text content into Python data structures. This utility is essential for agents and applications that need to interpret or manipulate configuration data, agent responses, or any dynamic content expressed in formats such as **YAML**, **JSON**, **XML**, **INI**, **CSV**, or **Markdown**.

---

## Overview

The `ParsingUtils` class offers the following key functionalities:

- **Extracting Code Blocks**: Identifies and extracts content from code blocks within larger text blocks, supporting multiple languages.
- **Parsing YAML Content**: Parses YAML-formatted strings into Python dictionaries.
- **Parsing JSON Content**: Parses JSON-formatted strings into Python dictionaries.
- **Parsing XML Content**: Parses XML-formatted strings into Python dictionaries.
- **Parsing INI Content**: Parses INI-formatted strings into Python dictionaries.
- **Parsing CSV Content**: Parses CSV-formatted strings into lists of dictionaries.
- **Parsing Markdown Content**: Parses Markdown-formatted strings, extracting headings and their associated content into a dictionary.

---

## Methods

### 1. `extract_code_block(text: str) -> Optional[Tuple[str, Optional[str]]]`

**Purpose**: Extracts the content of a code block from a given text and returns the language specifier if present. Supports code blocks with or without a language specifier. If multiple code blocks are present, returns the outermost one.

**Parameters**:

- `text` (str): The text containing the code block.

**Returns**:

- `Optional[Tuple[str, Optional[str]]]`: A tuple containing the extracted code block content and the language specifier (or `None` if not specified).

**Example Usage**:

~~~python
from agentforge.utils.ParsingProcessor import ParsingProcessor

parsing_utils = ParsingProcessor()

text_with_code_block = '''
Here is some text.

```python
def hello_world():
    print("Hello, World!")
```

End of message.
'''

code_content, language = parsing_utils.extract_code_block(text_with_code_block)
print(f"Language: {language}")
print("Content:")
print(code_content)
~~~

**Output**:

```
Language: python
Content:
def hello_world():
    print("Hello, World!")
```

---

### 2. `parse_yaml_content(yaml_string: str) -> Optional[Dict[str, Any]]`

**Purpose**: Parses a YAML-formatted string into a Python dictionary.

**Parameters**:

- `yaml_string` (str): The YAML string to parse.

**Returns**:

- `Optional[Dict[str, Any]]`: The parsed YAML content as a dictionary, or `None` if parsing fails.

**Example Usage**:

~~~python
from agentforge.utils.ParsingProcessor import ParsingProcessor

parsing_utils = ParsingProcessor()

yaml_text = '''
```yaml
name: AgentForge
version: 1.0
features:
  - Custom Agents
  - Utilities
  - LLM Integration
```
'''

parsed_data = parsing_utils.parse_yaml_content(yaml_text)
print(parsed_data)
~~~

**Output**:

```python
{
  'name': 'AgentForge',
  'version': 1.0,
  'features': ['Custom Agents', 'Utilities', 'LLM Integration']
}
```

---

### 3. `parse_json_content(json_string: str) -> Optional[Dict[str, Any]]`

**Purpose**: Parses a JSON-formatted string into a Python dictionary.

**Parameters**:

- `json_string` (str): The JSON string to parse.

**Returns**:

- `Optional[Dict[str, Any]]`: The parsed JSON content as a dictionary, or `None` if parsing fails.

**Example Usage**:

~~~python
from agentforge.utils.ParsingProcessor import ParsingProcessor

parsing_utils = ParsingProcessor()

json_text = '''
```json
{
  "name": "AgentForge",
  "version": "1.0",
  "features": ["Custom Agents", "Utilities", "LLM Integration"]
}
```
'''

parsed_data = parsing_utils.parse_json_content(json_text)
print(parsed_data)
~~~

**Output**:

```python
{
  'name': 'AgentForge',
  'version': '1.0',
  'features': ['Custom Agents', 'Utilities', 'LLM Integration']
}
```

---

### 4. `parse_xml_content(xml_string: str) -> Optional[Dict[str, Any]]`

**Purpose**: Parses an XML-formatted string into a Python dictionary.

**Parameters**:

- `xml_string` (str): The XML string to parse.

**Returns**:

- `Optional[Dict[str, Any]]`: The parsed XML content as a dictionary, or `None` if parsing fails.

**Example Usage**:

~~~python
from agentforge.utils.ParsingProcessor import ParsingProcessor

parsing_utils = ParsingProcessor()

xml_text = '''
```xml
<agent>
    <name>AgentForge</name>
    <version>1.0</version>
    <features>
        <feature>Custom Agents</feature>
        <feature>Utilities</feature>
        <feature>LLM Integration</feature>
    </features>
</agent>
```
'''

parsed_data = parsing_utils.parse_xml_content(xml_text)
print(parsed_data)
~~~

**Output**:

```python
{
  'agent': {
    'name': 'AgentForge',
    'version': '1.0',
    'features': {
      'feature': ['Custom Agents', 'Utilities', 'LLM Integration']
    }
  }
}
```

---

### 5. `parse_ini_content(ini_string: str) -> Optional[Dict[str, Any]]`

**Purpose**: Parses an INI-formatted string into a Python dictionary.

**Parameters**:

- `ini_string` (str): The INI string to parse.

**Returns**:

- `Optional[Dict[str, Any]]`: The parsed INI content as a dictionary, or `None` if parsing fails.

**Example Usage**:

~~~python
from agentforge.utils.ParsingProcessor import ParsingProcessor

parsing_utils = ParsingProcessor()

ini_text = '''
```ini
[Agent]
name = AgentForge
version = 1.0

[Features]
feature1 = Custom Agents
feature2 = Utilities
feature3 = LLM Integration
```
'''

parsed_data = parsing_utils.parse_ini_content(ini_text)
print(parsed_data)
~~~

**Output**:

```python
{
  'Agent': {
    'name': 'AgentForge',
    'version': '1.0'
  },
  'Features': {
    'feature1': 'Custom Agents',
    'feature2': 'Utilities',
    'feature3': 'LLM Integration'
  }
}
```

---

### 6. `parse_csv_content(csv_string: str) -> Optional[List[Dict[str, Any]]]`

**Purpose**: Parses a CSV-formatted string into a list of dictionaries.

**Parameters**:

- `csv_string` (str): The CSV string to parse.

**Returns**:

- `Optional[List[Dict[str, Any]]]`: The parsed CSV content as a list of dictionaries, or `None` if parsing fails.

**Example Usage**:

~~~python
from agentforge.utils.ParsingProcessor import ParsingProcessor

parsing_utils = ParsingProcessor()

csv_text = '''
```csv
name,version,features
AgentForge,1.0,"Custom Agents; Utilities; LLM Integration"
```
'''

parsed_data = parsing_utils.parse_csv_content(csv_text)
print(parsed_data)
~~~

**Output**:

```python
[
  {
    'name': 'AgentForge',
    'version': '1.0',
    'features': 'Custom Agents; Utilities; LLM Integration'
  }
]
```

---

### 7. `parse_markdown_content(markdown_string: str, min_heading_level=2, max_heading_level=6) -> Optional[Dict[str, Any]]`

**Purpose**: Parses a Markdown-formatted string, extracting headings and their associated content into a Python dictionary.

**Parameters**:

- `markdown_string` (str): The Markdown string to parse.
- `min_heading_level` (int, optional): The minimum heading level to include (default is `2`).
- `max_heading_level` (int, optional): The maximum heading level to include (default is `6`).

**Returns**:

- `Optional[Dict[str, Any]]`: A dictionary where each key is a heading and each value is the associated content, or `None` if parsing fails.

**Behavior**:

- Attempts to extract a code block from the provided text using `extract_code_block`.
- Checks if the language specifier matches 'markdown'.
  - If not, logs a warning but proceeds with parsing.
- Uses `parse_markdown_to_dict` to parse the extracted content into a dictionary mapping headings to their content.

**Example Usage**:

~~~python
from agentforge.utils.ParsingProcessor import ParsingProcessor

parsing_utils = ParsingProcessor()

markdown_text = '''
Here is some introductory text.

```markdown
### Initial Understanding
I understand that the conversation has transitioned from casual small talk to a deeper inquiry into my thoughts and feelings.

### Step-by-Step Thought Process
1. **Initial Intrigue**: I notice the unique approach.
   - This prompts me to consider opening up about my thoughts and feelings.

### Conclusions
Based on my analysis, I conclude that the user's approach invites a deeper level of engagement.

### Attempt
Hey there! I appreciate your genuine interest in my thoughts and feelings.
```

End of message.
'''

parsed_data = parsing_utils.parse_markdown_content(markdown_text, min_heading_level=3, max_heading_level=3)
print(parsed_data)
~~~

**Output**:

```python
{
  'Initial Understanding': 'I understand that the conversation has transitioned from casual small talk to a deeper inquiry into my thoughts and feelings.',
  'Step-by-Step Thought Process': '1. **Initial Intrigue**: I notice the unique approach.\n   - This prompts me to consider opening up about my thoughts and feelings.',
  'Conclusions': "Based on my analysis, I conclude that the user's approach invites a deeper level of engagement.",
  'Attempt': 'Hey there! I appreciate your genuine interest in my thoughts and feelings.'
}
```

---

## Use Cases

### Parsing Agent Responses

Agents may return responses that include structured data in various formats (YAML, JSON, XML, etc.). You can use `ParsingUtils` to extract and parse this data for further processing.

**Example**:

~~~python
from agentforge.utils.ParsingProcessor import ParsingProcessor

response = '''
Thank you for your input. Here are the details:

```json
{
  "status": "success",
  "data": {
    "user": "John Doe",
    "action": "process"
  }
}
```

Let me know if you need anything else.
'''

parsing_utils = ParsingProcessor()
parsed_response = parsing_utils.parse_json_content(response)
print(parsed_response['data']['user'])  # Output: John Doe
~~~

### Processing Configuration Files

If you have configuration data embedded within larger text files or strings, `ParsingUtils` can help extract and parse that data.

---

## Error Handling

- **Parsing Failures**: If parsing fails due to invalid syntax or unexpected content, the methods will log the error using the `Logger` utility and return `None`.
- **Code Block Extraction**: If no code block is found, `extract_code_block` will return the entire text stripped of leading and trailing whitespace, and `None` as the language specifier.
- **Type Checking**: Always check the return value for `None` before proceeding to use the parsed data.

---

## Best Practices

- **Ensure Correct Formatting**: Make sure that the text you are parsing contains properly formatted content (e.g., valid JSON, YAML, etc.) enclosed within code blocks for reliable extraction.
- **Handle Parsing Failures**: Implement checks for `None` return values to handle parsing failures gracefully.

---

## Conclusion

The `ParsingUtils` utility in **AgentForge** is a versatile tool for handling structured text data across multiple formats. By leveraging its methods, you can seamlessly extract and parse content from agent responses, configuration files, or any text containing embedded structured data.

---

**Need Help?**

If you have questions or need assistance, feel free to reach out:

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)

---