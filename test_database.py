import unittest
import tempfile
import shutil
import os
import json
from database import Database


class TestDatabaseIntegration(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.collection_name = 'users'
        self.database = Database(self.tempdir, self.collection_name)

        self.doc1 = {'name': 'Alice', 'age': 30}
        self.doc2 = {'name': 'Bob', 'age': 25}
        self.doc3 = {'name': 'Charlie', 'age': 35}

        self.id1 = self.database.insert(json.dumps(self.doc1))
        self.id2 = self.database.insert(json.dumps(self.doc2))
        self.id3 = self.database.insert(json.dumps(self.doc3))

        self.another_collection_name = 'admins'
        self.admin_db = Database(self.tempdir, self.another_collection_name)

        self.admin_doc1 = {'name': 'AdminAlice', 'role': 'superadmin'}
        self.admin_doc2 = {'name': 'AdminBob', 'role': 'moderator'}

        self.admin_id1 = self.admin_db.insert(json.dumps(self.admin_doc1))
        self.admin_id2 = self.admin_db.insert(json.dumps(self.admin_doc2))

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_insert_and_retrieve(self):
        path_to_file = os.path.join(self.tempdir, self.collection_name, f"{self.id1}.json")
        self.assertTrue(os.path.exists(path_to_file))
        with open(path_to_file, 'r', encoding='utf-8') as f:
            content = json.load(f)
            self.assertEqual(content['name'], 'Alice')
            self.assertEqual(content['age'], 30)

    def test_delete_document(self):
        path_to_file = os.path.join(self.tempdir, self.collection_name, f"{self.id2}.json")
        self.assertTrue(os.path.exists(path_to_file))
        self.database.delete(self.id2)
        self.assertFalse(os.path.exists(path_to_file))

    def test_delete_nonexistent_document(self):
        with self.assertRaises(FileNotFoundError):
            self.database.delete('nonexistent_id')

    def test_index_and_search(self):
        count = self.database.index('age')
        self.assertEqual(count, 3)

        query = json.dumps({'age': {'@eq': 30}})
        results = self.database.search_by_condition(query)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'Alice')

    def test_search_by_condition_no_result(self):
        query = json.dumps({'age': {'@eq': 99}})
        results = self.database.search_by_condition(query)
        self.assertEqual(results, [])

    def test_insert_invalid_json(self):
        with self.assertRaises(Exception):
            self.database.insert('{invalid_json:}')

    def test_insert_valid_python_dict(self):
        string_repr = "{'name': 'David', 'age': 28}"
        inserted_id = self.database.insert(string_repr)
        self.assertIsInstance(inserted_id, str)

    def test_search_invalid_json_query(self):
        with self.assertRaises(Exception):
            self.database.search_by_condition('{invalid_query}')

    def test_search_nested_field(self):
        nested_doc = {'user': {'name': 'Eve', 'age': 22}}
        nested_id = self.database.insert(json.dumps(nested_doc))

        query = json.dumps({'user.name': {'@eq': 'Eve'}})
        results = self.database.search_by_condition(query)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['user']['name'], 'Eve')


    def test_multiple_collections(self):
        # Проверка данных в users
        query_users = json.dumps({'age': {'@gte': 25}})
        users_results = self.database.search_by_condition(query_users)
        self.assertGreaterEqual(len(users_results), 2)

        # Проверка данных в admins
        query_admins = json.dumps({'role': {'@eq': 'superadmin'}})
        admins_results = self.admin_db.search_by_condition(query_admins)
        self.assertEqual(len(admins_results), 1)
        self.assertEqual(admins_results[0]['name'], 'AdminAlice')

    def test_index_multiple_collections(self):
        self.database.index('age')
        self.admin_db.index('role')

        query_users = json.dumps({'age': {'@eq': 30}})
        users_results = self.database.search_by_condition(query_users)
        self.assertEqual(len(users_results), 1)

        query_admins = json.dumps({'role': {'@eq': 'moderator'}})
        admins_results = self.admin_db.search_by_condition(query_admins)
        self.assertEqual(len(admins_results), 1)

    def test_delete_all_documents_and_search(self):
        self.database.delete(self.id1)
        self.database.delete(self.id2)
        self.database.delete(self.id3)

        query_users = json.dumps({'age': {'@gte': 0}})
        users_results = self.database.search_by_condition(query_users)
        self.assertEqual(len(users_results), 0)

    def test_switch_collections_and_insert(self):
        new_collection = Database(self.tempdir, 'guests')
        guest_doc = {'name': 'Guest1', 'visit': '2024-05-01'}
        guest_id = new_collection.insert(json.dumps(guest_doc))

        query = json.dumps({'name': {'@eq': 'Guest1'}})
        guests_results = new_collection.search_by_condition(query)
        self.assertEqual(len(guests_results), 1)
        self.assertEqual(guests_results[0]['name'], 'Guest1')


if __name__ == '__main__':
    unittest.main()
