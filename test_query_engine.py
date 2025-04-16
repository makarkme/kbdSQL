import unittest
from collection import Collection
from query_engine import QueryEngine
import os
import shutil


class TestQueryEngine(unittest.TestCase):
    def setUp(self):
        self.test_dir = "./test_query_engine"
        os.makedirs(self.test_dir, exist_ok=True)
        self.collection = Collection(self.test_dir)
        self.query_engine = QueryEngine(self.collection)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_parse_query_eq(self):
        query = {"age": {"@eq": 25}}
        condition = self.query_engine.parse_query(query)
        doc = {"age": 25}
        self.assertTrue(condition(doc))
        doc = {"age": 30}
        self.assertFalse(condition(doc))

    def test_parse_query_or(self):
        query = {"@or": [{"age": {"@eq": 25}}, {"name": {"@eq": "Alice"}}]}
        condition = self.query_engine.parse_query(query)
        doc1 = {"age": 25, "name": "Bob"}
        doc2 = {"age": 30, "name": "Alice"}
        doc3 = {"age": 30, "name": "Bob"}
        self.assertTrue(condition(doc1))
        self.assertTrue(condition(doc2))
        self.assertFalse(condition(doc3))

    def test_parse_query_regex(self):
        query = {"name": {"@regex": "Al.*"}}
        condition = self.query_engine.parse_query(query)
        doc = {"name": "Alice"}
        self.assertTrue(condition(doc))
        doc = {"name": "Bob"}
        self.assertFalse(condition(doc))

    def test_parse_query_length(self):
        query = {"tags": {"@length": 3}}
        condition = self.query_engine.parse_query(query)
        doc = {"tags": ["a", "b", "c"]}
        self.assertTrue(condition(doc)) # надо либо фиксить collection.get_value, либо убирать его из функции length_condition()
        doc = {"tags": ["a", "b"]}
        self.assertFalse(condition(doc))

    def test_parse_query_date(self):
        query = {"date": {"@year": 2023}}
        condition = self.query_engine.parse_query(query)
        doc = {"date": "2023-05-15T00:00:00"}
        self.assertTrue(condition(doc))
        doc = {"date": "2022-05-15T00:00:00"}
        self.assertFalse(condition(doc))


if __name__ == "__main__":
    unittest.main()