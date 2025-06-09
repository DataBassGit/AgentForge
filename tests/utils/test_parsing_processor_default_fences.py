"""
Tests for ParsingProcessor default code fence functionality.

This module tests the enhanced ParsingProcessor that now defaults to using
code fence extraction with ['```'] by default, while still allowing users
to disable or customize code fence behavior.
"""

import pytest
from unittest.mock import Mock, patch
from agentforge.utils.parsing_processor import ParsingProcessor, ParsingError


class TestParsingProcessorDefaultFences:
    """Test suite for default code fence functionality in ParsingProcessor."""
    
    @pytest.fixture
    def processor(self):
        """Create a ParsingProcessor instance for testing."""
        return ParsingProcessor()
    
    def test_default_code_fences_class_variable(self, processor):
        """Test that the DEFAULT_CODE_FENCES class variable is set correctly."""
        assert hasattr(ParsingProcessor, 'DEFAULT_CODE_FENCES')
        assert ParsingProcessor.DEFAULT_CODE_FENCES == ['```']
    
    def test_parse_by_format_uses_default_fences_when_none_provided(self, processor):
        """Test that parse_by_format uses default code fences when no code_fences parameter is provided."""
        json_fenced = '''
        Here is some JSON data:
        
        ```json
        {
            "name": "AgentForge",
            "version": "2.0",
            "features": ["parsing", "agents"]
        }
        ```
        
        That's the data.
        '''
        
        # Call without code_fences parameter - should use default ['```']
        result = processor.parse_by_format(json_fenced, 'json')
        
        assert result['name'] == 'AgentForge'
        assert result['version'] == '2.0'
        assert result['features'] == ['parsing', 'agents']
    
    def test_auto_parse_content_uses_default_fences_when_none_provided(self, processor):
        """Test that auto_parse_content uses default code fences when no code_fences parameter is provided."""
        yaml_fenced = '''
        ```yaml
        agent:
          name: TestAgent
          settings:
            temperature: 0.7
        ```
        '''
        
        # Call without code_fences parameter - should use default ['```']
        result = processor.auto_parse_content(yaml_fenced)
        
        assert result['agent']['name'] == 'TestAgent'
        assert result['agent']['settings']['temperature'] == 0.7
    
    def test_extract_code_block_uses_default_fences_when_none_provided(self, processor):
        """Test that extract_code_block uses default code fences when no code_fences parameter is provided."""
        text_with_fence = '''
        Some explanation text.
        
        ```python
        print("Hello, world!")
        ```
        
        More text after.
        '''
        
        # Call without code_fences parameter - should use default ['```']
        language, content = processor.extract_code_block(text_with_fence)
        
        assert language == 'python'
        assert content == 'print("Hello, world!")'
    
    def test_parse_by_format_respects_explicit_empty_list(self, processor):
        """Test that parse_by_format respects explicitly passed empty list to disable code fence extraction."""
        json_content = '''
        {
            "message": "No code fence extraction",
            "direct_parsing": true
        }
        '''
        
        # Explicitly pass empty list to disable code fence extraction
        result = processor.parse_by_format(json_content, 'json', code_fences=[])
        
        assert result['message'] == 'No code fence extraction'
        assert result['direct_parsing'] is True
    
    def test_auto_parse_content_respects_explicit_empty_list(self, processor):
        """Test that auto_parse_content respects explicitly passed empty list to disable code fence extraction."""
        text_content = '''
        This is just plain text without any structured data.
        No code fences should be extracted.
        '''
        
        # Explicitly pass empty list to disable code fence extraction
        result = processor.auto_parse_content(text_content, code_fences=[])
        
        # Should return the raw text since no language can be detected
        assert result == text_content
    
    def test_extract_code_block_respects_explicit_empty_list(self, processor):
        """Test that extract_code_block respects explicitly passed empty list to disable code fence extraction."""
        text_with_fence = '''
        Some text with a code fence:
        
        ```python
        print("This should not be extracted")
        ```
        
        More text.
        '''
        
        # Explicitly pass empty list to disable code fence extraction
        language, content = processor.extract_code_block(text_with_fence, code_fences=[])
        
        assert language is None
        assert content == text_with_fence.strip()
    
    def test_custom_code_fences_override_default(self, processor):
        """Test that custom code fences override the default behavior."""
        text_with_custom_fence = '''
        Some explanation.
        
        ~~~json
        {
            "custom": "fence",
            "type": "tildes"
        }
        ~~~
        
        End of text.
        '''
        
        # Use custom fence markers
        result = processor.parse_by_format(text_with_custom_fence, 'json', code_fences=['~~~'])
        
        assert result['custom'] == 'fence'
        assert result['type'] == 'tildes'
    
    def test_multiple_code_blocks_extracts_first_with_default_fences(self, processor):
        """Test that when using default fences, only the first code block is extracted."""
        text_with_multiple_blocks = '''
        First block:
        
        ```json
        {
            "first": "block",
            "order": 1
        }
        ```
        
        Second block:
        
        ```json
        {
            "second": "block",
            "order": 2
        }
        ```
        '''
        
        # Should extract and parse only the first block
        result = processor.parse_by_format(text_with_multiple_blocks, 'json')
        
        assert result['first'] == 'block'
        assert result['order'] == 1
        assert 'second' not in result
    
    def test_fenced_content_with_leading_trailing_text_default_fences(self, processor):
        """Test that default fences work with leading and trailing explanatory text."""
        content_with_explanation = '''
        The agent analyzed the data and produced the following YAML configuration:
        
        ```yaml
        system:
          name: "AgentForge"
          version: "2.0"
          features:
            - parsing
            - memory
            - agents
        ```
        
        This configuration should be applied to the system immediately.
        The parsing was successful and all required fields are present.
        '''
        
        # Should extract and parse the YAML block using default fences
        result = processor.parse_by_format(content_with_explanation, 'yaml')
        
        assert result['system']['name'] == 'AgentForge'
        assert result['system']['version'] == '2.0'
        assert 'parsing' in result['system']['features']
        assert len(result['system']['features']) == 3
    
    def test_incorrect_language_specifier_with_default_fences(self, processor):
        """Test that default fences work even with incorrect language specifiers."""
        yaml_with_wrong_language = '''```json
name: "AgentForge"
version: 2.0
features:
  - "parsing"
  - "agents"
```'''
        
        with patch.object(processor.logger, 'warning') as mock_warning:
            # Should still parse as YAML despite json language specifier
            result = processor.parse_by_format(yaml_with_wrong_language, 'yaml')
            
            assert result['name'] == 'AgentForge'
            assert result['version'] == 2.0
            assert 'parsing' in result['features']
            
            # Should have logged a warning about language mismatch
            assert mock_warning.call_count > 0
            assert any("Expected YAML" in str(call.args[0]) for call in mock_warning.call_args_list)
    
    def test_no_language_specifier_with_default_fences(self, processor):
        """Test that default fences work with code blocks that have no language specifier."""
        content_no_language = '''
        Here's the data:
        
        ```
        {
            "no_language": "specified",
            "should_work": true
        }
        ```
        '''
        
        # Should extract and parse the JSON content
        result = processor.parse_by_format(content_no_language, 'json')
        
        assert result['no_language'] == 'specified'
        assert result['should_work'] is True
    
    def test_fallback_to_bare_parsing_with_default_fences(self, processor):
        """Test that fallback to bare parsing works when default fences are used but no fence is found."""
        bare_json = '''
        {
            "no_fence": "present",
            "should_fallback": "to_bare_parsing",
            "success": true
        }
        '''
        
        # Should fall back to bare parsing when no fence is found
        result = processor.parse_by_format(bare_json, 'json')
        
        assert result['no_fence'] == 'present'
        assert result['should_fallback'] == 'to_bare_parsing'
        assert result['success'] is True
    
    def test_csv_parsing_with_default_fences(self, processor):
        """Test CSV parsing with default code fences."""
        csv_content = '''
        Here's the CSV data:
        
        ```csv
        name,age,city
        Alice,30,New York
        Bob,25,San Francisco
        Charlie,35,Chicago
        ```
        '''
        
        result = processor.parse_by_format(csv_content, 'csv')
        
        assert len(result) == 3
        assert result[0]['name'].strip() == 'Alice'
        assert result[1]['city'].strip() == 'San Francisco'
        assert result[2]['age'].strip() == '35'
    
    def test_xml_parsing_with_default_fences(self, processor):
        """Test XML parsing with default code fences."""
        xml_content = '''
        The system configuration:
        
        ```xml
        <config>
            <database>
                <host>localhost</host>
                <port>5432</port>
            </database>
            <logging level="DEBUG"/>
        </config>
        ```
        '''
        
        result = processor.parse_by_format(xml_content, 'xml')
        
        assert result['config']['database']['host'] == 'localhost'
        assert result['config']['database']['port'] == '5432'
        assert result['config']['logging']['@level'] == 'DEBUG'
    
    def test_ini_parsing_with_default_fences(self, processor):
        """Test INI parsing with default code fences."""
        ini_content = '''
        Configuration file:
        
        ```ini
        [server]
        host=localhost
        port=8080
        debug=true
        
        [database]
        url=postgresql://localhost/mydb
        ```
        '''
        
        result = processor.parse_by_format(ini_content, 'ini')
        
        assert result['server']['host'] == 'localhost'
        assert result['server']['port'] == '8080'
        assert result['server']['debug'] == 'true'
        assert result['database']['url'] == 'postgresql://localhost/mydb'
    
    def test_markdown_parsing_with_default_fences(self, processor):
        """Test Markdown parsing with default code fences."""
        markdown_content = '''```markdown
## Installation
Follow these steps to install the software.

### Prerequisites
You need Python 3.8 or higher.

## Usage
Run the application with the following command.
```'''
        
        result = processor.parse_by_format(markdown_content, 'markdown')
        
        assert 'Installation' in result
        assert 'Usage' in result
        assert 'Follow these steps' in result['Installation']
        assert 'Run the application' in result['Usage']
    
    def test_logging_indicates_default_fence_usage(self, processor):
        """Test that log messages indicate when default fences are being used."""
        yaml_content = '''
        ```yaml
        test: value
        ```
        '''
        
        with patch.object(processor.logger, 'debug') as mock_debug:
            processor.parse_by_format(yaml_content, 'yaml')
            
            # Should have log messages mentioning code fence behavior
            debug_calls = [str(call) for call in mock_debug.call_args_list]
            # At least one call should mention code-fenced block detection or similar
            fence_related_logs = [call for call in debug_calls if 'Code-fenced' in call or 'code-fenced' in call]
            assert len(fence_related_logs) > 0

    def test_parse_by_format_returns_original_content_when_parser_type_is_none(self, processor):
        """Test that parse_by_format returns the original content unchanged when parser_type is None."""
        test_content = "This is some raw text content that should be returned unchanged."
        
        result = processor.parse_by_format(test_content, None)
        
        assert result == test_content
        
        # Test with empty string as parser_type too
        result_empty = processor.parse_by_format(test_content, "")
        assert result_empty == test_content 