import unittest
import tempfile
import shutil
from collection import Collection
from query_engine import QueryEngine


class TestQueryEngineIntegration(unittest.TestCase):
    def setUp(self):
        # Создаем временную директорию и инициализируем Collection и QueryEngine
        self.tempdir = tempfile.mkdtemp()
        self.collection = Collection(self.tempdir)
        self.query_engine = QueryEngine(self.collection)

    def tearDown(self):
        # Удаляем временную директорию после тестов
        shutil.rmtree(self.tempdir)

    def test_eq_ne_numeric(self):
        pred_eq = self.query_engine.parse_query({'age': {'@eq': 30}})
        self.assertTrue(pred_eq({'age': 30}))
        self.assertFalse(pred_eq({'age': 31}))

        pred_ne = self.query_engine.parse_query({'age': {'@ne': 30}})
        self.assertTrue(pred_ne({'age': 31}))
        self.assertFalse(pred_ne({'age': 30}))

    def test_gt_lt_gte_lte(self):
        doc = {'val': 10}
        self.assertTrue(self.query_engine.parse_query({'val': {'@gt': 5}})(doc))
        self.assertFalse(self.query_engine.parse_query({'val': {'@gt': 10}})(doc))
        self.assertTrue(self.query_engine.parse_query({'val': {'@lt': 15}})(doc))
        self.assertFalse(self.query_engine.parse_query({'val': {'@lt': 10}})(doc))
        self.assertTrue(self.query_engine.parse_query({'val': {'@gte': 10}})(doc))
        self.assertFalse(self.query_engine.parse_query({'val': {'@gte': 11}})(doc))
        self.assertTrue(self.query_engine.parse_query({'val': {'@lte': 10}})(doc))
        self.assertFalse(self.query_engine.parse_query({'val': {'@lte': 9}})(doc))

    def test_regex(self):
        doc = {'name': 'Ivan123'}
        self.assertTrue(self.query_engine.parse_query({'name': {'@regex': r'^[A-Za-z]+\d+$'}})(doc))
        self.assertFalse(self.query_engine.parse_query({'name': {'@regex': r'^123'}})(doc))

    def test_length(self):
        self.assertTrue(self.query_engine.parse_query({'code': {'@length': 5}})({'code': 'abcde'}))
        self.assertFalse(self.query_engine.parse_query({'code': {'@length': 4}})({'code': 'abcde'}))

        self.assertTrue(self.query_engine.parse_query({'lst': {'@length': 3}})({'lst': [1, 2, 3]}))

        self.assertTrue(self.query_engine.parse_query({'num': {'@length': 2}})({'num': 42}))

        self.assertTrue(self.query_engine.parse_query({'multi': {'@length': 2}})({'multi': ['a', 'b']}))
        self.assertFalse(self.query_engine.parse_query({'multi': {'@length': 3}})({'multi': ['a', 'b']}))

    def test_and_or_not(self):
        doc = {'a': 1, 'b': 2, 'c': 3}

        query_and = {'@and': [{'a': {'@gt': 0}}, {'b': {'@lt': 3}}]}
        self.assertTrue(self.query_engine.parse_query(query_and)(doc))
        self.assertFalse(self.query_engine.parse_query(query_and)({'a': 0, 'b': 2}))

        query_or = {'@or': [{'a': {'@eq': 0}}, {'c': {'@eq': 3}}]}
        self.assertTrue(self.query_engine.parse_query(query_or)(doc))
        self.assertFalse(self.query_engine.parse_query(query_or)({'a': 1, 'c': 0}))

        query_not = {'@not': {'b': {'@eq': 2}}}
        self.assertFalse(self.query_engine.parse_query(query_not)(doc))
        self.assertTrue(self.query_engine.parse_query(query_not)({'a': 1, 'b': 3}))

    def test_list_variable(self):
        self.assertTrue(self.query_engine.parse_query({'x': 5})({'x': 5}))
        self.assertFalse(self.query_engine.parse_query({'x': 5})({'x': 6}))

        self.assertTrue(self.query_engine.parse_query({'x': 5})({'x': [1, 5, 9]}))
        self.assertFalse(self.query_engine.parse_query({'x': 2})({'x': [1, 5, 9]}))

    def test_nested_json_fields_and_complex_conditions(self):
        # Сложный вложенный JSON
        doc = {
            'user': {
                'name': 'Ivan',
                'address': {'city': 'Moscow', 'zip': '101000'},
                'age': 25,
                'roles': ['admin', 'user']
            },
            'active': True
        }
        # Проверяем вложенное равенство
        self.assertTrue(self.query_engine.parse_query({'user.name': {'@eq': 'Ivan'}})(doc))
        self.assertTrue(self.query_engine.parse_query({'user.address.city': {'@eq': 'Moscow'}})(doc))
        self.assertFalse(self.query_engine.parse_query({'user.address.zip': {'@eq': '999999'}})(doc))

        # Несколько условий одновременно (AND)
        # Несколько условий одновременно (AND)
        query = {
            '@and': [
                {'user.age': {'@gte': 18}},
                {'active': {'@eq': True}}
            ]
        }
        self.assertTrue(self.query_engine.parse_query(query)(doc))

        # Условие OR внутри AND
        complex_query = {
            '@and': [
                query,
                {'user.age': {'@lt': 30}}
            ]
        }
        self.assertTrue(self.query_engine.parse_query(complex_query)(doc))

        # Сложное сочетание И/ИЛИ
        combo_query = {
            '@or': [
                {'user.age': {'@lt': 30}},
                {'@and': [
                    {'active': {'@eq': True}}
                ]}
            ]
        }
        self.assertTrue(self.query_engine.parse_query(combo_query)(doc))
        self.assertTrue(
            self.query_engine.parse_query(combo_query)({'user': {'age': 35, 'roles': ['user']}, 'active': True}))

    def test_invalid_queries_and_robustness(self):
        # Неизвестный оператор
        pred = self.query_engine.parse_query({'age': {'@unknown': 30}})
        self.assertFalse(pred({'age': 30}))

        # Неверный тип: @and должен быть списком
        with self.assertRaises(TypeError):
            self.query_engine.parse_query({'@and': 123})({'age': 30})

        # Несуществующее поле
        pred = self.query_engine.parse_query({'nonexistent': {'@eq': 1}})
        self.assertFalse(pred({'age': 1}))

        # Невалидный regex
        pred = self.query_engine.parse_query({'name': {'@regex': '['}})
        self.assertFalse(pred({'name': 'Ivan'}))

        # Попытка сравнения строки и числа
        pred = self.query_engine.parse_query({'age': {'@gt': 'abc'}})
        self.assertFalse(pred({'age': 25}))


        # Пустой документ
        pred = self.query_engine.parse_query({'age': {'@eq': 30}})
        self.assertFalse(pred({}))

        # Отсутствие условия у поля — должно обрабатываться как @eq
        pred = self.query_engine.parse_query({'name': 'Ivan'})
        self.assertTrue(pred({'name': 'Ivan'}))
        self.assertFalse(pred({'name': 'Petr'}))

        # Значение None в документе
        pred = self.query_engine.parse_query({'name': {'@eq': 'Ivan'}})
        self.assertFalse(pred({'name': None}))


if __name__ == '__main__':
    unittest.main()
