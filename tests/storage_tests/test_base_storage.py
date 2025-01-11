# test_base_storage.py

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch
from agentforge.config import Config

# We assume BaseDB is in a file named base_storage.py in the same directory (or adjust import as needed)
from agentforge.storage.base_storage import BaseStorage


class TestBaseStorage(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to copy the real .agentforge folder into
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_root_path = Path(self.temp_dir.name)

        # Copy the existing .agentforge from setup_files into the temp dir
        root_dir = Path(__file__).resolve().parent.parent  # __file__ is the path to the current file
        real_agentforge = root_dir.parent / "src" / "agentforge" / "setup_files" / ".agentforge"
        shutil.copytree(real_agentforge, self.temp_root_path / ".agentforge")

        # Reset the Config singleton with the desired root path
        Config.reset(root_path=str(self.temp_root_path))

        # Now BaseStorage will use the re-initialized Config instance
        self.storage = BaseStorage()


    def test_connect_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.storage.connect()

    def test_disconnect_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.storage.disconnect()

    def test_select_collection_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.storage.select_collection("test_collection")

    def test_create_collection_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.storage.create_collection("test_collection")

    def test_delete_collection_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.storage.delete_collection("test_collection")

    def test_insert_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.storage.insert("test_collection", data={"foo": "bar"})

    def test_query_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.storage.query("test_collection", query={"foo": "bar"})

    def test_update_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.storage.update("test_collection", query={"foo": "bar"}, new_data={"bar": "baz"})

    def test_delete_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.storage.delete("test_collection", query={"foo": "bar"})

    def test_count_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.storage.count("test_collection")

    def test_reset_storage_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.storage.reset_storage()


if __name__ == "__main__":
    unittest.main()
