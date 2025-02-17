# tests/cog_tests/test_cog_flow.py

import unittest
from typing import Dict, List
from unittest.mock import patch
from tests.base_test_case import BaseTestCase
from agentforge.cog import Cog

# Import dummy agents for later overriding if needed.
from tests.cog_tests import dummy_agents

dummy_agent_path = "dummy_agents.DummyAgent"
decision_agent_path = "dummy_agents.DecisionAgent"

class TestCogFlow(BaseTestCase):

    def _define_fake_config(self):
        self.test_definition = {}

    def _patch_config(self):
        patcher = patch.object(Cog, '_load_cog_config',
                               lambda instance: setattr(instance, "cog_config", self.test_definition.copy()))
        self.addCleanup(patcher.stop)
        patcher.start()

    def setUp(self):
        super().setUp()
        self._define_fake_config()
        self._patch_config()
        self.engine = Cog("dummy", enable_trail_logging=True)

class TestSimpleCogFlow(TestCogFlow):

    def _define_fake_config(self):
        self.test_definition = {
            "cog": {
                "name": "DecisionFlowExample",
                "description": "A Cog example to test decision branching.",
                "agents": [
                    {"id": "A1", "type": dummy_agent_path},
                    {"id": "A2", "type": decision_agent_path, "template_file": "DummyTemplate"},
                    {"id": "A3", "type": dummy_agent_path}
                ],
                "flow": {
                    "start": "A1",
                    "transitions": {
                        "A1": "A2",
                        "A2": {
                            "conclusion": {
                                "positive": "A3",
                                "negative": "A1",
                                "default": "A3"
                            }
                        },
                        "A3": {"end": True}
                    }
                }
            }
        }

    def setUp(self):
        super().setUp()

        self.engine.agents["A1"] = dummy_agents.DummyAgent("A1 complete")
        self.engine.agents["A2"] = dummy_agents.DecisionAgent("positive")
        self.engine.agents["A3"] = dummy_agents.DummyAgent({"final": True})

    def test_decision_flow_execution(self):
        context = self.engine.execute()
        self.assertTrue(context["A3"].get("final"))

        # Since we go through 3 agent, we expect 1 thought flow trail with 3 agents .
        self.assertEqual(len(self.engine.thought_flow_trail), 1)
        self.assertEqual(len(self.engine.thought_flow_trail[0]), 3)


class TestCogAgentFailure(TestCogFlow):

    def _define_fake_config(self):
        self.test_definition = {
            "cog": {
                "name": "FailureFlowExample",
                "description": "A Cog example to test agent failure handling.",
                "agents": [
                    {"id": "A1", "type": dummy_agent_path},
                    {"id": "A2", "type": dummy_agent_path},
                    {"id": "A3", "type": dummy_agent_path}
                ],
                "flow": {
                    "start": "A1",
                    "transitions": {
                        "A1": "A2",
                        "A2": "A3",
                        "A3": {"end": True}
                    }
                }
            }
        }

    def setUp(self):
        super().setUp()

        self.engine.agents["A1"] = dummy_agents.DummyAgent("A1 complete")
        self.engine.agents["A2"] = dummy_agents.DummyAgent(None)
        self.engine.agents["A3"] = dummy_agents.DummyAgent({"final": True})

    def test_agent_failure_on_flow(self):
        context = self.engine.execute()
        self.assertIsNone(context)


if __name__ == '__main__':
    unittest.main()
