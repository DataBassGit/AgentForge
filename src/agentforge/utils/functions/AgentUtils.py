from typing import Dict, Any

from ...config import Config
from ..storage_interface import StorageInterface


class AgentUtils:

    def __init__(self):
        self.config = Config()

    def load_agent_data(self, agent_name):
        self.config.reload(agent_name)

        agent = self.config.agent
        settings = self.config.settings

        # Check for a Persona override in the agent's configuration
        agent_persona_override = agent.get('Persona', None)

        # Use the overridden persona if available, or default to the system's predefined persona_name
        persona_name = agent_persona_override or self.config.persona_name

        # Check if the selected persona exists
        if persona_name not in self.config.personas:
            raise FileNotFoundError(
                f"Persona file for '{persona_name}' not found. Please check your persona configuration.")

        # Load the selected persona
        persona = self.config.personas[persona_name]

        # Check for API and model_name overrides in the agent's ModelOverrides
        agent_api_override = agent.get('ModelOverrides', {}).get('API', None)
        agent_model_override = agent.get('ModelOverrides', {}).get('Model', None)

        # Use overrides if available, otherwise default to the settings
        api = agent_api_override or settings['models']['ModelSettings']['API']
        model = agent_model_override or settings['models']['ModelSettings']['Model']

        # Load default model parameter settings
        default_params = settings['models']['ModelSettings']['Params']

        # Load model-specific settings (if any)
        model_params = settings['models']['ModelLibrary'][api]['models'].get(model, {}).get('params', {})

        # Merge default settings with model-specific settings
        combined_params = {**default_params, **model_params}

        # Apply agent's parameter overrides (if any)
        agent_params_overrides = agent.get('ModelOverrides', {}).get('Params', {})
        final_model_params = {**combined_params, **agent_params_overrides}

        # Initialize agent data
        agent_data: Dict[str, Any] = dict(
            name=agent_name,
            settings=settings,
            llm=self.config.get_llm(api, model),
            params=final_model_params,
            prompts=agent['Prompts'],
            storage=StorageInterface().storage_utils,
            persona=persona,
        )

        return agent_data

    def prepare_objective(self):
        while True:
            user_input = input("\nDefine Objective (leave empty to use defaults): ")
            if user_input.lower() == '':
                return None
            else:
                self.config.settings['directives']['Objective'] = user_input
                return user_input
