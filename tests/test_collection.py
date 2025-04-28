import unittest
import tempfile
import shutil
import os
from code.collection import Collection


class TestCollectionIntegration(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.collection = Collection(self.tempdir)

        self.doc1 = {'name': 'Alice', 'age': 30}
        self.doc2 = {'name': 'Bob', 'age': 25}
        self.doc3 = {'name': 'Charlie', 'details': {'city': 'Moscow', 'zip': '101000'}}

        self.id1 = self.collection.insert(self.doc1)
        self.id2 = self.collection.insert(self.doc2)
        self.id3 = self.collection.insert(self.doc3)

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_insert_and_get_json(self):
        json_doc = self.collection.get_json(self.id1)
        self.assertEqual(json_doc['name'], 'Alice')
        self.assertEqual(json_doc['age'], 30)

    def test_delete_document(self):
        path = self.collection.delete(self.id1)
        self.assertFalse(os.path.exists(path))
        self.assertIsNone(self.collection.get_json(self.id1))

    def test_delete_nonexistent_document(self):
        with self.assertRaises(FileNotFoundError):
            self.collection.delete('nonexistent_id')

    def test_get_all_jsons(self):
        jsons = self.collection.get_jsons()
        ids = [id_ for id_, _ in jsons]
        self.assertIn(self.id1, ids)
        self.assertIn(self.id2, ids)
        self.assertIn(self.id3, ids)

    def test_search_by_condition_direct(self):
        query = {'name': {'@eq': 'Bob'}}
        results = self.collection.search_by_condition(query)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'Bob')

    def test_search_by_condition_nested(self):
        query = {'details.city': {'@eq': 'Moscow'}}
        results = self.collection.search_by_condition(query)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['details']['city'], 'Moscow')

    def test_get_value_existing_field(self):
        json_doc = self.collection.get_json(self.id3)
        values = self.collection.get_value(json_doc, 'details.city')
        self.assertIn('Moscow', values)

    def test_get_value_nonexistent_field(self):
        json_doc = self.collection.get_json(self.id3)
        values = self.collection.get_value(json_doc, 'nonexistent.field')
        self.assertEqual(values, [])

    def test_get_value_invalid_jsonpath(self):
        json_doc = self.collection.get_json(self.id3)
        values = self.collection.get_value(json_doc, 'details.city[')
        self.assertEqual(values, [])

    def test_search_with_empty_query(self):
        query = {}
        results = self.collection.search_by_condition(query)
        self.assertEqual(len(results), 3)

    def test_search_after_deletion(self):
        self.collection.delete(self.id2)
        query = {'name': {'@eq': 'Bob'}}
        results = self.collection.search_by_condition(query)
        self.assertEqual(len(results), 0)


if __name__ == '__main__':
    unittest.main()
