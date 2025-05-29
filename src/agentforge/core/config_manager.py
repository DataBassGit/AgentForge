from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List, Union


class ConfigManager:
    """
    Responsible for all configuration validation, normalization, merging, and structured config object construction for AgentForge.
    
    - Accepts raw config dicts (from Config)
    - Validates schema, types, and required fields
    - Normalizes and merges config data as needed
    - Returns structured config objects for use by Agent, Cog, etc.
    
    NOTE: Config objects are designed to be immutable by convention - they should never be mutated in place.
    For hot-reload support, always replace the entire config object with a new one from ConfigManager.
    """

    def __init__(self):
        """Initialize ConfigManager with required processors."""
        pass

    # ==============================================================================
    # Agent Configuration Dataclasses
    # ==============================================================================

    @dataclass
    class PersonaSettings:
        """Persona configuration from system settings."""
        enabled: bool = True
        name: str = "DefaultAssistant"
        static_char_cap: int = 8000

    @dataclass
    class DebugSettings:
        """Debug configuration from system settings."""
        mode: bool = False
        save_memory: bool = False
        simulated_response: str = "Text designed to simulate an LLM response for debugging purposes without invoking the model."

    @dataclass
    class LoggingSettings:
        """Logging configuration from system settings."""
        enabled: bool = True
        console_level: str = "warning"
        folder: str = "./logs"
        files: Dict[str, str] = field(default_factory=dict)

    @dataclass
    class MiscSettings:
        """Miscellaneous system settings."""
        on_the_fly: bool = True

    @dataclass
    class PathSettings:
        """System file path settings."""
        files: str = "./files"

    @dataclass
    class SystemSettings:
        """System settings structure from settings/system.yaml."""
        persona: 'ConfigManager.PersonaSettings'
        debug: 'ConfigManager.DebugSettings'
        logging: 'ConfigManager.LoggingSettings'
        misc: 'ConfigManager.MiscSettings'
        paths: 'ConfigManager.PathSettings'

    @dataclass
    class Settings:
        """Complete settings structure containing system, models, and storage."""
        system: 'ConfigManager.SystemSettings'
        models: Dict[str, Any] = field(default_factory=dict)
        storage: Dict[str, Any] = field(default_factory=dict)

    @dataclass
    class AgentConfig:
        """
        Structured configuration object for agents.
        
        NOTE: This object should not be mutated in place. For hot-reload support,
        replace the entire object with a new one from ConfigManager.build_agent_config().
        """
        name: str
        settings: 'ConfigManager.Settings'
        model: Any
        params: Dict[str, Any]
        prompts: Dict[str, Any]
        persona: Optional[Dict[str, Any]] = None
        simulated_response: Optional[str] = None
        parse_response_as: Optional[str] = None
        # Support for additional custom fields from YAML
        custom_fields: Dict[str, Any] = field(default_factory=dict)

    # ==============================================================================
    # Cog Configuration Dataclasses
    # ==============================================================================

    @dataclass
    class CogAgentDef:
        """Definition of an agent within a cog."""
        id: str
        template_file: Optional[str] = None
        type: Optional[str] = None  # Full class path for custom agent types
        # Additional agent configuration can be added here

    @dataclass
    class CogMemoryDef:
        """Definition of a memory node within a cog."""
        id: str
        type: Optional[str] = None  # Full class path for memory type
        collection_id: Optional[str] = None
        query_before: Union[str, List[str], None] = None
        query_keys: List[str] = field(default_factory=list)
        update_after: Union[str, List[str], None] = None
        update_keys: List[str] = field(default_factory=list)

    @dataclass
    class CogFlowTransition:
        """A single flow transition definition."""
        # Can be a string (direct transition), dict (decision), or special end marker
        type: str  # "direct", "decision", "end"
        next_agent: Optional[str] = None  # For direct transitions
        decision_key: Optional[str] = None  # For decision transitions
        decision_map: Dict[str, str] = field(default_factory=dict)  # For decision transitions
        fallback: Optional[str] = None
        max_visits: Optional[int] = None
        end: bool = False

    @dataclass
    class CogFlow:
        """Flow definition for a cog."""
        start: str
        transitions: Dict[str, 'ConfigManager.CogFlowTransition']

    @dataclass
    class CogDefinition:
        """The core cog definition structure."""
        name: str
        description: Optional[str] = None
        persona: Optional[str] = None  # Persona override for the cog
        trail_logging: bool = True
        agents: List['ConfigManager.CogAgentDef'] = field(default_factory=list)
        memory: List['ConfigManager.CogMemoryDef'] = field(default_factory=list)
        flow: Optional['ConfigManager.CogFlow'] = None

    @dataclass
    class CogConfig:
        """
        Structured configuration object for cogs.
        
        NOTE: This object should not be mutated in place. For hot-reload support,
        replace the entire object with a new one from ConfigManager.build_cog_config().
        """
        cog: 'ConfigManager.CogDefinition'
        # Support for additional top-level fields
        custom_fields: Dict[str, Any] = field(default_factory=dict)

    # ==============================================================================
    # Builder Methods
    # ==============================================================================

    def build_agent_config(self, raw_agent_data: Dict[str, Any]) -> 'ConfigManager.AgentConfig':
        """
        Validates and normalizes a raw agent config dict, returning a structured AgentConfig object.
        Raises ValueError if required fields are missing or invalid.
        """
        # Validate required keys
        required_keys = ['params', 'prompts', 'settings']
        for key in required_keys:
            if key not in raw_agent_data:
                raise ValueError(f"Agent config missing required key '{key}' for agent '{raw_agent_data.get('name', '<unknown>')}'.")

        # Validate name is present
        if not raw_agent_data.get('name'):
            raise ValueError("Agent config missing required 'name' field.")

        # Validate prompts are not empty
        prompts = raw_agent_data.get('prompts', {})
        if not prompts or not isinstance(prompts, dict):
            raise ValueError(f"Agent '{raw_agent_data['name']}' must have a non-empty 'prompts' dictionary.")

        # Validate prompt format (structure and template syntax)
        try:
            self.check_prompt_format(prompts)
        except ValueError as e:
            raise ValueError(f"Agent '{raw_agent_data['name']}' has invalid prompt format: {e}")

        # Validate model is not None
        model = raw_agent_data.get('model')
        if model is None:
            raise ValueError(f"Agent '{raw_agent_data['name']}' must have a 'model' specified.")

        # Validate params is a dict
        params = raw_agent_data.get('params', {})
        if not isinstance(params, dict):
            raise ValueError(f"Agent '{raw_agent_data['name']}' params must be a dictionary.")

        # Parse and validate settings structure
        settings = self._build_settings(raw_agent_data['settings'])

        # Persona validation (warn, not error)
        persona = raw_agent_data.get('persona', None)
        if settings.system.persona.enabled and not persona:
            # In the future, could log a warning here
            pass

        # Extract core fields
        core_fields = {
            'name', 'settings', 'model', 'params', 'persona', 
            'prompts', 'simulated_response', 'parse_response_as'
        }
        
        # Collect any additional custom fields from the YAML
        custom_fields = {}
        for key, value in raw_agent_data.items():
            if key not in core_fields:
                custom_fields[key] = value

        # Return structured config object
        return self.AgentConfig(
            name=raw_agent_data['name'],
            settings=settings,
            model=model,
            params=params,
            persona=persona,
            prompts=prompts,
            simulated_response=raw_agent_data.get('simulated_response'),
            parse_response_as=raw_agent_data.get('parse_response_as'),
            custom_fields=custom_fields
        )

    def build_cog_config(self, raw_cog_data: Dict[str, Any]) -> 'ConfigManager.CogConfig':
        """
        Validates and normalizes a raw cog config dict, returning a structured CogConfig object.
        Raises ValueError if required fields are missing or invalid.
        """
        # Validate that 'cog' key exists
        if 'cog' not in raw_cog_data:
            raise ValueError("Cog config must have a 'cog' dictionary defined.")
        
        raw_cog = raw_cog_data['cog']
        if not isinstance(raw_cog, dict):
            raise ValueError("Cog 'cog' value must be a dictionary.")

        # Validate and build agents list
        agents = self._build_cog_agents(raw_cog.get('agents', []))
        
        # Validate and build memory list
        memory = self._build_cog_memory(raw_cog.get('memory', []))
        
        # Validate and build flow
        flow = self._build_cog_flow(raw_cog.get('flow'))

        # Build cog definition
        cog_def = self.CogDefinition(
            name=raw_cog.get('name', ''),
            description=raw_cog.get('description'),
            persona=raw_cog.get('persona'),
            trail_logging=raw_cog.get('trail_logging', True),
            agents=agents,
            memory=memory,
            flow=flow
        )

        # Extract any additional top-level custom fields
        custom_fields = {}
        for key, value in raw_cog_data.items():
            if key != 'cog':
                custom_fields[key] = value

        return self.CogConfig(
            cog=cog_def,
            custom_fields=custom_fields
        )

    # ==============================================================================
    # Private Builder Helper Methods
    # ==============================================================================

    def _build_settings(self, raw_settings: Dict[str, Any]) -> 'ConfigManager.Settings':
        """Build structured Settings object from raw settings dict."""
        # Validate system settings exist
        if 'system' not in raw_settings:
            raise ValueError("Settings missing required 'system' key.")
        
        raw_system = raw_settings['system']
        
        # Build system settings components
        persona_settings = self.PersonaSettings(
            enabled=raw_system.get('persona', {}).get('enabled', True),
            name=raw_system.get('persona', {}).get('name', 'DefaultAssistant'),
            static_char_cap=raw_system.get('persona', {}).get('static_char_cap', 8000)
        )
        
        debug_settings = self.DebugSettings(
            mode=raw_system.get('debug', {}).get('mode', False),
            save_memory=raw_system.get('debug', {}).get('save_memory', False),
            simulated_response=raw_system.get('debug', {}).get('simulated_response', 
                "Text designed to simulate an LLM response for debugging purposes without invoking the model.")
        )
        
        logging_settings = self.LoggingSettings(
            enabled=raw_system.get('logging', {}).get('enabled', True),
            console_level=raw_system.get('logging', {}).get('console_level', 'warning'),
            folder=raw_system.get('logging', {}).get('folder', './logs'),
            files=raw_system.get('logging', {}).get('files', {})
        )
        
        misc_settings = self.MiscSettings(
            on_the_fly=raw_system.get('misc', {}).get('on_the_fly', True)
        )
        
        path_settings = self.PathSettings(
            files=raw_system.get('paths', {}).get('files', './files')
        )
        
        system_settings = self.SystemSettings(
            persona=persona_settings,
            debug=debug_settings,
            logging=logging_settings,
            misc=misc_settings,
            paths=path_settings
        )
        
        return self.Settings(
            system=system_settings,
            models=raw_settings.get('models', {}),
            storage=raw_settings.get('storage', {})
        )

    def _build_cog_agents(self, raw_agents: List[Dict[str, Any]]) -> List['ConfigManager.CogAgentDef']:
        """Build list of CogAgentDef objects from raw agent definitions."""
        if not isinstance(raw_agents, list):
            raise ValueError("Cog agents must be a list.")
        
        agents = []
        for agent_def in raw_agents:
            if not isinstance(agent_def, dict):
                raise ValueError("Each agent definition must be a dictionary.")
            
            agent_id = agent_def.get('id')
            if not agent_id:
                raise ValueError("Every agent must have an 'id'.")
            
            # Validate that at least one of type or template_file is present
            if 'type' not in agent_def and 'template_file' not in agent_def:
                raise ValueError(f"Agent '{agent_id}' must have at least a 'type' or a 'template_file' defined.")
            
            agents.append(self.CogAgentDef(
                id=agent_id,
                template_file=agent_def.get('template_file'),
                type=agent_def.get('type')
            ))
        
        return agents

    def _build_cog_memory(self, raw_memory: List[Dict[str, Any]]) -> List['ConfigManager.CogMemoryDef']:
        """Build list of CogMemoryDef objects from raw memory definitions."""
        if not isinstance(raw_memory, list):
            return []  # Memory is optional
        
        memory_nodes = []
        for mem_def in raw_memory:
            if not isinstance(mem_def, dict):
                raise ValueError("Each memory definition must be a dictionary.")
            
            mem_id = mem_def.get('id')
            if not mem_id:
                raise ValueError("Every memory node must have an 'id'.")
            
            # Normalize query_before and update_after to handle both string and list formats
            query_before = mem_def.get('query_before')
            if isinstance(query_before, str):
                query_before = [query_before]
            elif query_before is None:
                query_before = []
            
            update_after = mem_def.get('update_after')
            if isinstance(update_after, str):
                update_after = [update_after]
            elif update_after is None:
                update_after = []
            
            memory_nodes.append(self.CogMemoryDef(
                id=mem_id,
                type=mem_def.get('type'),
                collection_id=mem_def.get('collection_id'),
                query_before=query_before,
                query_keys=mem_def.get('query_keys', []),
                update_after=update_after,
                update_keys=mem_def.get('update_keys', [])
            ))
        
        return memory_nodes

    def _build_cog_flow(self, raw_flow: Optional[Dict[str, Any]]) -> Optional['ConfigManager.CogFlow']:
        """Build CogFlow object from raw flow definition."""
        if not raw_flow:
            raise ValueError("Flow must be defined.")
        
        if not isinstance(raw_flow, dict):
            raise ValueError("Flow must be a dictionary.")
        
        # Validate required flow fields
        if 'start' not in raw_flow:
            raise ValueError("Flow must have a 'start' key.")
        
        if 'transitions' not in raw_flow:
            raise ValueError("Flow must have a 'transitions' dictionary defined.")
        
        raw_transitions = raw_flow['transitions']
        if not isinstance(raw_transitions, dict):
            raise ValueError("Flow 'transitions' must be a dictionary.")
        
        # Parse transitions
        transitions = {}
        for agent_id, transition_def in raw_transitions.items():
            transitions[agent_id] = self._parse_flow_transition(transition_def)
        
        return self.CogFlow(
            start=raw_flow['start'],
            transitions=transitions
        )

    def _parse_flow_transition(self, transition_def: Any) -> 'ConfigManager.CogFlowTransition':
        """Parse a single flow transition definition into a CogFlowTransition object."""
        if isinstance(transition_def, str):
            # Direct transition to another agent
            return self.CogFlowTransition(
                type="direct",
                next_agent=transition_def
            )
        
        if isinstance(transition_def, dict):
            # Check if this is an end transition
            if transition_def.get('end', False):
                return self.CogFlowTransition(
                    type="end",
                    end=True
                )
            
            # Check for decision transition
            reserved_keys = {'fallback', 'max_visits', 'end'}
            decision_key = None
            decision_map = {}
            
            for key, value in transition_def.items():
                if key not in reserved_keys:
                    if decision_key is not None:
                        raise ValueError(f"Multiple decision keys found in transition: {decision_key}, {key}")
                    decision_key = key
                    if isinstance(value, dict):
                        decision_map = value
                    else:
                        # Single value decision
                        decision_map = {str(value): value}
            
            if decision_key:
                return self.CogFlowTransition(
                    type="decision",
                    decision_key=decision_key,
                    decision_map=decision_map,
                    fallback=transition_def.get('fallback'),
                    max_visits=transition_def.get('max_visits')
                )
            
            # If no decision key found, this might be a malformed transition
            raise ValueError(f"Invalid transition definition: {transition_def}")
        
        raise ValueError(f"Transition must be string or dict, got: {type(transition_def)}")

    def check_prompt_format(self, prompts: Dict[str, Any]) -> None:
        """
        Validates that the prompts dictionary has the correct format.
        Raises ValueError if the prompts do not contain only 'system' and 'user' keys,
        or if the sub-prompts are not dictionaries or strings.
        """
        # Check if 'system' and 'user' are the only keys present
        if set(prompts.keys()) != {'system', 'user'}:
            raise ValueError(
                "Prompts should contain only 'system' and 'user' keys. "
                "Please check the prompt YAML file format."
            )

        # Allow 'system' and 'user' prompts to be either dicts or strings
        for prompt_type in ['system', 'user']:
            prompt_value = prompts.get(prompt_type, {})
            if not isinstance(prompt_value, (dict, str)):
                raise ValueError(
                    f"The '{prompt_type}' prompt should be either a string or a dictionary of sub-prompts."
                ) 