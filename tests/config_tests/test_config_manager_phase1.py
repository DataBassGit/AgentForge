"""Test script to verify ConfigManager Phase 1 functionality"""

def test_config_manager_agent_config(isolated_config):
    """Test that ConfigManager can build structured agent configs from raw data."""
    from src.agentforge.core.config_manager import ConfigManager
    
    config_manager = ConfigManager()
    
    # Get raw agent data by calling Config internal methods
    raw_agent = isolated_config.find_config('prompts', 'AnalyzeAgent')
    api_name, class_name, model_name, final_params = isolated_config.resolve_model_overrides(raw_agent)
    model = isolated_config.get_model(api_name, class_name, model_name)
    persona_data = isolated_config.load_persona(raw_agent)
    prompts = isolated_config.fix_prompt_placeholders(raw_agent.get('prompts', {}))
    settings = isolated_config.data.get('settings', {})
    default_debug_text = settings['system']['debug'].get('simulated_response', 'Simulated Text Goes Here!!!')
    simulated_response = raw_agent.get('simulated_response', default_debug_text).strip()

    # Construct raw agent data dict
    raw_agent_data = {
        'name': 'AnalyzeAgent',
        'settings': settings,
        'model': model,
        'params': final_params,
        'persona': persona_data,
        'prompts': prompts,
        'simulated_response': simulated_response,
    }
    
    # Test agent config building with raw data
    agent_config = config_manager.build_agent_config(raw_agent_data)
    
    # Verify structured config object
    assert agent_config.name == 'AnalyzeAgent'
    assert hasattr(agent_config.settings, 'system')
    assert hasattr(agent_config.settings.system, 'persona')
    assert hasattr(agent_config.settings.system, 'debug')
    assert hasattr(agent_config.settings.system, 'misc')
    
    # Verify attribute access works (no more dict access)
    assert isinstance(agent_config.settings.system.persona.enabled, bool)
    assert isinstance(agent_config.settings.system.debug.mode, bool)
    assert isinstance(agent_config.settings.system.misc.on_the_fly, bool)
    
    # Verify required fields are present
    assert agent_config.params is not None
    assert agent_config.prompts is not None
    assert agent_config.model is not None
    
    print(f"✓ Agent config: {agent_config.name}")
    print(f"  - Persona enabled: {agent_config.settings.system.persona.enabled}")
    print(f"  - Debug mode: {agent_config.settings.system.debug.mode}")
    print(f"  - On-the-fly: {agent_config.settings.system.misc.on_the_fly}")


def test_config_manager_cog_config(isolated_config):
    """Test that ConfigManager can build structured cog configs from raw data."""
    from src.agentforge.core.config_manager import ConfigManager
    
    config_manager = ConfigManager()
    
    # Get raw cog data directly
    raw_cog_data = isolated_config.find_config('cogs', 'ExampleCog')
    
    # Test cog config building with raw data
    cog_config = config_manager.build_cog_config(raw_cog_data)
    
    # Verify structured config object
    assert cog_config.cog.name == 'ExampleFlow'
    assert cog_config.cog.flow is not None
    assert cog_config.cog.flow.start == 'analyze'
    assert len(cog_config.cog.agents) > 0
    
    # Verify agent definitions
    first_agent = cog_config.cog.agents[0]
    assert first_agent.id == 'analyze'
    assert first_agent.template_file == 'AnalyzeAgent'
    
    # Verify flow transitions
    assert 'decide' in cog_config.cog.flow.transitions
    decide_transition = cog_config.cog.flow.transitions['decide']
    assert decide_transition.type == 'decision'
    assert decide_transition.decision_key == 'choice'
    assert 'approve' in decide_transition.decision_map
    assert 'reject' in decide_transition.decision_map
    
    print(f"✓ Cog config: {cog_config.cog.name}")
    print(f"  - Flow start: {cog_config.cog.flow.start}")
    print(f"  - Agent count: {len(cog_config.cog.agents)}")
    print(f"  - Memory nodes: {len(cog_config.cog.memory)}")


def test_config_manager_custom_fields(isolated_config):
    """Test that ConfigManager preserves custom fields from YAML."""
    from src.agentforge.core.config_manager import ConfigManager
    
    config_manager = ConfigManager()
    
    # Test with a simple custom agent data
    raw_agent_data = {
        'name': 'TestAgent',
        'params': {},
        'prompts': {'system': 'test', 'user': 'test'},
        'settings': isolated_config.data['settings'],
        'model': object(),
        'persona': None,
        'simulated_response': 'test',
        'parse_response_as': 'json',  # Custom field
        'custom_field': 'custom_value'  # Another custom field
    }
    
    # Build structured config object
    agent_config = config_manager.build_agent_config(raw_agent_data)
    
    # Should have custom fields preserved
    assert agent_config.parse_response_as == 'json'
    assert 'custom_field' in agent_config.custom_fields
    assert agent_config.custom_fields['custom_field'] == 'custom_value'
    print(f"✓ Custom fields preserved: parse_response_as={agent_config.parse_response_as}, custom_fields={agent_config.custom_fields}")


def test_config_manager_validation():
    """Test that ConfigManager properly validates config data."""
    from src.agentforge.core.config_manager import ConfigManager
    
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
            'prompts': {'system': 'test', 'user': 'test'},  # Include both required keys
            'settings': {'system': {'persona': {'enabled': False}}},
            'model': object()
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
        assert "non-empty 'prompts' dictionary" in str(e)
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