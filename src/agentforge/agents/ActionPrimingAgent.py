from agentforge.agent import Agent


class ActionPrimingAgent(Agent):
    def load_additional_data(self):
        self.data["task"] = self.functions.task_handling.get_current_task()["document"]

    def build_output(self):
        try:
            self.output = self.functions.agent_utils.parse_yaml_string(self.result)
        except Exception as e:
            raise ValueError(f"\n\nError while building output for agent: {e}")

    def save_result(self):
        pass
