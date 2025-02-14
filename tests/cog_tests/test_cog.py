# tests/cog_tests/test_cog_flow.py

import unittest
from typing import Dict, List
from unittest.mock import patch
from tests.base_test_case import BaseTestCase
from agentforge.cog import Cog

# Import dummy agents for later overriding if needed.
from tests.cog_tests import dummy_agents

dummy_agent_path = "tests.cog_tests.dummy_agents.DummyAgent"
decision_agent_path = "tests.cog_tests.dummy_agents.DecisionAgent"
failing_agent_path = "tests.cog_tests.dummy_agents.FailingAgent"

class TestCogLoading(BaseTestCase):
    def test_load_cog_yaml(self):
        # Ensure the test cog YAML file is present in the config
        expected_cog = self.config.load_cog_data('simple_flow')
        self.assertIn('cog', expected_cog, "Expected 'simple_flow.yaml' in config data under cogs")

        # Instantiate the Cog with the file name (without extension)
        engine = Cog("simple_flow")

        # Verify that the loaded definition matches what we expect from the config
        self.assertEqual(engine.cog, expected_cog)


class TestCogSimpleFlow(BaseTestCase):

    def setUp(self):
        super().setUp()

        # Define a test YAML definition as a dictionary.
        self.test_definition = {
            "cog": {
                "name": "SimpleFlowExample",
                "description": "A simple Cog example to test linear flows.",
                "agents": [
                    {"id": "A1", "type": dummy_agent_path},
                    {"id": "A2", "type": decision_agent_path, "template_file": "DummyTemplate"},
                    {"id": "A3", "type": dummy_agent_path, "template_file": "AlternateDummyTemplate"}
                ],
                "flow": {
                    "start": "A1",
                    "transitions": {
                        "A1": "A2",
                        "A2": {
                            "decision": {
                                "continue": "A3",
                                "loop": "A1",
                                "default": "A3"
                            }
                        },
                        "A3": {"end": True}
                    }
                }
            }
        }

        # Patch _load_flow_data so that it sets self.cog from our test definition.
        def load_flow_data_patch(instance, test_definition=None):
            if test_definition is None:
                test_definition = self.test_definition
            instance.cog = test_definition["cog"].copy()

        patcher = patch.object(Cog, '_load_flow_data', load_flow_data_patch)
        self.addCleanup(patcher.stop)
        patcher.start()

        # Instantiate Cog; _load_flow_data is patched, so __init__ will call _build_nodes.
        self.engine = Cog("dummy", enable_trail_logging=True)

        # Optionally, override nodes with our dummy agents to control behavior.
        self.engine.nodes["A1"] = dummy_agents.DummyAgent({"step": "A1 complete"})
        self.engine.nodes["A2"] = dummy_agents.DecisionAgent("continue")
        self.engine.nodes["A3"] = dummy_agents.DummyAgent({"final": True})

    def test_simple_flow_execution(self):
        context = self.engine.execute()
        self.assertTrue(context.get("final"))
        # Expect one snapshot per node execution: A1, A2, and A3.
        self.assertEqual(len(self.engine.thought_flow_trail), 3)


class TestCogDecisionFlow(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.test_definition = {
            "cog": {
                "name": "DecisionFlowExample",
                "description": "A Cog example to test decision branching.",
                "agents": [
                    {"id": "A1", "type": "tests.dummy_agents.DummyAgent"},
                    {"id": "A2", "type": "tests.dummy_agents.DecisionAgent", "template_file": "DummyTemplate"},
                    {"id": "A3", "type": "tests.dummy_agents.DummyAgent"}
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
        patcher = patch.object(Cog, '_load_flow_data',
                               lambda instance: setattr(instance, "cog", self.test_definition["cog"].copy()))
        self.addCleanup(patcher.stop)
        patcher.start()

        self.engine = Cog("dummy", enable_trail_logging=True)

        self.engine.nodes["A1"] = dummy_agents.DummyAgent("A1", {"step": "A1 complete"})

        self.call_count = 0

        def dynamic_decision_run(**context):
            self.call_count += 1
            decision = "negative" if self.call_count == 1 else "positive"
            return {"conclusion": decision}

        decision_agent = dummy_agents.DecisionAgent("A2", "positive")
        decision_agent.run = dynamic_decision_run
        self.engine.nodes["A2"] = decision_agent
        self.engine.nodes["A3"] = dummy_agents.DummyAgent("A3", {"final": True})

    def test_decision_flow_execution(self):
        context = self.engine.execute()
        self.assertTrue(context.get("final"))
        # Since we looped once, expect more than three snapshots.
        self.assertGreater(len(self.engine.thought_flow_trail), 3)


class TestCogAgentFailure(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.test_definition = {
            "cog": {
                "name": "FailureFlowExample",
                "description": "A Cog example to test agent failure handling.",
                "agents": [
                    {"id": "A1", "type": "tests.dummy_agents.DummyAgent"},
                    {"id": "A2", "type": "tests.dummy_agents.FailingAgent"},
                    {"id": "A3", "type": "tests.dummy_agents.DummyAgent"}
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
        patcher = patch.object(Cog, '_load_flow_data',
                               lambda instance: setattr(instance, "cog", self.test_definition["cog"].copy()))
        self.addCleanup(patcher.stop)
        patcher.start()

        self.engine = Cog("dummy", enable_trail_logging=True)
        self.engine.nodes["A1"] = dummy_agents.DummyAgent("A1", {"step": "A1 complete"})
        self.engine.nodes["A2"] = dummy_agents.FailingAgent("A2")
        self.engine.nodes["A3"] = dummy_agents.DummyAgent("A3", {"final": True})

    def test_agent_failure_on_flow(self):
        context = self.engine.execute()
        self.assertIsNone(context)


if __name__ == '__main__':
    unittest.main()
