# base_test_case.py

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch
from agentforge.config import Config

# ---------------------------------
# Prep.
# ---------------------------------

class BaseTestCaseNoAgentForgeFolder(unittest.TestCase):

    # ---------------------------------
    # Prep.
    # ---------------------------------

    def setUp(self):
        Config._instance = None
        self._patch_print()
        self._create_temp_directory()

    def tearDown(self):
        Config._instance = None
        self.temp_dir.cleanup()

    # ---------------------------------
    # Internal Methods
    # ---------------------------------

    def _patch_print(self):
        # Supress Print Statements
        self.print_patch = patch("builtins.print", lambda *args, **kwargs: None)
        self.print_patch.start()

    def _create_temp_directory(self):
        # Create a temporary directory to copy the real .agentforge folder into
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_root_path = Path(self.temp_dir.name)


class BaseTestCaseEmptyAgentForgeFolder(BaseTestCaseNoAgentForgeFolder):

    # ---------------------------------
    # Prep.
    # ---------------------------------

    def setUp(self):
        super().setUp()
        self._create_agentforge_folder()

    # ---------------------------------
    # Internal Methods
    # ---------------------------------

    def _create_agentforge_folder(self):
        # Create an empty .agentforge folder
        (self.temp_root_path / ".agentforge").mkdir(exist_ok=True)


class BaseTestCase(BaseTestCaseNoAgentForgeFolder):

    # ---------------------------------
    # Prep.
    # ---------------------------------

    def setUp(self):
        super().setUp()
        self._copy_agentforge_files()
        self._reset_config()

    def tearDown(self):
        super().setUp()
        self.config = None

    # ---------------------------------
    # Internal Methods
    # ---------------------------------

    def _copy_agentforge_files(self):
        # Copy the existing .agentforge from setup_files into the temp dir
        # If some classes need an empty .agentforge, override or skip this
        root_dir = Path(__file__).resolve().parent
        real_agentforge = root_dir.parent / "src" / "agentforge" / "setup_files" / ".agentforge"
        shutil.copytree(real_agentforge, self.temp_root_path / ".agentforge")

    def _reset_config(self):
        # Reset the Config singleton with the desired temp root path
        self.config = Config.reset(root_path=str(self.temp_root_path))

if __name__ == '__main__':
    unittest.main()


