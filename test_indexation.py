import unittest
import os
import json
import shutil
from collection import Collection
from indexation import Indexation
from btree import BTree


class TestIndexation(unittest.TestCase):
    def setUp(self):
        self.test_dir = "./test_indexation"
        os.makedirs(self.test_dir, exist_ok=True)
        self.collection = Collection(self.test_dir)
        self.indexation = Indexation(self.collection)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_create_index(self):
        doc1 = {"name": "Alice", "age": 25}
        doc2 = {"name": "Bob", "age": 30}
        id1 = self.collection.insert(doc1)
        id2 = self.collection.insert(doc2)
        count = self.indexation.create_index("age")
        self.assertEqual(count, 2)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "indexes", "age.pkl")))
        self.assertIn("age", self.indexation.indexes)

    def test_load_indexes(self):
        doc1 = {"name": "Alice", "age": 25}
        self.collection.insert(doc1)
        self.indexation.create_index("age")
        new_indexation = Indexation(self.collection)
        self.assertIn("age", new_indexation.indexes)
        index = new_indexation.indexes["age"]
        self.assertIsInstance(index.btree, BTree)

    def test_indexed_search(self):
        doc1 = {"name": "Alice", "age": 25}
        doc2 = {"name": "Bob", "age": 30}
        self.collection.insert(doc1)
        self.collection.insert(doc2)
        self.indexation.create_index("age")
        query = {"age": {"@eq": 25}}
        results = self.indexation.indexed_search("age", query)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], doc1)
        query = {"age": {"@eq": 999}}
        results = self.indexation.indexed_search("age", query) # index.btree.search(value) должна всегда возвращать список, а у нас btree.search может вернуть None
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()