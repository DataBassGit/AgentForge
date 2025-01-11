# test_chroma_storage.py

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch
from agentforge.config import Config
from agentforge.storage.chroma_storage import ChromaStorage


class TestChromaStorage(unittest.TestCase):
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
        self.storage = ChromaStorage()

    def tearDown(self):
        """
        Make sure we reset and disconnect after each test, so no data carries over.
        """
        # We assume the class implements reset_storage and disconnect
        self.storage.reset_storage()
        self.storage.disconnect()

    def test_connect_disconnect(self):
        """
        Verifies we can connect to Chroma and then disconnect without errors.
        """
        self.storage.connect()
        # Maybe we can check some internal state or call a method that verifies a connection.
        # But for now, we might just see if it doesn't raise any exceptions.

        self.storage.disconnect()
        # Same idea: if there's no exception, that might suffice for an initial test.
        # But you can check state changes if needed.

    def test_create_and_delete_collection(self):
        """
        Basic test to confirm that we can create a collection (table) and delete it.
        """
        self.storage.connect()
        self.storage.create_collection("test_collection")
        # Potentially check that the collection actually exists by some method
        self.storage.delete_collection("test_collection")
        # Check that it actually got removed or handle exceptions as needed.

    def test_insert_and_query(self):
        """
        Test that we can insert documents into a collection and retrieve them with a query.
        """
        self.storage.connect()
        self.storage.create_collection("test_collection")

        # Insert one or more documents
        data_to_insert = [
            {"id": "1", "content": "Hello"},
            {"id": "2", "content": "World"},
        ]
        self.storage.insert("test_collection", data_to_insert)

        # Query them back
        results = self.storage.query("test_collection", query={"id": "2"})
        self.assertTrue(len(results) == 1)
        self.assertEqual(results[0].get("content"), "World")

    def test_update_and_query(self):
        """
        Insert, then update a record, then check if we get the updated field back.
        """
        self.storage.connect()
        self.storage.create_collection("test_collection")

        self.storage.insert("test_collection", [{"id": "1", "content": "Foo"}])
        self.storage.update("test_collection", query={"id": "1"}, new_data={"content": "Bar"})

        results = self.storage.query("test_collection", query={"id": "1"})
        self.assertEqual(results[0].get("content"), "Bar")

    def test_delete_and_count(self):
        """
        Insert some records, delete some of them, and count how many remain.
        """
        self.storage.connect()
        self.storage.create_collection("test_collection")

        self.storage.insert("test_collection", [{"id": "1"}, {"id": "2"}, {"id": "3"}])
        self.storage.delete("test_collection", {"id": "2"})

        # count should be 2
        count_after_delete = self.storage.count("test_collection")
        self.assertEqual(count_after_delete, 2)

    def test_reset_storage(self):
        """
        After inserting data, reset_storage should nuke it all.
        """
        self.storage.connect()
        self.storage.create_collection("test_collection")
        self.storage.insert("test_collection", [{"id": "1"}, {"id": "2"}])

        count_before_reset = self.storage.count("test_collection")
        self.assertEqual(count_before_reset, 2)

        self.storage.reset_storage()

        # Optionally, if reset_storage deletes the entire DB,
        # then test_collection might not exist, or it’s empty if it’s re-created automatically.
        # We'll assume the simplest case: everything is gone.
        self.assertRaises(Exception, self.storage.count, "test_collection")

        # or if you prefer "reset" to simply empty out the data rather than drop everything:
        # count_after_reset = self.storage.count("test_collection")
        # self.assertEqual(count_after_reset, 0)


if __name__ == "__main__":
    unittest.main()
