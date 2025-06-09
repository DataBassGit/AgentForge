"""
Tests for ParsingProcessor two-stage parsing functionality.

This module tests the enhanced ParsingProcessor that supports:
1. Code-fenced parsing (stage 1)
2. Bare parsing fallback (stage 2)
3. Enhanced logging for both stages
"""

import pytest
from unittest.mock import Mock, patch
from agentforge.utils.parsing_processor import ParsingProcessor, ParsingError


class TestParsingProcessorTwoStage:
    """Test suite for two-stage parsing functionality in ParsingProcessor."""
    
    @pytest.fixture
    def processor(self):
        """Create a ParsingProcessor instance for testing."""
        return ParsingProcessor()
    
    def test_code_fenced_json_parsing_succeeds(self, processor):
        """Test successful parsing of code-fenced JSON content."""
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
        
        result = processor.parse_by_format(json_fenced, 'json')
        
        assert result['name'] == 'AgentForge'
        assert result['version'] == '2.0'
        assert result['features'] == ['parsing', 'agents']
    
    def test_code_fenced_yaml_parsing_succeeds(self, processor):
        """Test successful parsing of code-fenced YAML content."""
        yaml_fenced = '''
        ```yaml
        agent:
          name: TestAgent
          settings:
            temperature: 0.7
            max_tokens: 1000
        ```
        '''
        
        result = processor.parse_by_format(yaml_fenced, 'yaml')
        
        assert result['agent']['name'] == 'TestAgent'
        assert result['agent']['settings']['temperature'] == 0.7
        assert result['agent']['settings']['max_tokens'] == 1000
    
    def test_bare_json_parsing_fallback(self, processor):
        """Test bare JSON parsing when no code fence is present."""
        bare_json = '''
        {
            "status": "success",
            "data": {
                "count": 42,
                "message": "Hello World"
            }
        }
        '''
        
        result = processor.parse_by_format(bare_json, 'json')
        
        assert result['status'] == 'success'
        assert result['data']['count'] == 42
        assert result['data']['message'] == 'Hello World'
    
    def test_bare_yaml_parsing_fallback(self, processor):
        """Test bare YAML parsing when no code fence is present."""
        bare_yaml = '''
        configuration:
          debug: true
          modules:
            - parsing
            - logging
            - memory
        '''
        
        result = processor.parse_by_format(bare_yaml, 'yaml')
        
        assert result['configuration']['debug'] is True
        assert 'parsing' in result['configuration']['modules']
        assert len(result['configuration']['modules']) == 3
    
    def test_fallback_after_failed_fence_parsing(self, processor):
        """Test that bare parsing succeeds when no code fence is found but content is valid."""
        # Content without code fences that should fall back to bare parsing
        bare_json_content = '''{
            "message": "No code fence found",
            "valid": "json",
            "result": "success"
        }'''
        
        result = processor.parse_by_format(bare_json_content, 'json')
        
        assert result['valid'] == 'json'
        assert result['result'] == 'success'
        assert result['message'] == 'No code fence found'
    
    def test_csv_two_stage_parsing(self, processor):
        """Test two-stage parsing for CSV format."""
        csv_content = '''```csv
name,age,city
Alice,30,New York
Bob,25,San Francisco
```'''
        
        result = processor.parse_by_format(csv_content, 'csv')
        
        assert len(result) == 2
        assert result[0]['name'].strip() == 'Alice'
        assert result[0]['age'].strip() == '30'
        assert result[1]['name'].strip() == 'Bob'
        assert result[1]['city'].strip() == 'San Francisco'
    
    def test_xml_two_stage_parsing(self, processor):
        """Test two-stage parsing for XML format."""
        xml_content = '''```xml
<root>
    <item id="1">
        <name>Test Item</name>
        <value>42</value>
    </item>
</root>
```'''
        
        result = processor.parse_by_format(xml_content, 'xml')
        
        assert result['root']['item']['name'] == 'Test Item'
        assert result['root']['item']['value'] == '42'
        assert result['root']['item']['@id'] == '1'
    
    def test_ini_two_stage_parsing(self, processor):
        """Test two-stage parsing for INI format."""
        ini_content = '''```ini
[database]
host=localhost
port=5432
name=testdb

[logging]
level=DEBUG
file=app.log
```'''
        
        result = processor.parse_by_format(ini_content, 'ini')
        
        assert result['database']['host'] == 'localhost'
        assert result['database']['port'] == '5432'
        assert result['logging']['level'] == 'DEBUG'
        assert result['logging']['file'] == 'app.log'
    
    def test_markdown_two_stage_parsing(self, processor):
        """Test two-stage parsing for Markdown format."""
        markdown_content = '''```markdown
## Section 1
This is the first section with some content.

### Subsection A
More detailed information here.

## Section 2
Another main section.
```'''
        
        result = processor.parse_by_format(markdown_content, 'markdown')
        
        assert 'Section 1' in result
        assert 'Section 2' in result
        assert 'This is the first section' in result['Section 1']
        assert 'Another main section' in result['Section 2']
    
    def test_language_mismatch_warning(self, processor):
        """Test that a warning is logged when language specifier doesn't match expected format."""
        yaml_with_wrong_language = '''```json
name: AgentForge
version: 2.0
```'''
        
        with patch.object(processor.logger, 'warning') as mock_warning:
            result = processor.parse_by_format(yaml_with_wrong_language, 'yaml')
            
            # Should still parse successfully
            assert result['name'] == 'AgentForge'
            assert result['version'] == 2.0
            
            # Should have logged a warning about language mismatch
            assert mock_warning.call_count > 0
            assert any("Expected YAML" in str(call.args[0]) for call in mock_warning.call_args_list)
    
    def test_no_code_fences_provided(self, processor):
        """Test behavior when no code fences are provided (should proceed with full content)."""
        json_content = '''
        {
            "direct": "parsing",
            "no_fences": true
        }
        '''
        
        with patch.object(processor.logger, 'debug') as mock_debug:
            result = processor.parse_by_format(json_content, 'json', code_fences=[])
            
            assert result['direct'] == 'parsing'
            assert result['no_fences'] is True
            
            # Should log that no code fences were specified
            assert any("No code fences specified" in str(call.args[0]) for call in mock_debug.call_args_list)
    
    def test_enhanced_logging_for_bare_parsing_fallback(self, processor):
        """Test that enhanced logging is present when falling back to bare parsing."""
        # Content without code fence to demonstrate fallback logging
        bare_json_content = '''{
            "logging_test": true,
            "valid": "json",
            "result": "success"
        }'''
        
        with patch.object(processor.logger, 'debug') as mock_debug:
            result = processor.parse_by_format(bare_json_content, 'json', code_fences=['```'])
            
            assert result['valid'] == 'json'
            assert result['result'] == 'success'
            assert result['logging_test'] is True
            
            # Check for specific log messages indicating parsing behavior
            log_messages = [call.args[0] for call in mock_debug.call_args_list]
            
            # Should have debug message about no code fence found
            assert any("No code-fenced block found" in msg for msg in log_messages)
            
            # Should have debug message about attempting parsing
            assert any("Attempting code-fenced JSON parsing" in msg for msg in log_messages)
            
            # Should have success message
            assert any("Code-fenced JSON parsing succeeded" in msg for msg in log_messages)
    
    def test_parsing_error_when_all_stages_fail(self, processor):
        """Test that ParsingError is raised when both stages fail."""
        invalid_json = '''
        ```json
        {invalid json in fence}
        ```
        {also invalid json outside fence}
        '''
        
        with pytest.raises(ParsingError) as exc_info:
            processor.parse_by_format(invalid_json, 'json')
        
        assert "Failed to parse json" in str(exc_info.value)
    
    def test_yaml_special_cleanup_behavior(self, processor):
        """Test that YAML maintains its special cleanup behavior in the refactor."""
        # Test YAML content that should parse successfully
        yaml_content = '''```yaml
name: AgentForge
description: "A framework for agents"
version: 2.0
```'''
        
        result = processor.parse_by_format(yaml_content, 'yaml')
        
        assert result['name'] == 'AgentForge'
        assert result['description'] == 'A framework for agents'
        assert result['version'] == 2.0 