"""
Tests for PromptProcessor markdown rendering functionality.

This module tests the enhanced PromptProcessor that now formats dict/list values
in placeholders as markdown instead of Python repr.
"""

import pytest
from agentforge.utils.prompt_processor import PromptProcessor


class TestPromptProcessorMarkdown:
    """Test suite for markdown formatting functionality in PromptProcessor."""
    
    @pytest.fixture
    def processor(self):
        """Create a PromptProcessor instance for testing."""
        return PromptProcessor()
    
    def test_value_to_markdown_dict(self, processor):
        """Test that dictionaries are formatted as markdown with minimalist keys."""
        test_dict = {
            'name': 'John Doe',
            'skills': ['Python', 'JavaScript'],
            'preferences': {
                'language': 'English',
                'timezone': 'UTC'
            }
        }
        
        result = processor.value_to_markdown(test_dict)
        
        assert 'name: John Doe' in result
        assert 'skills:' in result
        assert 'preferences:' in result
        
        assert '- Python' in result
        assert '- JavaScript' in result
        
        assert 'language: English' in result
        assert 'timezone: UTC' in result
    
    def test_value_to_markdown_list(self, processor):
        """Test that lists are formatted as markdown bullet points."""
        test_list = ['item1', 'item2', 'item3']
        
        result = processor.value_to_markdown(test_list)
        
        assert result == '- item1\n- item2\n- item3'
    
    def test_value_to_markdown_string(self, processor):
        """Test that strings are returned as-is."""
        test_string = 'Hello, world!'
        
        result = processor.value_to_markdown(test_string)
        
        assert result == 'Hello, world!'
    
    def test_value_to_markdown_empty_dict(self, processor):
        """Test that empty dictionaries return empty string."""
        result = processor.value_to_markdown({})
        assert result == ""
    
    def test_value_to_markdown_empty_list(self, processor):
        """Test that empty lists return empty string."""
        result = processor.value_to_markdown([])
        assert result == ""
    
    def test_dict_placeholder_renders_as_markdown(self, processor):
        """Test that dict placeholders render as markdown instead of Python repr."""
        template = "User data: {user_info}"
        data = {
            'user_info': {
                'name': 'Alice',
                'preferences': ['reading', 'music'],
                'settings': {
                    'theme': 'dark',
                    'notifications': True
                }
            }
        }
        
        result = processor.render_prompt_template(template, data)
        
        assert "{'name': 'Alice'" not in result
        assert "['reading', 'music']" not in result
        
        assert 'name: Alice' in result
        assert 'preferences:' in result
        assert '- reading' in result
        assert '- music' in result
        assert 'settings:' in result
        assert 'theme: dark' in result
        assert 'notifications: True' in result
    
    def test_list_placeholder_renders_as_markdown(self, processor):
        """Test that list placeholders render as markdown bullets."""
        template = "Todo items: {tasks}"
        data = {
            'tasks': ['Buy groceries', 'Walk the dog', 'Finish project']
        }
        
        result = processor.render_prompt_template(template, data)
        
        assert "['Buy groceries'," not in result
        
        assert '- Buy groceries' in result
        assert '- Walk the dog' in result
        assert '- Finish project' in result
    
    def test_mixed_data_types_in_template(self, processor):
        """Test template with mixed data types (string, dict, list)."""
        template = "User: {name}\nInfo: {details}\nTags: {tags}"
        data = {
            'name': 'Bob',
            'details': {
                'age': 30,
                'city': 'New York'
            },
            'tags': ['developer', 'musician']
        }
        
        result = processor.render_prompt_template(template, data)
        
        assert 'User: Bob' in result
        
        assert 'age: 30' in result
        assert 'city: New York' in result
        
        assert '- developer' in result
        assert '- musician' in result
    
    def test_nested_placeholders_with_markdown(self, processor):
        """Test nested placeholders work with markdown formatting."""
        template = "Agent analysis: {analyze.result}"
        data = {
            'analyze': {
                'result': {
                    'sentiment': 'positive',
                    'topics': ['technology', 'education'],
                    'confidence': 0.95
                }
            }
        }
        
        result = processor.render_prompt_template(template, data)
        
        assert 'sentiment: positive' in result
        assert 'topics:' in result
        assert '- technology' in result
        assert '- education' in result
        assert 'confidence: 0.95' in result
    
    def test_build_persona_markdown_uses_helper(self, processor):
        """Test that build_persona_markdown uses the centralized helper."""
        static_content = {
            'name': 'Test Assistant',
            'traits': ['helpful', 'analytical'],
            'background': {
                'experience': '5 years',
                'domain': 'AI'
            }
        }
        persona_settings = {'static_char_cap': 1000}
        
        result = processor.build_persona_markdown(static_content, persona_settings)
        
        assert 'name: Test Assistant' in result
        assert 'traits:' in result
        assert '- helpful' in result
        assert '- analytical' in result
        assert 'background:' in result
        assert 'experience: 5 years' in result
        assert 'domain: AI' in result 