"""
Test ConfigManager Phase 1: Basic configuration validation and object building.

This test suite validates that ConfigManager can:
1. Build structured AgentConfig objects from raw data
2. Build structured CogConfig objects from raw data
3. Validate required fields and reject invalid configurations
4. Handle both agent and cog configurations correctly

These tests use raw configuration data and test the core validation logic.
"""

import pytest
from src.agentforge.core.config_manager import ConfigManager


def test_config_manager_agent_config_building(isolated_config):
    """Test that ConfigManager can build structured agent configs from raw data."""
    config_manager = ConfigManager()
    
    # Get raw agent data
    raw_agent_data = isolated_config.find_config('prompts', 'cog_analyze_agent')
    
    # Add required fields that might be missing in test config
    raw_agent_data['name'] = 'cog_analyze_agent'
    
    # Resolve model for the agent
    api_name, class_name, model_name, final_params = isolated_config.resolve_model_overrides(raw_agent_data)
    model = isolated_config.get_model(api_name, class_name, model_name)
    raw_agent_data['model'] = model
    raw_agent_data['params'] = final_params
    
    # Get settings
    raw_agent_data['settings'] = isolated_config.data.get('settings', {})
    
    # Test agent config building with raw data
    agent_config = config_manager.build_agent_config(raw_agent_data)
    
    # Verify structured config object
    assert agent_config.name == 'cog_analyze_agent'
    assert agent_config.model is not None
    assert 'system' in agent_config.prompts
    assert 'user' in agent_config.prompts
    assert agent_config.settings.system.persona.enabled is not None
    
    print(f"✓ Agent config: {agent_config.name}")
    print(f"  - Model: {type(agent_config.model).__name__}")
    print(f"  - Persona enabled: {agent_config.settings.system.persona.enabled}")
    print(f"  - Debug mode: {agent_config.settings.system.debug.mode}")


def test_config_manager_cog_config(isolated_config):
    """Test that ConfigManager can build structured cog configs from raw data."""
    config_manager = ConfigManager()
    
    # Get raw cog data directly
    raw_cog_data = isolated_config.find_config('cogs', 'example_cog')
    
    # Test cog config building with raw data
    cog_config = config_manager.build_cog_config(raw_cog_data)
    
    # Verify structured config object
    assert cog_config.cog.name == 'ExampleCog'
    assert cog_config.cog.flow is not None
    assert cog_config.cog.flow.start == 'analysis'
    assert len(cog_config.cog.agents) > 0
    
    # Verify agent definitions
    first_agent = cog_config.cog.agents[0]
    assert first_agent.id == 'analysis'
    assert first_agent.template_file == 'cog_analyze_agent'
    
    # Verify flow transitions
    assert 'decision' in cog_config.cog.flow.transitions
    decide_transition = cog_config.cog.flow.transitions['decision']
    assert decide_transition.type == 'decision'
    assert decide_transition.decision_key == 'choice'
    assert 'approve' in decide_transition.decision_map
    assert 'reject' in decide_transition.decision_map
    
    print(f"✓ Cog config: {cog_config.cog.name}")
    print(f"  - Flow start: {cog_config.cog.flow.start}")
    print(f"  - Agent count: {len(cog_config.cog.agents)}")
    print(f"  - Memory nodes: {len(cog_config.cog.memory)}")


def test_config_manager_validation():
    """Test that ConfigManager properly validates config data."""
    config_manager = ConfigManager()
    
    # Test missing required keys
    try:
        invalid_agent_data = {'name': 'TestAgent'}  # Missing required keys
        config_manager.build_agent_config(invalid_agent_data)
        assert False, "Should have raised ValueError for missing required keys"
    except ValueError as e:
        assert "missing required key" in str(e)
        print("✓ Validation catches missing required keys")
    
    # Test missing name
    try:
        invalid_agent_data = {
            'params': {},
            'prompts': {'system': 'test', 'user': 'test'},
            'settings': {'system': {'persona': {'enabled': False}}},
        }  # Missing name
        config_manager.build_agent_config(invalid_agent_data)
        assert False, "Should have raised ValueError for missing name"
    except ValueError as e:
        assert "missing required 'name' field" in str(e)
        print("✓ Validation catches missing name")
    
    # Test empty prompts
    try:
        invalid_agent_data = {
            'name': 'TestAgent',
            'params': {},
            'prompts': {},  # Empty prompts
            'settings': {'system': {'persona': {'enabled': False}}},
            'model': object()
        }
        config_manager.build_agent_config(invalid_agent_data)
        assert False, "Should have raised ValueError for empty prompts"
    except ValueError as e:
        assert "must have a non-empty 'prompts' dictionary" in str(e)
        print("✓ Validation catches empty prompts")
    
    # Test null model
    try:
        invalid_agent_data = {
            'name': 'TestAgent',
            'params': {},
            'prompts': {'system': 'test', 'user': 'test'},  # Include both required keys
            'settings': {'system': {'persona': {'enabled': False}}},
            'model': None  # Null model
        }
        config_manager.build_agent_config(invalid_agent_data)
        assert False, "Should have raised ValueError for null model"
    except ValueError as e:
        assert "must have a 'model' specified" in str(e)
        print("✓ Validation catches null model")
    
    # Test invalid prompt format (missing user key)
    try:
        invalid_agent_data = {
            'name': 'TestAgent',
            'params': {},
            'prompts': {'system': 'test'},  # Missing 'user' key
            'settings': {'system': {'persona': {'enabled': False}}},
            'model': object()
        }
        config_manager.build_agent_config(invalid_agent_data)
        assert False, "Should have raised ValueError for invalid prompt format"
    except ValueError as e:
        assert "invalid prompt format" in str(e)
        print("✓ Validation catches invalid prompt format")
    
    # Test invalid cog data
    try:
        invalid_cog_data = {'not_cog': 'invalid'}  # Missing 'cog' key
        config_manager.build_cog_config(invalid_cog_data)
        assert False, "Should have raised ValueError for missing cog key"
    except ValueError as e:
        assert "must have a 'cog' dictionary" in str(e)
        print("✓ Validation catches invalid cog structure")


def test_config_manager_settings_building():
    """Test that ConfigManager correctly builds Settings objects."""
    config_manager = ConfigManager()
    
    # Test with minimal settings
    raw_settings = {
        'system': {
            'persona': {'enabled': True, 'name': 'TestPersona'},
            'debug': {'mode': False},
            'logging': {'enabled': True, 'console_level': 'info'},
            'misc': {'on_the_fly': True},
            'paths': {'files': './test_files'}
        },
        'models': {'openai': {}},
        'storage': {'chroma': {}}
    }
    
    settings = config_manager._build_settings(raw_settings)
    
    # Verify settings structure
    assert settings.system.persona.enabled == True
    assert settings.system.persona.name == 'TestPersona'
    assert settings.system.debug.mode == False
    assert settings.system.logging.enabled == True
    assert settings.system.logging.console_level == 'info'
    assert settings.system.misc.on_the_fly == True
    assert settings.system.paths.files == './test_files'
    assert 'openai' in settings.models
    assert 'chroma' in settings.storage
    
    print("✓ Settings building works correctly")
    print(f"  - Persona: {settings.system.persona.name} (enabled: {settings.system.persona.enabled})")
    print(f"  - Debug mode: {settings.system.debug.mode}")
    print(f"  - Logging level: {settings.system.logging.console_level}")


def test_config_manager_cog_flow_parsing():
    """Test that ConfigManager correctly parses cog flow transitions."""
    config_manager = ConfigManager()
    
    # Test direct transition
    direct_transition = config_manager._parse_flow_transition("next_agent")
    assert direct_transition.type == "direct"
    assert direct_transition.next_agent == "next_agent"
    
    # Test end transition
    end_transition = config_manager._parse_flow_transition({"end": True})
    assert end_transition.type == "end"
    assert end_transition.end == True
    
    # Test decision transition
    decision_transition = config_manager._parse_flow_transition({
        "choice": {"approve": "respond", "reject": "analyze"},
        "fallback": "analyze"
    })
    assert decision_transition.type == "decision"
    assert decision_transition.decision_key == "choice"
    assert decision_transition.decision_map["approve"] == "respond"
    assert decision_transition.decision_map["reject"] == "analyze"
    assert decision_transition.fallback == "analyze"
    
    print("✓ Flow parsing works correctly")
    print(f"  - Direct: {direct_transition.next_agent}")
    print(f"  - End: {end_transition.end}")
    print(f"  - Decision: {decision_transition.decision_key} -> {len(decision_transition.decision_map)} options") 