# test_config_unit.py

import unittest
from unittest.mock import patch, MagicMock
from agentforge.config import Config
from tests.base_test_case import BaseTestCase, BaseTestCaseEmptyAgentForgeFolder, BaseTestCaseNoAgentForgeFolder

class TestConfigNoAgentForge(BaseTestCaseNoAgentForgeFolder):

    def test_config_raises_FileNotFound_for_missing_folder(self):
        # temp_root_path is a custom root path that does NOT contain .agentforge
        # We expect a FileNotFoundError to be raised
        with self.assertRaises(FileNotFoundError):
            Config(root_path=str(self.temp_root_path))


class TestEmptyConfig(BaseTestCaseEmptyAgentForgeFolder):

    @patch.object(Config, 'find_project_root')
    def test_config_without_root_path(self, mock_find_project_root):
        # Instead of letting it do the real search, we'll just ensure it *calls* find_project_root
        # then we’ll simulate returning the same directory we set up in setUp.
        mock_find_project_root.return_value = self.temp_root_path.resolve()

        config = Config()

        mock_find_project_root.assert_called_once()
        self.assertEqual(config.project_root, self.temp_root_path.resolve())
        self.assertTrue(config.config_path.is_dir())


class TestConfig(BaseTestCase):

    def test_config_with_custom_root_path(self):
        # Ensure that the discovered project_root is exactly our temp directory
        self.assertEqual(self.config.project_root, self.temp_root_path.resolve())
        self.assertTrue(self.config.config_path.is_dir(), "config_path should point to an existing .agentforge directory")

    @patch.object(Config, 'reload', return_value=None)
    def test_load_agent_data_agent_not_found(self, mock_reload):
        # We'll raise FileNotFoundError if the agent is not found
        with self.assertRaises(FileNotFoundError):
            self.config.load_agent_data("MissingAgent")


if __name__ == '__main__':
    unittest.main()
