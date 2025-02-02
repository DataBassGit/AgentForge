# test_config_integration.py

import unittest
from agentforge.config import Config
from tests.base_test_case import BaseTestCase, BaseTestCaseEmptyAgentForgeFolder, BaseTestCaseNoAgentForgeFolder


class TestConfigIntegrationNoAgentForge(BaseTestCaseNoAgentForgeFolder):

    def test_no_agentforge_folder_raises(self):
        with self.assertRaises(FileNotFoundError):
            Config(root_path=str(self.temp_root_path))


class TestConfigIntegrationEmptyAgentForge(BaseTestCaseEmptyAgentForgeFolder):

    def test_empty_agentforge_loads_no_settings(self):
        config = Config(root_path=self.temp_root_path)
        self.assertEqual(config.data, {}, "Expected an empty config.data but got something else")

class TestConfigIntegration(BaseTestCase):

    def test_custom_root_path(self):
        # Assert known configs from real .agentforge is loaded
        self.assertIn("actions", self.config.data)
        self.assertIn("personas", self.config.data)
        self.assertIn("prompts", self.config.data)
        self.assertIn("settings", self.config.data)
        self.assertIn("tools", self.config.data)

        # Assert Setting Files are loaded
        self.assertIn("models", self.config.data["settings"])
        self.assertIn("storage", self.config.data["settings"])
        self.assertIn("system", self.config.data["settings"])

        # Assert settings are set to the correct default value
        self.assertTrue(self.config.data["settings"]["system"]["persona"].get("enabled"))

        # ... maybe we write a separate test for validating a system, storage and models files ...

if __name__ == '__main__':
    unittest.main()