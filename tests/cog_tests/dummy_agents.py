# tests/cog_tests/dummy_agents.py

class DummyAgent:
    def __init__(self, simulated_output=None):
        self.simulated_output = simulated_output or {}
        self.template_data = {}

    def run(self, **context):
        return self.simulated_output

class DecisionAgent:
    def __init__(self, decision_value=None):
        self.decision_value = decision_value or ""
        self.template_data = {}

    def run(self, **context):
        # For testing, return the decision using a key "conclusion"
        return {"conclusion": self.decision_value}

class FailingAgent:
    def __init__(self):
        self.template_data = {}

    def run(self, **context):
        raise Exception("Simulated failure")
