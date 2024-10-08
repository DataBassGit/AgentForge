# ParsingUtils Utility Guide

## Introduction

The `ParsingUtils` class in **AgentForge** provides methods for parsing formatted text, particularly **YAML** content embedded within larger text blocks. This utility is essential for agents that need to interpret or utilize configuration data, agent responses, or any dynamic content expressed in YAML or other structured formats.

---

## Overview

The `ParsingUtils` class offers the following key functionalities:

- **Extracting YAML Blocks**: Identifies and extracts **YAML** content from larger text blocks, even when embedded within code blocks.
- **Parsing YAML Content**: Parses **YAML**-formatted strings into Python dictionaries for easy manipulation within your code.

---

## Class Definition

```python
class ParsingUtils:
    def __init__(self):
        self.logger = Logger(name=self.__class__.__name__)

    def extract_yaml_block(self, text: str) -> Optional[str]:
        # Method implementation

    def parse_yaml_content(self, yaml_string: str) -> Optional[Dict[str, Any]]:
        # Method implementation
```

---

## Methods

### 1. `extract_yaml_block(text: str) -> Optional[str]`

**Purpose**: Extracts a **YAML** block from a given text. This is useful when dealing with text that contains embedded **YAML** code, such as agent responses or documentation.

**Parameters**:
- `text` (str): The text containing the YAML block.

**Returns**:
- `Optional[str]`: The extracted **YAML** content as a string, or `None` if no valid **YAML** content is found.

**Behavior**:

- Looks for content enclosed within triple backticks  and labeled as `yaml` (e.g., \```yaml ... ```).
- If not found, looks for any content within triple backticks \``` ... ```.
- If no code blocks are found, returns the entire text after stripping leading and trailing whitespace.

**Example Usage**:

```python
from agentforge.utils.ParsingUtils import ParsingUtils

parsing_utils = ParsingUtils()

text_with_yaml = '''
Here is some text.

```yaml
key: value
list:
  - item1
  - item2
```&nbsp;

End of message.
'''

yaml_content = parsing_utils.extract_yaml_block(text_with_yaml)
print(yaml_content)
```

**Output**:

```
key: value
list:
  - item1
  - item2
```

---

### 2. `parse_yaml_content(yaml_string: str) -> Optional[Dict[str, Any]]`

**Purpose**: Parses a **YAML**-formatted string into a Python dictionary.

**Parameters**:

- `yaml_string` (str): The **YAML** string to parse.

**Returns**:

- `Optional[Dict[str, Any]]`: The parsed **YAML** content as a dictionary, or `None` if parsing fails.

**Behavior**:

- First, calls `extract_yaml_block(yaml_string)` to extract the **YAML** content.
- Then, uses `yaml.safe_load()` to parse the **YAML** string into a Python dictionary.
- If parsing fails, logs the error and returns `None`.

**Example Usage**:

```python
from agentforge.utils.ParsingUtils import ParsingUtils

parsing_utils = ParsingUtils()

text_with_yaml = '''
Here is some text.

```yaml
name: AgentForge
version: 1.0
features:
  - Custom Agents
  - Utilities
  - LLM Integration
```&nbsp;

End of message.
'''

parsed_data = parsing_utils.parse_yaml_content(text_with_yaml)
print(parsed_data)
```

**Output**:

```python
{
  'name': 'AgentForge',
  'version': 1.0,
  'features': ['Custom Agents', 'Utilities', 'LLM Integration']
}
```

---

## Use Cases

### Parsing Agent Responses

Agents may return responses that include structured data in **YAML** format. You can use `ParsingUtils` to extract and parse this data for further processing.

**Example**:

```python
from agentforge.utils.ParsingUtils import ParsingUtils

response = '''
Thank you for your input. Here are the details:

```yaml
status: success
data:
  user: John Doe
  action: process
```&nbsp;

Let me know if you need anything else.
'''

parsing_utils = ParsingUtils()
parsed_response = parsing_utils.parse_yaml_content(response)
print(parsed_response['data']['user'])  # Output: John Doe
```

### Processing Configuration Files

If you have configuration data embedded within larger text files or strings, `ParsingUtils` can help extract and parse that data.

---

## Error Handling

- If no **YAML** block is found, `extract_yaml_block` will attempt to return any content within triple backticks.
- If parsing fails due to invalid **YAML** syntax, `parse_yaml_content` will log the error using the `Logger` utility and return `None`.
- Always check the return value for `None` before proceeding to use the parsed data.

---

## Best Practices

- Ensure that the text you are parsing actually contains **YAML** content enclosed within code blocks for reliable extraction.
- Handle the case where parsing might fail by checking if the returned value is `None`.
- Be cautious with untrusted input to avoid security risks associated with parsing **YAML** content.

---

## Conclusion

The `ParsingUtils` utility is a valuable tool within **AgentForge** for handling structured text data. By leveraging its methods, you can seamlessly extract and parse **YAML** content from agent responses, configuration files, or any text containing embedded **YAML**.

---

**Need Help?**

If you have questions or need assistance, feel free to reach out:

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)

---