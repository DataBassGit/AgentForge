from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List, Union

# Import dataclasses from config_structs modules
from ..config_structs import (
    # Agent config structs
    PersonaSettings,
    DebugSettings,
    LoggingSettings,
    MiscSettings,
    PathSettings,
    SystemSettings,
    Settings,
    AgentConfig,
    # Cog config structs
    CogAgentDef,
    CogMemoryDef,
    CogFlowTransition,
    CogFlow,
    CogDefinition,
    CogConfig,
)

# from agentforge.utils.logger import Logger


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
        self._initialize_processors()

    def _initialize_processors(self):
        """Initialize any required processors or internal state."""
        pass

    def debug_print(self, msg: str, settings: dict):
        """Print debug messages if debug mode is enabled in settings dict."""
        debug_mode = False
        # Try to get debug flag from settings dict
        if isinstance(settings, dict):
            debug_mode = settings.get('system', {}).get('debug', {}).get('mode', False)
        if debug_mode:
            print(msg)

    # ==============================================================================
    # Builder Methods
    # ==============================================================================

    def build_agent_config(self, raw_agent_data: Dict[str, Any]) -> AgentConfig:
        """
        Validates and normalizes a raw agent config dict, returning a structured AgentConfig object.
        Raises ValueError if required fields are missing or invalid.
        """
        try:
            self._validate_agent_config(raw_agent_data)
            agent_config = self._normalize_agent_config(raw_agent_data)
            self.debug_print(f"Agent config for '{raw_agent_data.get('name', '<unknown>')}' built successfully.", raw_agent_data.get('settings', {}))
            return agent_config
        except Exception as e:
            self.debug_print(f"Failed to build agent config: {e}", raw_agent_data.get('settings', {}))
            raise

    def _validate_agent_config(self, raw_agent_data: Dict[str, Any]) -> None:
        """Validate required fields and structure for agent config."""
        required_keys = ['params', 'prompts', 'settings']
        for key in required_keys:
            if key not in raw_agent_data:
                raise ValueError(f"Agent config missing required key '{key}' for agent '{raw_agent_data.get('name', '<unknown>')}'.")

        if not raw_agent_data.get('name'):
            raise ValueError("Agent config missing required 'name' field.")

        prompts = raw_agent_data.get('prompts', {})
        if not prompts or not isinstance(prompts, dict):
            raise ValueError(f"Agent '{raw_agent_data.get('name', '<unknown>')}' must have a non-empty 'prompts' dictionary.")

        try:
            self._validate_prompt_format(prompts)
        except ValueError as e:
            raise ValueError(f"Agent '{raw_agent_data.get('name', '<unknown>')}' has invalid prompt format: {e}")

        model = raw_agent_data.get('model')
        if model is None:
            raise ValueError(f"Agent '{raw_agent_data.get('name', '<unknown>')}' must have a 'model' specified.")

        params = raw_agent_data.get('params', {})
        if not isinstance(params, dict):
            raise ValueError(f"Agent '{raw_agent_data.get('name', '<unknown>')}' params must be a dictionary.")

        persona = raw_agent_data.get('persona')
        if persona is not None and not isinstance(persona, dict):
            self.debug_print(f"Agent '{raw_agent_data.get('name', '<unknown>')}' persona should be a dictionary, got {type(persona)}", raw_agent_data.get('settings', {}))

    def _normalize_agent_config(self, raw_agent_data: Dict[str, Any]) -> AgentConfig:
        """Normalize and construct AgentConfig object from validated raw data."""
        settings = self._build_settings(raw_agent_data['settings'])
        reserved_fields = {'name', 'settings', 'model', 'params', 'prompts', 'persona', 'simulated_response', 'parse_response_as'}
        custom_fields = {key: value for key, value in raw_agent_data.items() if key not in reserved_fields}
        return AgentConfig(
            name=raw_agent_data['name'],
            settings=settings,
            model=raw_agent_data['model'],
            params=raw_agent_data['params'],
            prompts=raw_agent_data['prompts'],
            persona=raw_agent_data.get('persona'),
            simulated_response=raw_agent_data.get('simulated_response'),
            parse_response_as=raw_agent_data.get('parse_response_as'),
            custom_fields=custom_fields
        )

    def _validate_prompt_format(self, prompts: Dict[str, Any]) -> None:
        """
        Validates that the prompts dictionary has the correct format.
        Raises ValueError if the prompts do not contain only 'system' and 'user' keys,
        or if the sub-prompts are not dictionaries or strings.
        """
        if set(prompts.keys()) != {'system', 'user'}:
            raise ValueError(
                "Prompts should contain only 'system' and 'user' keys. "
                "Please check the prompt YAML file format."
            )
        for prompt_type in ['system', 'user']:
            prompt_value = prompts.get(prompt_type, {})
            if not isinstance(prompt_value, (dict, str)):
                raise ValueError(
                    f"The '{prompt_type}' prompt should be either a string or a dictionary of sub-prompts."
                )

    def build_cog_config(self, raw_cog_data: Dict[str, Any]) -> CogConfig:
        """
        Validates and normalizes a raw cog config dict, returning a structured CogConfig object.
        Raises ValueError if required fields are missing or invalid.
        """
        try:
            self._validate_cog_config(raw_cog_data)
            cog_config = self._normalize_cog_config(raw_cog_data)
            # Try to get debug flag from cog settings if present, else from agent/global settings if available
            settings = None
            if 'settings' in raw_cog_data:
                settings = raw_cog_data['settings']
            elif 'cog' in raw_cog_data and 'settings' in raw_cog_data['cog']:
                settings = raw_cog_data['cog']['settings']
            self.debug_print("Cog config built successfully.", settings or {})
            return cog_config
        except Exception as e:
            settings = None
            if 'settings' in raw_cog_data:
                settings = raw_cog_data['settings']
            elif 'cog' in raw_cog_data and 'settings' in raw_cog_data['cog']:
                settings = raw_cog_data['cog']['settings']
            self.debug_print(f"Failed to build cog config: {e}", settings or {})
            raise

    def _validate_cog_config(self, raw_cog_data: Dict[str, Any]) -> None:
        """Validate required fields and structure for cog config."""
        if 'cog' not in raw_cog_data:
            raise ValueError("Cog config must have a 'cog' dictionary defined.")
        raw_cog = raw_cog_data['cog']
        if not isinstance(raw_cog, dict):
            raise ValueError("Cog 'cog' value must be a dictionary.")
        if 'flow' not in raw_cog or raw_cog.get('flow') is None:
            raise ValueError("Cog 'flow' must be defined.")
        if 'agents' not in raw_cog or not isinstance(raw_cog.get('agents'), list):
            raise ValueError("Cog 'agents' must be a list.")
        # Additional validation can be added here as needed

    def _normalize_cog_config(self, raw_cog_data: Dict[str, Any]) -> CogConfig:
        """Normalize and construct CogConfig object from validated raw data."""
        raw_cog = raw_cog_data['cog']
        agents = self._build_cog_agents(raw_cog.get('agents', []))
        memory = self._build_cog_memory(raw_cog.get('memory', []))
        flow = self._build_cog_flow(raw_cog.get('flow'))
        self._validate_agent_modules(agents)
        self._validate_flow_references(flow, agents)
        cog_def = CogDefinition(
            name=raw_cog.get('name', ''),
            description=raw_cog.get('description'),
            persona=raw_cog.get('persona'),
            trail_logging=raw_cog.get('trail_logging', True),
            agents=agents,
            memory=memory,
            flow=flow
        )
        custom_fields = {key: value for key, value in raw_cog_data.items() if key != 'cog'}
        return CogConfig(
            cog=cog_def,
            custom_fields=custom_fields
        )

    # ==============================================================================
    # Private Helper Methods
    # ==============================================================================

    def _build_settings(self, raw_settings: Dict[str, Any]) -> Settings:
        """Build structured Settings object from raw settings dict."""
        raw_system = raw_settings.get('system', {})
        
        persona_settings = PersonaSettings(
            enabled=raw_system.get('persona', {}).get('enabled', True),
            name=raw_system.get('persona', {}).get('name', 'default_assistant'),
            static_char_cap=raw_system.get('persona', {}).get('static_char_cap', 8000)
        )
        
        debug_settings = DebugSettings(
            mode=raw_system.get('debug', {}).get('mode', False),
            save_memory=raw_system.get('debug', {}).get('save_memory', False),
            simulated_response=raw_system.get('debug', {}).get('simulated_response', 
                "Text designed to simulate an LLM response for debugging purposes without invoking the model.")
        )
        
        logging_settings = LoggingSettings(
            enabled=raw_system.get('logging', {}).get('enabled', True),
            console_level=raw_system.get('logging', {}).get('console_level', 'warning'),
            folder=raw_system.get('logging', {}).get('folder', './logs'),
            files=raw_system.get('logging', {}).get('files', {})
        )
        
        misc_settings = MiscSettings(
            on_the_fly=raw_system.get('misc', {}).get('on_the_fly', True)
        )
        
        path_settings = PathSettings(
            files=raw_system.get('paths', {}).get('files', './files')
        )
        
        system_settings = SystemSettings(
            persona=persona_settings,
            debug=debug_settings,
            logging=logging_settings,
            misc=misc_settings,
            paths=path_settings
        )
        
        return Settings(
            system=system_settings,
            models=raw_settings.get('models', {}),
            storage=raw_settings.get('storage', {})
        )

    def _build_cog_agents(self, raw_agents: List[Dict[str, Any]]) -> List[CogAgentDef]:
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
            
            agents.append(CogAgentDef(
                id=agent_id,
                template_file=agent_def.get('template_file'),
                type=agent_def.get('type')
            ))
        
        return agents

    def _build_cog_memory(self, raw_memory: List[Dict[str, Any]]) -> List[CogMemoryDef]:
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
            
            memory_nodes.append(CogMemoryDef(
                id=mem_id,
                type=mem_def.get('type'),
                collection_id=mem_def.get('collection_id'),
                query_before=query_before,
                query_keys=mem_def.get('query_keys', []),
                update_after=update_after,
                update_keys=mem_def.get('update_keys', [])
            ))
        
        return memory_nodes

    def _build_cog_flow(self, raw_flow: Optional[Dict[str, Any]]) -> Optional[CogFlow]:
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
        
        return CogFlow(
            start=raw_flow['start'],
            transitions=transitions
        )

    def _parse_flow_transition(self, transition_def: Any) -> CogFlowTransition:
        """Parse a single flow transition definition into a CogFlowTransition object."""
        if isinstance(transition_def, str):
            # Direct transition to another agent
            return CogFlowTransition(
                type="direct",
                next_agent=transition_def
            )
        
        if isinstance(transition_def, dict):
            # Check if this is an end transition
            if 'end' in transition_def:
                return CogFlowTransition(
                    type="end",
                    end=transition_def['end']
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
                return CogFlowTransition(
                    type="decision",
                    decision_key=decision_key,
                    decision_map=decision_map,
                    fallback=transition_def.get('fallback'),
                    max_visits=transition_def.get('max_visits')
                )
            
            # If no decision key found, this might be a malformed transition
            raise ValueError(f"Invalid transition definition: {transition_def}")
        
        raise ValueError(f"Transition must be string or dict, got: {type(transition_def)}")

    def _validate_agent_modules(self, agents: List[CogAgentDef]) -> None:
        """Validate that agent modules exist and can be imported."""
        for agent in agents:
            if agent.type:
                self._validate_module_exists(agent.type, agent.id)

    def _validate_module_exists(self, full_class_path: str, agent_id: str) -> None:
        """
        Validate that the module exists and contains the specified class.
        
        Args:
            full_class_path: The full module.ClassName path
            agent_id: The agent ID for error messages
            
        Raises:
            ValueError: If the module path format is invalid
            ImportError: If the module or class cannot be found
        """
        from agentforge.config import Config
        # Use Config.resolve_class to validate - we don't need the returned class
        Config.resolve_class(full_class_path, context=f"agent '{agent_id}'")

    def _validate_flow_references(self, flow: CogFlow, agents: List[CogAgentDef]) -> None:
        """Validate that flow references valid agent IDs."""
        if not flow:
            return
            
        agent_ids = {agent.id for agent in agents}
        
        # Validate start agent exists
        if flow.start not in agent_ids:
            raise ValueError(f"Flow start agent '{flow.start}' not found in agents list.")
        
        # Validate all transition references
        for agent_id, transition in flow.transitions.items():
            if agent_id not in agent_ids:
                raise ValueError(f"Transition defined for unknown agent '{agent_id}'.")
            
            # Check transition targets
            if transition.type == "direct" and transition.next_agent:
                if transition.next_agent not in agent_ids:
                    raise ValueError(f"Transition from '{agent_id}' references unknown agent '{transition.next_agent}'.")
            elif transition.type == "decision" and transition.decision_map:
                for decision_value, target_agent in transition.decision_map.items():
                    if target_agent not in agent_ids:
                        raise ValueError(f"Decision transition from '{agent_id}' references unknown agent '{target_agent}'.")
            
            # Check fallback references
            if transition.fallback and transition.fallback not in agent_ids:
                raise ValueError(f"Fallback from '{agent_id}' references unknown agent '{transition.fallback}'.")

        # Warn if no end transition is present
        has_end_transition = any(
            transition.type == "end" or transition.end
            for transition in flow.transitions.values()
        )
        
        if not has_end_transition:
            print("Flow has no 'end:' transition; cog may loop forever.") 