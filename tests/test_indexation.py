import unittest
import tempfile
import shutil
import os
import pickle
from code.collection import Collection
from code.indexation import Indexation, Index
from code.btree import BTree


class TestIndexationIntegration(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.collection = Collection(self.tempdir)
        self.indexation = Indexation(self.collection)

        self.doc1 = {'name': 'Alice', 'age': 30}
        self.doc2 = {'name': 'Bob', 'age': 25}
        self.doc3 = {'name': 'Charlie', 'age': 30}
        self.doc4 = {'name': 'David', 'age': 40}

        self.id1 = self.collection.insert(self.doc1)
        self.id2 = self.collection.insert(self.doc2)
        self.id3 = self.collection.insert(self.doc3)
        self.id4 = self.collection.insert(self.doc4)

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_create_index(self):
        count = self.indexation.create_index('age')
        self.assertEqual(count, 4)

        index_file = os.path.join(self.indexation.path_to_indexes, 'age.pkl')
        self.assertTrue(os.path.exists(index_file))

        with open(index_file, 'rb') as f:
            btree = pickle.load(f)
            self.assertIsInstance(btree, BTree)

    def test_indexed_search(self):
        self.indexation.create_index('age')
        query = {'age': {'@eq': 30}}
        result = self.indexation.indexed_search('age', query)

        self.assertIn(self.id1, result)
        self.assertIn(self.id3, result)
        self.assertNotIn(self.id2, result)
        self.assertNotIn(self.id4, result)

    def test_remove_from_index(self):
        self.indexation.create_index('age')
        self.indexation.remove_from_index(self.id1)

        query = {'age': {'@eq': 30}}
        result = self.indexation.indexed_search('age', query)

        self.assertNotIn(self.id1, result)
        self.assertIn(self.id3, result)

    def test_load_indexes(self):
        self.indexation.create_index('age')
        new_indexation = Indexation(self.collection)
        self.assertIn('age', new_indexation.indexes)
        self.assertIsInstance(new_indexation.indexes['age'], Index)
        self.assertIsInstance(new_indexation.indexes['age'].btree, BTree)

    def test_search_nonexistent_field(self):
        self.indexation.create_index('age')
        with self.assertRaises(KeyError):
            self.indexation.indexed_search('nonexistent', {'nonexistent': {'@eq': 42}})

    def test_remove_nonexistent_file(self):
        self.indexation.create_index('age')
        fake_id = 'nonexistent_id'
        try:
            self.indexation.remove_from_index(fake_id)
        except Exception as e:
            self.fail(f"remove_from_index raised an exception unexpectedly: {e}")

    def test_multiple_indexes_creation(self):
        self.indexation.create_index('age')
        self.indexation.create_index('name')
        self.assertIn('age', self.indexation.indexes)
        self.assertIn('name', self.indexation.indexes)

    def test_index_search_by_string(self):
        self.indexation.create_index('name')
        query = {'name': {'@eq': 'Alice'}}
        result = self.indexation.indexed_search('name', query)
        self.assertIn(self.id1, result)
        self.assertNotIn(self.id2, result)

    def test_index_search_empty_collection(self):
        empty_tempdir = tempfile.mkdtemp()
        empty_collection = Collection(empty_tempdir)
        empty_indexation = Indexation(empty_collection)
        count = empty_indexation.create_index('nonexistent')
        self.assertEqual(count, 0)
        shutil.rmtree(empty_tempdir)


if __name__ == '__main__':
    unittest.main()
