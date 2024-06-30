from agentforge.agent import Agent


class ActionSelectionAgent(Agent):

    def __init__(self, threshold: float = 0.6, num_results: int = 10) -> None:
        super().__init__()
        self.actions: dict = {}
        self.threshold = threshold  # Threshold value for action selection.
        self.num_results = num_results  # Number of results to be considered in the action selection process.

    def load_additional_data(self, **kwargs):
        pass

    def load_actions(self, objective: str):
        """
        Loads actions based on the current object and specified criteria from the storage system.
        """
        try:
            self.actions = self.agent_data['storage'].search_storage_by_threshold(collection_name='Actions',
                                                                                  query_text=objective,
                                                                                  threshold=self.threshold,
                                                                                  num_results=self.num_results)
        except Exception as e:
            self.logger.log(f"Error loading actions: {e}", 'error')
            self.actions = {}

    # def run(self, objective: str):
    #     pass
