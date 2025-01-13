# test_base_storage.py

import unittest
from agentforge.storage.base_storage import BaseStorage
from tests.base_test_case import BaseTestCase

class TestBaseStorage(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.storage = BaseStorage()

    def tearDown(self):
        super().tearDown()
        self.storage = None

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

    def test_set_current_collection_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.storage.create_collection("test_collection")

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
