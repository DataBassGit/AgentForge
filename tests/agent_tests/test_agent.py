import unittest
from agentforge.agent import Agent
from agentforge.config import Config

class TestAgent(unittest.TestCase):
    # Provide an explicit path to .agentforge (within your test directory or setup_files)
    test_root = "../src/agentforge/setup_files"  # Adjust as needed
    config_override = Config(root_path=test_root)

    def test_agent_init(self):
        agent = Agent(agent_name="TestAgent")
        self.assertEqual(agent.agent_name, "TestAgent")
        self.assertIsNotNone(agent.logger)
        self.assertIsNotNone(agent.config)
        self.assertIsNotNone(agent.prompt_processor)

if __name__ == '__main__':
    unittest.main()
