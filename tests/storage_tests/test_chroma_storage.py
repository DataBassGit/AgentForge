# test_chroma_storage.py

from agentforge.storage.chroma_storage import ChromaStorage

import unittest
from tests.base_test_case import BaseTestCase

class TestBaseStorage(BaseTestCase):

    # ---------------------------------
    # Prep.
    # ---------------------------------

    def setUp(self):
        super().setUp()
        self.storage = ChromaStorage()

    def tearDown(self):
        super().tearDown()
        # Clear ONLY IF the chroma client exists otherwise no need to do anything
        if self.storage.client:
            self.storage.reset_storage()
            self.storage.disconnect()

        self.storage = None

    # ---------------------------------
    # Tests
    # ---------------------------------

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
        data_to_insert = ["Hello"]
        self.storage.insert("test_collection", ids=["1"], data=data_to_insert)

        # Query them back
        results = self.storage.query(collection_name="test_collection", ids=["1"])
        self.assertTrue(len(results['documents']) == 1)
        self.assertEqual(results['documents'][0], "Hello")

    def test_update_and_query(self):
        """
        Insert, then update a record, then check if we get the updated field back.
        """
        self.storage.connect()
        self.storage.create_collection("test_collection")

        # Insert documents
        self.storage.insert("test_collection", ids=["1"], data=['Foo'])
        self.storage.update("test_collection", ids=["1"], new_data=['Bar'])

        results = self.storage.query(collection_name="test_collection", ids=["1"])
        self.assertTrue(len(results['documents']) == 1)
        self.assertEqual(results['documents'][0], "Bar")

    def test_delete_and_count(self):
        """
        Insert some records, delete some of them, and count how many remain.
        """
        self.storage.connect()
        self.storage.create_collection("test_collection")

        # Insert documents
        self.storage.insert("test_collection", ids=["1", "2", "3"], data=['Foo', 'Bar', 'Bacon'])
        self.storage.delete("test_collection", ids=["2"])

        # count should be 2
        count_after_delete = self.storage.count("test_collection")
        self.assertEqual(count_after_delete, 2)

    def test_reset_storage(self):
        """
        After inserting data, reset_storage should nuke it all.
        """
        self.storage.connect()
        self.storage.create_collection("test_collection")
        self.storage.insert("test_collection", ids=["1", "2"], data=['Foo', 'Bar'])

        count_before_reset = self.storage.count("test_collection")
        self.assertEqual(count_before_reset, 2)

        self.storage.reset_storage()

        # reset_storage deletes the entire DB, so test_collection will not exist
        # We'll test the simplest case: everything is gone.
        self.assertRaises(Exception, self.storage.count, "test_collection")


if __name__ == "__main__":
    unittest.main()
