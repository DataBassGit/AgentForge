# Parsing Processor Guide

In **AgentForge**, the `ParsingProcessor` class offers a robust suite of methods for extracting and parsing structured data from text. Whether you’re handling YAML, JSON, XML, INI, CSV, or Markdown content (including code fences), `ParsingProcessor` ensures consistent results and logs parsing errors gracefully.

---

## Overview

`ParsingProcessor` is designed to help agents and other system components interpret text that may contain structured data. It accomplishes this by:

1. **Extracting Code Blocks**: Locates code fences (with an optional language specifier) and returns their contents.  
2. **Parsing Common Formats**: YAML, JSON, XML, INI, CSV, and Markdown can all be converted to Python data structures (e.g., dictionaries).  
3. **Logging and Error Handling**: Uses a built-in logger to record successes, warnings (e.g., unexpected language labels), and parsing failures.

---

## Key Methods

### 1. `extract_code_block(text: str, code_fence: str = "```")`

**Purpose**  
Extracts the first matching code block using the specified `code_fence` delimiter.  
Returns a tuple `(language, content)` or `(None, entire_text_if_no_fence_found)`.

**Parameters**  
- `text` (`str`): The input string containing potential code fences.  
- `code_fence` (`str`, optional): The delimiter marking the start and end of the code block (default is triple backticks ```).  

**Behavior**  
- If a code block is found, it returns `(language, content)`. `language` may be `None` if no specifier is present or the matched language is empty.  
- If no code fence is found, returns `(None, text.strip())`.  
- Not infallible if multiple or nested code blocks exist; it only returns the **first** match.

**Example**:
~~~python
from agentforge.utils.logger import Logger
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

### 2. `parse_content(...)`

**Purpose**  
A generic helper method that `ParsingProcessor` uses internally to:

1. Extract code fences from a string.  
2. Compare the extracted language specifier (if any) to an expected format (like `json`, `yaml`, etc.).  
3. Run a specific parsing function (e.g., `json.loads`).  
4. Log any errors or warnings.

You typically won’t call `parse_content` directly; instead, you’ll call format-specific methods like `parse_json_content`, `parse_yaml_content`, etc.

---

### 3. `parse_markdown_content(markdown_string, min_heading_level=2, max_heading_level=6)`

**Purpose**  
Parses **Markdown**-formatted text, extracting headings (of the specified levels) and mapping each heading to its associated content in a Python dictionary.

**Behavior**  
- Wraps `extract_code_block`; expects the code fence language to be `'markdown'` but continues even if they differ.  
- Uses a helper (`parse_markdown_to_dict`) to parse headings from the extracted text.

**Example**:
~~~python
markdown_text = """
```markdown
## Heading One
Some content under heading one.

### Heading Two
More details here.
```
"""

processor = ParsingProcessor()
parsed = processor.parse_markdown_content(markdown_text, min_heading_level=2, max_heading_level=3)
print(parsed)
# {
#   'Heading One': 'Some content under heading one.',
#   'Heading Two': 'More details here.'
# }
~~~

---

### 4. `parse_yaml_content(yaml_string)`

**Purpose**  
Parses a **YAML** string into a Python dictionary.

**Behavior**  
- Extracts a code block (default fence is triple backticks ```).  
- Checks if the extracted language is `'yaml'`; logs a warning if not.  
- Parses with `yaml.safe_load`.  
- Returns a dictionary or `None` if parsing fails.

**Example**:
~~~python
yaml_text = """
```yaml
name: AgentForge
version: 1.0
```
"""

processor = ParsingProcessor()
parsed_yaml = processor.parse_yaml_content(yaml_text)
print(parsed_yaml)  # {'name': 'AgentForge', 'version': 1.0}
~~~

---

### 5. `parse_json_content(json_string)`

**Purpose**  
Parses a **JSON** string into a Python dictionary.

**Behavior**  
- Similar process: extracts code block, checks language specifier `'json'`, calls `json.loads`.  
- Logs an error if parsing fails.

**Example**:
~~~python
json_text = """
```json
{
  "name": "AgentForge",
  "features": ["Custom Agents", "Utilities"]
}
```
"""

parsed_json = processor.parse_json_content(json_text)
# {'name': 'AgentForge', 'features': ['Custom Agents', 'Utilities']}
~~~

---

### 6. `parse_xml_content(xml_string)`

**Purpose**  
Parses an **XML** string into a Python dictionary (via `xmltodict`).

**Behavior**  
- Expects `'xml'` in the code fence (but logs only a warning if missing or mismatched).  
- Returns a nested dict representing the XML structure.

**Example**:
~~~python
xml_text = """
```xml
<agent>
  <name>AgentForge</name>
</agent>
```
"""

parsed_xml = processor.parse_xml_content(xml_text)
# {'agent': {'name': 'AgentForge'}}
~~~

---

### 7. `parse_ini_content(ini_string)`

**Purpose**  
Parses an **INI**-formatted string into a dictionary where each section is a key, mapping to a dictionary of key-value pairs.

**Behavior**  
- If the code block language is `'ini'`, it’s recognized, but a mismatch logs a warning.  
- Internally uses `configparser.ConfigParser`.

**Example**:
~~~python
ini_text = """
```ini
[Agent]
name=AgentForge
version=1.0
```
"""

parsed_ini = processor.parse_ini_content(ini_text)
# {'Agent': {'name': 'AgentForge', 'version': '1.0'}}
~~~
---

### 8. `parse_csv_content(csv_string)`

**Purpose**  
Parses **CSV** into a list of dictionaries, using the first row as headers.

**Behavior**  
- Extracts code fence, warns if `language` != `'csv'`.  
- Uses `csv.DictReader` on the cleaned content.

**Example**:
~~~python
csv_text = """
```csv
name,version
AgentForge,1.0
```
"""

parsed_csv = processor.parse_csv_content(csv_text)
# [{'name': 'AgentForge', 'version': '1.0'}]
~~~

---

## Handling Parsing Failures

All parsing methods return `None` if they fail to parse the content. Each method logs the error (or unexpected language specifier) via **AgentForge**’s logger, ensuring you have a record of what went wrong.

**Example**:
~~~python
invalid_json = """
```json
{
  "name": "AgentForge"
  "missingComma": true
}
```
"""

result = processor.parse_json_content(invalid_json)
if result is None:
    print("Parsing failed. Check logs for details.")
~~~

---

## Use Cases

1. **Agent Response Parsing**  
   Agents might embed structured data within code blocks. `ParsingProcessor` extracts the relevant code fence and parses it into a Python structure.  

2. **Configuration Loading**  
   If your system or flows rely on user-provided config in various formats (INI, JSON, etc.), you can seamlessly parse them from text.  

3. **Markdown Summaries**  
   For summarizing or extracting headings and content from user-generated Markdown, `parse_markdown_content` is extremely handy.

---

## Best Practices

1. **Code Fence Convention**  
   Agents often use triple backticks \`\`\` for code blocks. But if your data uses a different delimiter, pass it to `extract_code_block(..., code_fence="some_delimiter")`.  
2. **Validate Returns**  
   Always check if the result is `None` before proceeding.  
3. **Avoid Nested Blocks**  
   The parser currently only grabs the **first** matching block. Nesting or multiple blocks with the same fence can lead to partial or incorrect captures.  
4. **Log and Debug**  
   Review your logs to see warnings or errors. This can inform you when your agent or input is inconsistent with the expected format.

---

## Conclusion

By leveraging the `ParsingProcessor` in **AgentForge**, you can reliably convert text-based structures into usable data. Whether your agents produce YAML or a user supplies CSV for configuration, the methods in this utility handle extraction, parsing, and error reporting in a unified, developer-friendly manner.

**Need Help?**  
- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)  
- **Discord**: [Join our Discord Server](https://discord.gg/ttpXHUtCW6)
