# test_agent.py
import unittest
from unittest.mock import patch
from tests.base_test_case import BaseTestCase
from agentforge.agent import Agent
from agentforge.config import Config


# A simple dummy model to satisfy load_model; it won’t be called in debug mode.
class DummyModel:
    @staticmethod
    def generate(prompt, **params):
        return "Generated text"

class TestAgent(BaseTestCase):

    def setUp(self):
        super().setUp()

        # Create a dummy agent configuration that satisfies required keys.
        self.dummy_agent_data = {
            "params": {},
            "prompts": {
                "system": "You are a helpful assistant called {name}.",
                "user": "{user_input}"
            },
            "settings": {
                "system": {
                    "debug": {"mode": True},
                    "persona": {"enabled": False},
                    "misc": {"on_the_fly": False},
                    "logging": {
                        "enabled": False,
                        "console_level": "critical"
                    }
                },
                # Minimal dummy model settings – not used directly
                "models": {"default_model": {}},
                # Disable storage for this test
                "storage": {"options": {"enabled": False}}
            },
            "simulated_response": "Simulated Response Text",
            "model": DummyModel()
        }

    def test_run_returns_simulated_response(self):
        with patch.object(Config, 'load_agent_data', return_value=self.dummy_agent_data.copy()):
            agent = Agent("TestAgent")
            test_name = 'TestBot'
            test_user_input = 'dummy user input'
            test_prompt = {'system': f'You are a helpful assistant called {test_name}.', 'user': test_user_input}

            # Run Test Agent
            result = agent.run(name=test_name, user_input=test_user_input)

            # Verify result returns the simulates response
            self.assertEqual(result, "Simulated Response Text")

            # Verify that the run() call updated template_data with our kwargs.
            self.assertIn("name", agent.template_data)
            self.assertIn("user_input", agent.template_data)
            self.assertEqual(agent.template_data["name"], test_name)
            self.assertEqual(agent.template_data["user_input"], test_user_input)
            # Verify prompt was rendered correctly
            self.assertEqual(agent.prompt, test_prompt)

    def test_missing_prompts_raises_error(self):
        # Remove 'prompts' to simulate a misconfigured agent and check for ValueError.
        broken_config = self.dummy_agent_data.copy()
        del broken_config["prompts"]
        with patch.object(Config, 'load_agent_data', return_value=broken_config):
            with self.assertRaises(ValueError) as context:
                Agent("TestAgent")
            self.assertIn("Agent data missing required key 'prompts'", str(context.exception))

    def test_missing_model_raises_error(self):
        # Remove 'model' from configuration to force a ValueError in load_model.
        broken_config = self.dummy_agent_data.copy()
        del broken_config["model"]
        with patch.object(Config, 'load_agent_data', return_value=broken_config):
            with self.assertRaises(ValueError) as context:
                Agent("TestAgent")
            self.assertIn("Model not specified", str(context.exception))

    def test_missing_required_agent_data_key_raises_error(self):
        # Remove a required key (e.g., 'params') from the configuration.
        broken_config = self.dummy_agent_data.copy()
        del broken_config["params"]
        with patch.object(Config, 'load_agent_data', return_value=broken_config):
            with self.assertRaises(ValueError) as context:
                Agent("TestAgent")
            self.assertIn("missing required key 'params'", str(context.exception).lower())

    def test_run_handles_exception_and_returns_none(self):
        # Patch process_data to simulate an error, ensuring that run() returns None.
        with patch.object(Config, 'load_agent_data', return_value=self.dummy_agent_data.copy()):
            agent = Agent("TestAgent")
            with patch.object(agent, "process_data", side_effect=Exception("Test exception")):
                result = agent.run(user_input="dummy")
                self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
