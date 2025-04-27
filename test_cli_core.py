import unittest
import tempfile
import shutil
import os
import json
from cli_core import Storage, DB

class TestCLIIntegration(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.storage = Storage()
        self.db_name = "testdb"
        self.collection_name = "users"
        self.storage.create_database(self.db_name, self.tempdir)
        self.db = DB(self.db_name, self.tempdir, self.collection_name)

        self.path_to_collection = os.path.join(self.tempdir, self.db_name, self.collection_name)

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_create_and_list_database(self):
        self.assertTrue(os.path.exists(os.path.join(self.tempdir, self.db_name)))

    def test_insert_and_eq(self):
        self.db.insert("{'name': 'Alice', 'age': 30}")
        result = self.db.database.search_by_condition("{'name': {'@eq': 'Alice'}}")
        self.assertEqual(len(result), 1)

    def test_insert_and_ne(self):
        self.db.insert("{'name': 'Bob', 'age': 25}")
        result = self.db.database.search_by_condition("{'age': {'@ne': 30}}")
        self.assertEqual(len(result), 1)

    def test_insert_and_gt(self):
        self.db.insert("{'age': 40}")
        result = self.db.database.search_by_condition("{'age': {'@gt': 30}}")
        self.assertEqual(len(result), 1)

    def test_insert_and_lt(self):
        self.db.insert("{'age': 20}")
        result = self.db.database.search_by_condition("{'age': {'@lt': 30}}")
        self.assertEqual(len(result), 1)

    def test_insert_and_gte(self):
        self.db.insert("{'age': 30}")
        result = self.db.database.search_by_condition("{'age': {'@gte': 30}}")
        self.assertEqual(len(result), 1)

    def test_insert_and_lte(self):
        self.db.insert("{'age': 25}")
        result = self.db.database.search_by_condition("{'age': {'@lte': 30}}")
        self.assertEqual(len(result), 1)

    def test_insert_and_abs(self):
        self.db.insert("{'value': -5}")
        result = self.db.database.search_by_condition("{'value': {'@abs': 5}}")
        self.assertEqual(len(result), 1)

    def test_insert_and_round(self):
        self.db.insert("{'value': 3.6}")
        result = self.db.database.search_by_condition("{'value': {'@round': 4}}")
        self.assertEqual(len(result), 1)

    def test_insert_and_regex(self):
        self.db.insert("{'email': 'user@example.com'}")
        result = self.db.database.search_by_condition(r"{'email': {'@regex': '.*@example\\.com'}}")
        self.assertEqual(len(result), 1)

    def test_insert_and_length(self):
        self.db.insert("{'username': 'admin'}")
        result = self.db.database.search_by_condition("{'username': {'@length': 5}}")
        self.assertEqual(len(result), 1)

    def test_insert_and_year(self):
        self.db.insert("{'created_at': '2024-04-26T12:00:00'}")
        result = self.db.database.search_by_condition("{'created_at': {'@year': 2024}}")
        self.assertEqual(len(result), 1)

    def test_insert_and_month(self):
        self.db.insert("{'created_at': '2024-04-26T12:00:00'}")
        result = self.db.database.search_by_condition("{'created_at': {'@month': 4}}")
        self.assertEqual(len(result), 1)

    def test_insert_and_day(self):
        self.db.insert("{'created_at': '2024-04-26T12:00:00'}")
        result = self.db.database.search_by_condition("{'created_at': {'@day': 26}}")
        self.assertEqual(len(result), 1)

    def test_search_with_or(self):
        self.db.insert("{'role': 'admin'}")
        self.db.insert("{'role': 'user'}")
        result = self.db.database.search_by_condition("{'@or': [{'role': {'@eq': 'admin'}}, {'role': {'@eq': 'user'}}]}")
        self.assertEqual(len(result), 2)

    def test_search_with_and(self):
        self.db.insert("{'role': 'admin', 'active': True}")
        result = self.db.database.search_by_condition("{'@and': [{'role': {'@eq': 'admin'}}, {'active': {'@eq': True}}]}")
        self.assertEqual(len(result), 1)

    def test_search_with_not(self):
        self.db.insert("{'blocked': False}")
        result = self.db.database.search_by_condition("{'@not': {'blocked': {'@eq': True}}}")
        self.assertEqual(len(result), 1)

    def test_search_empty_query(self):
        self.db.insert("{'name': 'Alice'}")
        self.db.insert("{'name': 'Bob'}")
        result = self.db.database.search_by_condition("{}")
        self.assertEqual(len(result), 2)

    def test_delete_document(self):
        self.db.insert("{'name': 'Charlie'}")
        filename = os.listdir(self.path_to_collection)[0][:-5]
        self.db.delete(filename)
        json_files = [f for f in os.listdir(self.path_to_collection) if f.endswith('.json')]
        self.assertEqual(len(json_files), 0)

    def test_index_field(self):
        self.db.insert("{'name': 'David'}")
        count = self.db.index('name')
        self.assertEqual(count, 1)



if __name__ == "__main__":
    unittest.main()
