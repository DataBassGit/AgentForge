# test_base_db.py
import unittest

# We assume BaseDB is in a file named base_db.py in the same directory (or adjust import as needed)
from agentforge.dbs.base_db import BaseDB


class TestBaseDB(unittest.TestCase):
    def setUp(self):
        # BaseDB in its raw form isn't really meant to be instantiated directly,
        # but for the sake of testing default behaviors, we'll do it anyway.
        self.db = BaseDB()

    def test_connect_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.db.connect()

    def test_disconnect_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.db.disconnect()

    def test_select_collection_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.db.select_collection("test_collection")

    def test_create_collection_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.db.create_collection("test_collection")

    def test_delete_collection_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.db.delete_collection("test_collection")

    def test_insert_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.db.insert("test_collection", data={"foo": "bar"})

    def test_query_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.db.query("test_collection", query={"foo": "bar"})

    def test_update_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.db.update("test_collection", query={"foo": "bar"}, new_data={"bar": "baz"})

    def test_delete_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.db.delete("test_collection", query={"foo": "bar"})

    def test_count_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.db.count("test_collection")


if __name__ == "__main__":
    unittest.main()
