import unittest
import tempfile
import pathlib
import os
from unittest.mock import patch, MagicMock
from agentforge.config import Config


class TestConfig(unittest.TestCase):

    # ---------------------------------
    # Prep.
    # ---------------------------------

    def setUp(self):
        # Create a temporary directory that we'll treat as our custom root
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_root_path = pathlib.Path(self.temp_dir.name)

        # Make a .agentforge folder inside our temp root
        self.agentforge_dir = self.temp_root_path / ".agentforge"
        self.agentforge_dir.mkdir()

        # Optionally, create some subdirectories or YAML files in there
        # so it looks more like your real setup_files
        # (Not strictly necessary if you just want to confirm that .agentforge is found)

        # For instance:
        # (self.agentforge_dir / 'settings').mkdir()
        # (self.agentforge_dir / 'settings' / 'system.yaml').write_text("system: {}\n")

    def tearDown(self):
        # Clean up the Config class and temporary directory after each test
        Config._instance = None
        self.temp_dir.cleanup()

    # ---------------------------------
    # Tests
    # ---------------------------------

    def test_config_invalid_custom_root_path(self):
        # Provide a custom root path that does NOT contain .agentforge
        with tempfile.TemporaryDirectory() as dummy_dir:
            dummy_root = pathlib.Path(dummy_dir)

            # We expect a FileNotFoundError to be raised
            with self.assertRaises(FileNotFoundError):
                Config(root_path=str(dummy_root))

    def test_config_with_custom_root_path(self):
        # Pass in the temporary directory as root_path
        config = Config(root_path=str(self.temp_root_path))

        # Ensure that the discovered project_root is exactly our temp directory
        self.assertEqual(config.project_root, self.temp_root_path.resolve())
        self.assertTrue(config.config_path.is_dir(), "config_path should point to an existing .agentforge directory")

    @patch.object(Config, 'find_project_root')
    def test_config_without_root_path(self, mock_find_project_root):
        # Instead of letting it do the real search, we'll just ensure it *calls* find_project_root
        # and then we’ll simulate returning the same directory we set up in setUp.
        mock_find_project_root.return_value = self.temp_root_path.resolve()

        config = Config()

        mock_find_project_root.assert_called_once()
        self.assertEqual(config.project_root, self.temp_root_path.resolve())
        self.assertTrue(config.config_path.is_dir())

    @patch.object(Config, 'find_config', return_value=None)
    @patch.object(Config, 'reload', return_value=None)
    def test_load_agent_data_agent_not_found(self, mock_find_config, mock_reload):
        config = Config(root_path=str(self.temp_root_path))  # Valid .agentforge directory

        # We'll raise FileNotFoundError if the agent is not found
        with self.assertRaises(FileNotFoundError):
            config.load_agent_data("MissingAgent")


if __name__ == '__main__':
    unittest.main()
