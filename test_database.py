import unittest
import os
import json
import shutil
from database import Database
from collection import Collection
from indexation import Indexation


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.test_dir = "./test_databases"
        self.db_name = "testdb"
        self.collection_name = "users"
        self.path_to_db = os.path.join(self.test_dir, self.db_name)

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

        self.db = Database(self.path_to_db, self.collection_name)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_insert_valid_json(self):
        test_document = '{"name": "John", "age": 30}'
        result = self.db.insert(test_document)

        self.assertIsNotNone(result)
        inserted_doc = self.db.collection.get_json(result)
        self.assertEqual(inserted_doc["name"], "John")
        self.assertEqual(inserted_doc["age"], 30)

    def test_index_field(self):
        self.db.insert("{'name': 'John', 'age': 30}")
        self.db.insert("{'name': 'Alice', 'age': 25}")
        self.db.insert("{'name': 'Bob', 'age': 30}")

        count = self.db.index('age')

        self.assertEqual(count, 3)
        index_path = os.path.join(self.path_to_db, self.collection_name, "indexes", "age.pkl")
        self.assertTrue(os.path.exists(index_path))

    def test_search_by_condition(self):
        self.db.insert('{"name": "John", "age": 30}')
        self.db.insert('{"name": "Alice", "age": 25}')
        self.db.insert('{"name": "Bob", "age": 30}')

        query = '{"age": {"@eq": 30}}'
        results = self.db.search_by_condition(query)

        self.assertEqual(len(results), 2)
        names = [doc["name"] for doc in results]
        self.assertIn("John", names)
        self.assertIn("Bob", names)

    def test_search_by_condition_no_results(self):
        self.db.insert('{"name": "John", "age": 30}')

        query = '{"age": {"@eq": 40}}'
        results = self.db.search_by_condition(query)

        self.assertEqual(len(results), 0)

    def test_search_with_index(self):
        self.db.insert('{"name": "John", "age": 30}')
        self.db.insert('{"name": "Alice", "age": 25}')
        self.db.insert('{"name": "Bob", "age": 30}')

        self.db.index("age")

        query = '{"age": {"@eq": 30}}'
        results = self.db.search_by_condition(query)

        self.assertEqual(len(results), 2)
        names = [doc["name"] for doc in results]
        self.assertIn("John", names)
        self.assertIn("Bob", names)


if __name__ == '__main__':
    unittest.main()