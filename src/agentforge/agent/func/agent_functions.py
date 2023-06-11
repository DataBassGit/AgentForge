from typing import Dict, Any

from ... import config
from ...utils.storage_interface import StorageInterface


class AgentFunctions:

    def __init__(self, agent_name):
        # Load persona data
        self.persona_data = config.persona()

        # Load API and Model
        language_model_api = self.persona_data[agent_name]['API']
        generate_text = config._set_model_api(language_model_api)
        model = self.persona_data[agent_name]['Model']

        # Initialize agent data
        self.agent_data: Dict[str, Any] = dict(
            name=agent_name,
            generate_text=generate_text,
            storage=StorageInterface(),
            objective=self.persona_data['Objective'],
            model=config.model_library(model),
            prompts=self.persona_data[agent_name]['Prompts'],
            params=self.persona_data[agent_name]['Params'],
        )

        if "HeuristicImperatives" in self.persona_data:
            imperatives = self.persona_data["HeuristicImperatives"]
            self.agent_data.update(heuristic_imperatives=imperatives)
