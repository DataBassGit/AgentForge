from typing import Dict, Any

from ...config import Config
from ..storage_interface import StorageInterface


class AgentUtils:

    def __init__(self):
        self.storage = StorageInterface()
        self.config = Config()

    def load_agent_data(self, agent_name):
        self.config.reload(agent_name)

        # defaults = self.config.data['Defaults']
        # objective = self.config.data['Objective']

        defaults = self.config.models['Defaults']
        objective = self.config.directives['Objective']

        agent = self.config.agent
        api = agent.get('API', defaults['API'])
        params = agent.get('Params', defaults['Params'])

        # Initialize agent data
        agent_data: Dict[str, Any] = dict(
            name=agent_name,
            llm=self.config.get_llm(api),
            objective=objective,
            prompts=agent['Prompts'],
            params=params,
            storage=StorageInterface().storage_utils,
        )

        return agent_data

    def prepare_objective(self):
        while True:
            user_input = input("\nDefine Objective (leave empty to use defaults): ")
            if user_input.lower() == '':
                return None
            else:
                self.config.data['Objective'] = user_input
                return user_input
