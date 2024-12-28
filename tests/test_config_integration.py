import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch
from agentforge.config import Config


class TestConfigIntegration(unittest.TestCase):
    def setUp(self):
        Config._instance = None

        # Patch print for the entire class
        self.print_patch = patch("builtins.print", lambda *args, **kwargs: None)
        self.print_patch.start()

        # Create a temporary directory to copy the real .agentforge folder into
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_root_path = Path(self.temp_dir.name)

        # Copy the existing .agentforge from setup_files into the temp dir
        current_dir = Path(__file__).resolve().parent # __file__ is the path to the current file
        real_agentforge = current_dir.parent / "src" / "agentforge" / "setup_files" / ".agentforge"
        shutil.copytree(real_agentforge, self.temp_root_path / ".agentforge")

    def tearDown(self):
        # Clean up after each test
        self.temp_dir.cleanup()
        Config._instance = None

    def test_custom_root_path(self):
        config = Config(root_path=str(self.temp_root_path))

        # Assert known configs from real .agentforge is loaded
        self.assertIn("actions", config.data)
        self.assertIn("personas", config.data)
        self.assertIn("prompts", config.data)
        self.assertIn("settings", config.data)
        self.assertIn("tools", config.data)

        # Assert Setting Files are loaded
        self.assertIn("models", config.data["settings"])
        self.assertIn("system", config.data["settings"])

        # Assert settings are set to the correct default value
        self.assertTrue(config.data["settings"]["system"].get("PersonasEnabled"))

        # ... maybe we write a separate test for validating a settings and models file ...

    def test_no_agentforge_raises(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # No .agentforge is created here
            with self.assertRaises(FileNotFoundError):
                Config(root_path=temp_dir)

    def test_empty_agentforge_loads_no_settings(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            (Path(temp_dir) / ".agentforge").mkdir()
            config = Config(root_path=temp_dir)
            self.assertEqual(config.data, {}, "Expected an empty config.data but got something else")


if __name__ == '__main__':
    unittest.main()