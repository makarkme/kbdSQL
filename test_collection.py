import unittest
import os
import json
import shutil
from collection import Collection
from query_engine import QueryEngine
from indexation import Indexation


class TestCollection(unittest.TestCase):
    def setUp(self):
        self.test_dir = "./test_collection"
        os.makedirs(self.test_dir, exist_ok=True)
        self.collection = Collection(self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_insert(self):
        document = {"name": "Alice", "age": 25}
        doc_id = self.collection.insert(document)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, f"{doc_id}.json")))
        with open(os.path.join(self.test_dir, f"{doc_id}.json"), "r", encoding="utf-8") as f:
            saved_doc = json.load(f)
        self.assertEqual(saved_doc, document)

    def test_get_json(self):
        document = {"name": "Bob", "age": 30}
        doc_id = self.collection.insert(document)
        retrieved_doc = self.collection.get_json(doc_id)
        self.assertEqual(retrieved_doc, document)
        self.assertIsNone(self.collection.get_json("nonexistent"))

    def test_get_jsons(self):
        doc1 = {"name": "Alice", "age": 25}
        doc2 = {"name": "Bob", "age": 30}
        id1 = self.collection.insert(doc1)
        id2 = self.collection.insert(doc2)
        jsons = self.collection.get_jsons()
        self.assertEqual(len(jsons), 2)
        self.assertIn((id1, doc1), jsons)
        self.assertIn((id2, doc2), jsons)

    def test_get_value(self):
        document = {"user": {"name": "Alice", "age": 25}}
        doc_id = self.collection.insert(document)
        values = self.collection.get_value(document, "user.name")
        self.assertEqual(values, ["Alice"])
        values = self.collection.get_value(document, "user.age")
        self.assertEqual(values, [25])
        values = self.collection.get_value(document, "invalid.path")
        self.assertEqual(values, [])

    def test_search_by_condition(self):
        doc1 = {"name": "Alice", "age": 25}
        doc2 = {"name": "Bob", "age": 30}
        self.collection.insert(doc1)
        self.collection.insert(doc2)
        query = {"age": {"@eq": 25}}
        results = self.collection.search_by_condition(query)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], doc1)


if __name__ == "__main__":
    unittest.main()