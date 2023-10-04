from typing import Dict, Any

from ...config import Config
from ..storage_interface import StorageInterface


class AgentUtils:

    def __init__(self):
        self.config = Config()

    def load_agent_data(self, agent_name):
        self.config.reload(agent_name)

        agent = self.config.agent
        objective = self.config.settings['directives']['Objective']

        defaults = self.config.settings['models']['ModelSettings']
        settings = agent.get('ModelOverrides', defaults)

        # Initialize agent data
        agent_data: Dict[str, Any] = dict(
            name=agent_name,
            llm=self.config.get_llm(settings['API']),
            objective=objective,
            prompts=agent['Prompts'],
            params=settings['Params'],
            storage=StorageInterface().storage_utils,
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
