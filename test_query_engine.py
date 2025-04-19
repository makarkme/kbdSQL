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

    def test_parse_query_or(self):
        query = {"@or": [{"age": {"@eq": 25}}, {"name": {"@eq": "Alice"}}]}
        condition = self.query_engine.parse_query(query)
        doc = {"age": 25, "name": "Bob"}
        self.assertTrue(condition(doc))
        doc = {"age": 30, "name": "Alice"}
        self.assertTrue(condition(doc))
        doc = {"age": 30, "name": "Bob"}
        self.assertFalse(condition(doc))

    def test_parse_query_and(self):
        query = {"@or": [{"age": {"@eq": 25}}, {"name": {"@eq": "Alice"}}]}
        condition = self.query_engine.parse_query(query)
        doc = {"age": 25, "name": "Bob"}
        self.assertTrue(condition(doc))
        doc = {"age": 30, "name": "Alice"}
        self.assertTrue(condition(doc))
        doc = {"age": 30, "name": "Bob"}
        self.assertFalse(condition(doc))

    def test_parte_query_not(self):
        query = {"@not": {"age": {"@gt": 18}}}
        condition = self.query_engine.parse_query(query)
        doc = {"age": 20}
        self.assertFalse(condition(doc))
        doc = {"age": 15}
        self.assertTrue(condition(doc))

    def test_parse_query_regex(self):
        query = {"name": {"@regex": "Al.*"}}
        condition = self.query_engine.parse_query(query)
        doc = {"name": "Alice"}
        self.assertTrue(condition(doc))
        doc = {"name": "Al"}
        self.assertTrue(condition(doc))
        doc = {"name": "Bob"}
        self.assertFalse(condition(doc))
        query = {"@or": [{"email": {"@regex": ".+@gmail.com"}},{"email": {"@regex": ".+@mail.ru"}}]}
        condition = self.query_engine.parse_query(query)
        doc = {"email": "makarkme@gmail.com"}
        self.assertTrue(condition(doc))
        doc = {"email": "savik89@mail.ru"}
        self.assertTrue(condition(doc))
        doc = {"email": "lehamail.ru"}
        self.assertFalse(condition(doc))

    def test_parse_query_length(self):
        query = {"tags": {"@length": 3}}
        condition = self.query_engine.parse_query(query)
        doc = {"tags": ["a", "b", "5"]}
        self.assertTrue(condition(doc))
        doc = {"tags": ["a", "b"]}
        self.assertFalse(condition(doc))

    def test_parse_query_lower(self):
        query = {"tags": {"@upper": "hello"}}
        condition = self.query_engine.parse_query(query)
        doc = {"tags": "HELLO"}
        self.assertTrue(condition(doc))
        doc = {"tags": "hELLo"}
        self.assertTrue(condition(doc))
        doc = {"tags": "helll"}
        self.assertFalse(condition(doc))

    def test_parse_query_upper(self):
        query = {"tags": {"@upper": "HELLO"}}
        condition = self.query_engine.parse_query(query)
        doc = {"tags": "hello"}
        self.assertTrue(condition(doc))
        doc = {"tags": "HEllo"}
        self.assertTrue(condition(doc))
        doc = {"tags": "helll"}
        self.assertFalse(condition(doc))
        query = {"age": {"@upper": 15}}
        condition = self.query_engine.parse_query(query)
        doc = {"age": 15}
        self.assertTrue(condition(doc))
        doc = {"age": 20}
        self.assertFalse(condition(doc))

    def test_parse_query_contains(self):
        query = {"text": {"@contains": "world"}}
        condition = self.query_engine.parse_query(query)
        doc = {"text": "hello world"}
        self.assertTrue(condition(doc))
        doc = {"text": "worl"}
        self.assertFalse(condition(doc))
        doc = {"text": "worldd"}
        self.assertTrue(condition(doc))

    def test_parse_query_startswith(self):
        query = {"text": {"@startswith": "world"}}
        condition = self.query_engine.parse_query(query)
        doc = {"text": "world123"}
        self.assertTrue(condition(doc))
        doc = {"text": "worl"}
        self.assertFalse(condition(doc))
        doc = {"text": "aWorld"}
        self.assertFalse(condition(doc))
        query = {"person": [{"age": {"15"}}, {"name": {"Makar"}}]}
        query = {"name"}

    def test_parse_query_endswith(self):
        query = {"text": {"@endswith": "world"}}
        condition = self.query_engine.parse_query(query)
        doc = {"text": "hello world"}
        self.assertTrue(condition(doc))
        doc = {"text": "W orld"}
        self.assertFalse(condition(doc))
        doc = {"text": "aWorld"}
        self.assertTrue(condition(doc))

    def test_parse_query_eq(self):
        query = {"age": {"@eq": 25}}
        condition = self.query_engine.parse_query(query)
        doc = {"age": 25}
        self.assertTrue(condition(doc))
        doc = {"age": 30}
        self.assertFalse(condition(doc))

    def test_parse_query_ne(self):
        query = {"age": {"@ne": 30}}
        condition = self.query_engine.parse_query(query)
        doc = {"age": 25}
        self.assertTrue(condition(doc))
        doc = {"age": 30}
        self.assertFalse(condition(doc))

    def test_parse_query_gt(self):
        query = {"age": {"@gt": 30}}
        condition = self.query_engine.parse_query(query)
        doc = {"age": 35}
        self.assertTrue(condition(doc))
        doc = {"age": 30}
        self.assertFalse(condition(doc))

    def test_parse_query_lt(self):
        query = {"age": {"@lt": 30}}
        condition = self.query_engine.parse_query(query)
        doc = {"age": 25}
        self.assertTrue(condition(doc))
        doc = {"age": 30}
        self.assertFalse(condition(doc))

    def test_parse_query_gte(self):
        query = {"age": {"@gte": 30}}
        condition = self.query_engine.parse_query(query)
        doc = {"age": 30}
        self.assertTrue(condition(doc))
        doc = {"age": 35}
        self.assertTrue(condition(doc))
        doc = {"age": 29}
        self.assertFalse(condition(doc))

    def test_parse_query_lte(self):
        query = {"age": {"@lte": 30}}
        condition = self.query_engine.parse_query(query)
        doc = {"age": 30}
        self.assertTrue(condition(doc))
        doc = {"age": 25}
        self.assertTrue(condition(doc))
        doc = {"age": 31}
        self.assertFalse(condition(doc))

    def test_parse_query_abs(self):
        query = {"temperature": {"@abs": 15}}
        condition = self.query_engine.parse_query(query)
        doc = {"temperature": 15}
        self.assertTrue(condition(doc))
        doc = {"temperature": -15}
        self.assertTrue(condition(doc))
        doc = {"temperature": 0}
        self.assertFalse(condition(doc))

    def test_parse_query_round(self):
        query = {"age": {"@round": 26}}
        condition = self.query_engine.parse_query(query)
        doc = {"age": 26.2}
        self.assertTrue(condition(doc))
        doc = {"age": 26.5}
        self.assertTrue(condition(doc)) # round округляет до ближайшего чётного числа
        doc = {"age": 27}
        self.assertFalse(condition(doc))

    def test_parse_query_date(self):
        query = {"date": {"@year": 2025}}
        condition = self.query_engine.parse_query(query)
        doc = {"date": "2025-05-15T00:00:00"}
        self.assertTrue(condition(doc))
        doc = {"date": "2024-05-15T00:00:00"}
        self.assertFalse(condition(doc))
        doc = {"date": 2025}
        self.assertFalse(condition(doc))
        doc = {"date": "2025"}
        self.assertFalse(condition(doc))

    def test_parse_query_types(self):
        doc = {
            "user": {
                "id": 123,
                "name": "Ivan",
                "roles": ("admin", "editor"),
                "tags": {"python", "backend", "dev"},
                "profile": {
                    "age": 30,
                    "email": "ivan@example.com",
                    "signup_date": "2025-03-08T12:12:12"
                }
            },
            "settings": {
                "theme": "dark",
                "notifications": {
                    "email": True,
                    "sms": False
                },
                "language": "ru"
            },
            "stats": {
                "logins": 42,
                "avg_session_time": 15.75,
                "devices": [
                    {"type": "laptop", "os": "Linux"},
                    {"type": "phone", "os": "Android"}
                ]
            }
        }
        query = {"user.profile.age": {"@gte": 25}}
        condition = self.query_engine.parse_query(query)
        self.assertTrue(condition(doc))
        query = {"user.id": {"@eq": 123}}
        condition = self.query_engine.parse_query(query)
        self.assertTrue(condition(doc))
        query = {"user.roles": {"@eq": ("admin", "editor")}}
        condition = self.query_engine.parse_query(query)
        self.assertTrue(condition(doc))
        query = {"user.roles": {"@contains": ("admin", "editor")}}
        condition = self.query_engine.parse_query(query)
        self.assertTrue(condition(doc))
        query = {"settings.notifications.email": True}
        condition = self.query_engine.parse_query(query)
        self.assertTrue(condition(doc))
        query = {"stats.avg_session_time": {"@gt": 10}}
        condition = self.query_engine.parse_query(query)
        self.assertTrue(condition(doc))
        query = {"user.tags": {"@startswith": {"python", "backend", "dev"}}}
        condition = self.query_engine.parse_query(query)
        self.assertTrue(condition(doc))
        query = {"user.tags": {"@startswith": {"python", "backend", "dev"}}}
        condition = self.query_engine.parse_query(query)
        self.assertTrue(condition(doc))
        query = {"stats.devices": {"@upper": {"@contains": "LINUX"}}}
        condition = self.query_engine.parse_query(query)
        self.assertTrue(condition(doc))

if __name__ == "__main__":
    unittest.main()