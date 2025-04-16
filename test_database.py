import unittest
import os
import json
import shutil
from database import Database
from collection import Collection
from indexation import Indexation


class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = "./test_databases"
        self.db_name = "testdb"
        self.collection_name = "users"
        self.path_to_db = os.path.join(self.test_dir, self.db_name)

        # Ensure clean state
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

        # Initialize database
        self.db = Database(self.path_to_db, self.collection_name)

    def tearDown(self):
        # Clean up test directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_insert_valid_json(self):
        test_document = '{"name": "John", "age": 30}'
        result = self.db.insert(test_document)

        # Verify the document was inserted
        self.assertIsNotNone(result)
        inserted_doc = self.db.collection.get_json(result)
        self.assertEqual(inserted_doc["name"], "John")
        self.assertEqual(inserted_doc["age"], 30)

    def test_index_field(self):
        # Insert some test documents
        self.db.insert('{"name": "John", "age": 30}')
        self.db.insert('{"name": "Alice", "age": 25}')
        self.db.insert('{"name": "Bob", "age": 30}')

        # Create index on age
        count = self.db.index("age")

        # Verify index was created
        self.assertEqual(count, 3)  # Should index 3 documents
        index_path = os.path.join(self.path_to_db, "indexes", "age.pkl")
        self.assertTrue(os.path.exists(index_path)) # че то надо делать я хз че

    def test_search_by_condition(self):
        # Insert test documents
        self.db.insert('{"name": "John", "age": 30}')
        self.db.insert('{"name": "Alice", "age": 25}')
        self.db.insert('{"name": "Bob", "age": 30}')

        # Test search with equality condition
        query = '{"age": {"@eq": 30}}'
        results = self.db.search_by_condition(query)

        # Verify results
        self.assertEqual(len(results), 2)
        names = [doc["name"] for doc in results]
        self.assertIn("John", names)
        self.assertIn("Bob", names)

    def test_search_by_condition_no_results(self):
        # Insert test documents
        self.db.insert('{"name": "John", "age": 30}')

        # Test search with non-matching condition
        query = '{"age": {"@eq": 40}}'
        results = self.db.search_by_condition(query)

        # Verify no results
        self.assertEqual(len(results), 0)

    def test_search_with_index(self):
        # Insert test documents
        self.db.insert('{"name": "John", "age": 30}')
        self.db.insert('{"name": "Alice", "age": 25}')
        self.db.insert('{"name": "Bob", "age": 30}')

        # Create index
        self.db.index("age")

        # Test search using indexed field
        query = '{"age": {"@eq": 30}}'
        results = self.db.search_by_condition(query)

        # Verify results
        self.assertEqual(len(results), 2)
        names = [doc["name"] for doc in results]
        self.assertIn("John", names)
        self.assertIn("Bob", names)


if __name__ == '__main__':
    unittest.main()