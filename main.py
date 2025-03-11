import os
import json
import uuid
from datetime import datetime
from btree import *
from indexation import *

class Collection:
    def __init__(self, name, db_path):
        self.name = name
        self.path = os.path.join(db_path, name)
        os.makedirs(self.path, exist_ok=True)
        self.indexes = {}

    def insert(self, document):
        doc_id = str(uuid.uuid4())
        document['_id'] = doc_id
        file_path = os.path.join(self.path, f"{doc_id}.json")
        with open(file_path, 'w') as f:
            json.dump(document, f)
        for field, index in self.indexes.items():
            value = self._get_nested_field(document, field)
            if value is not None:
                index.btree.insert(value, doc_id)
        return doc_id

    def create_index(self, field):
        if field in self.indexes:
            return
        index = Index(field)
        for doc_id, doc in self._get_all_docs_with_ids():
            value = self._get_nested_field(doc, field)
            if value is not None:
                index.btree.insert(value, doc_id)
        self.indexes[field] = index

    def find(self, query):
        index_field = next((f for f in query if f in self.indexes), None)
        if index_field:
            return self._find_with_index(index_field, query)
        return self._find_with_scan(query)

    def _find_with_index(self, field, query):
        index = self.indexes[field]
        condition = query[field]
        
        if isinstance(condition, dict):
            op, value = next(iter(condition.items()))
        else:
            op, value = "$eq", condition

        doc_ids = index.btree.search(op, value)
        query_func = self._parse_query(query)
        return [doc for doc_id in doc_ids if (doc := self.get(doc_id)) and query_func(doc)]

    def _find_with_scan(self, query):
        query_func = self._parse_query(query)
        return [doc for doc in self._get_all_docs() if query_func(doc)]

    def get(self, doc_id):
        path = os.path.join(self.path, f"{doc_id}.json")
        if not os.path.exists(path):
            return None
        with open(path) as f:
            return json.load(f)

    def _get_nested_field(self, doc, field):
        parts = field.split('.')
        for part in parts:
            if isinstance(doc, dict):
                doc = doc.get(part)
            elif isinstance(doc, list) and part.isdigit():
                doc = doc[int(part)] if int(part) < len(doc) else None
            else:
                return None
        return doc

    def _parse_query(self, query):
        conditions = []
        
        # Обработка логических операторов верхнего уровня
        if "$or" in query:
            or_conditions = [self._parse_query(c) for c in query["$or"]]
            return lambda doc: any(cond(doc) for cond in or_conditions)
        if "$and" in query:
            and_conditions = [self._parse_query(c) for c in query["$and"]]
            return lambda doc: all(cond(doc) for cond in and_conditions)
        if "$not" in query:
            not_condition = self._parse_query(query["$not"])
            return lambda doc: not not_condition(doc)

        # Обработка обычных условий
        for field, condition in query.items():
            if isinstance(condition, dict):
                for op, val in condition.items():
                    # Обработка функций
                    if op.startswith("$"):
                        if op == "$regex":
                            conditions.append(self._create_regex_condition(field, val))
                        elif op == "$length":
                            conditions.append(self._create_length_condition(field, val))
                        elif op == "$lower":
                            conditions.append(self._create_lower_condition(field, val))
                        elif op == "$upper":
                            conditions.append(self._create_upper_condition(field, val))
                        else:
                            conditions.append(self._create_condition(field, op, val))
                    else:
                        conditions.append(self._create_condition(field, op, val))
            else:
                # Прямой поиск в массивах
                if isinstance(condition, (str, int, float, bool)):
                    conditions.append(self._create_array_contains_condition(field, condition))
                else:
                    conditions.append(self._create_condition(field, "$eq", condition))
        
        return lambda doc: all(cond(doc) for cond in conditions)

    def _create_condition(self, field, op, value):
        def check(doc):
            doc_val = self._get_nested_field(doc, field)
            if doc_val is None:
                return False
            
            # Handle array values
            if isinstance(doc_val, list):
                if op == "$eq":
                    return value in doc_val
                elif op == "$ne":
                    return value not in doc_val
                return any(self._compare_items(item, op, value) for item in doc_val)
            
            return self._compare_items(doc_val, op, value)
        
        return check

    def _get_all_docs(self):
        return (self.get(f[:-5]) for f in os.listdir(self.path) if f.endswith('.json'))

    def _get_all_docs_with_ids(self):
        return ((f[:-5], self.get(f[:-5])) for f in os.listdir(self.path) if f.endswith('.json'))
    
    def _compare_items(self, doc_val, op, value):
        # String functions
        if isinstance(doc_val, str):
            if op == "$lower":
                return doc_val.lower() == value.lower()
            if op == "$upper":
                return doc_val.upper() == value.upper()
            if op == "$contains":
                return value.lower() in doc_val.lower()
            if op == "$startsWith":
                return doc_val.lower().startswith(value.lower())
            if op == "$endsWith":
                return doc_val.lower().endswith(value.lower())
        
        # Number functions
        if isinstance(doc_val, (int, float)):
            if op == "$abs":
                return abs(doc_val) == value
            if op == "$round":
                return round(doc_val) == value
        
        # Date functions
        if isinstance(doc_val, str):  # Assuming ISO date strings
            try:
                doc_date = datetime.fromisoformat(doc_val)
                if op == "$year":
                    return doc_date.year == value
                if op == "$month":
                    return doc_date.month == value
                if op == "$day":
                    return doc_date.day == value
            except ValueError:
                pass
        
        # Standard comparisons
        try:
            if op == "$eq": return doc_val == value
            if op == "$ne": return doc_val != value
            if op == "$gt": return doc_val > value
            if op == "$lt": return doc_val < value
            if op == "$gte": return doc_val >= value
            if op == "$lte": return doc_val <= value
        except TypeError:
            return False
        return False
    
    def _create_array_contains_condition(self, field, value):
        def check(doc):
            doc_val = self._get_nested_field(doc, field)
            if isinstance(doc_val, list):
                return value in doc_val
            return doc_val == value
        return check
    
    def _create_regex_condition(self, field, pattern):
        import re
        regex = re.compile(pattern)
        def check(doc):
            doc_val = self._get_nested_field(doc, field)
            return bool(regex.search(str(doc_val))) if doc_val else False
        return check
    
    def _create_length_condition(self, field, length):
        def check(doc):
            doc_val = self._get_nested_field(doc, field)
            if isinstance(doc_val, (list, str)):
                return len(doc_val) == length
            return False
        return check
    
    def _create_lower_condition(self, field, value):
        def check(doc):
            doc_val = self._get_nested_field(doc, field)
            return str(doc_val).lower() == value.lower() if doc_val else False
        return check

    def _create_upper_condition(self, field, value):
        def check(doc):
            doc_val = self._get_nested_field(doc, field)
            return str(doc_val).upper() == value.upper() if doc_val else False
        return check

class Database:
    def __init__(self, name, storage_path='./data'):
        self.path = os.path.join(storage_path, name)
        os.makedirs(self.path, exist_ok=True)
        self.collections = {}

    def get_collection(self, name):
        if name not in self.collections:
            self.collections[name] = Collection(name, self.path)
        return self.collections[name]

if __name__ == "__main__":
    db = Database("test_db")
    users = db.get_collection("users")
    
    # Очищаем коллекцию
    for f in os.listdir(users.path):
        os.remove(os.path.join(users.path, f))
    
    # Новые тестовые данные
    users.insert({
        "name": "Alice",
        "age": 25,
        "email": "Alice@Example.com",
        "tags": ["admin", "user"],
        "bio": "Python developer"
    })
    
    users.insert({
        "name": "Bob",
        "age": 35,
        "email": "BOB@WORK.COM",
        "tags": ["manager"],
        "bio": "Team Lead"
    })
    
    users.insert({
        "name": "Charlie",
        "age": 28,
        "email": "charlie@test.org",
        "tags": ["user", "tester"],
        "bio": "QA Engineer"
    })
    
    users.insert({
        "name": "David",
        "age": 40,
        "email": "DAVID@example.com",
        "tags": ["admin", "manager"],
        "bio": "Senior Developer"
    })
    
    print("1. Базовый выбор всех документов:")
    for user in users.find({}):
        print(f"{user['name']} ({user['age']} лет)")
    
    print("\n2. Фильтр по точному совпадению (email):")
    results = users.find({"email": "charlie@test.org"})
    for user in results:
        print(user)
    
    print("\n3. Операторы сравнения для чисел:")
    print("Пользователи старше 30:")
    for user in users.find({"age": {"$gt": 30}}):
        print(f"{user['name']} ({user['age']})")
    
    print("\nПользователи младше или равные 35:")
    for user in users.find({"age": {"$lte": 35}}):
        print(f"{user['name']} ({user['age']})")
    
    print("\n4. Логические операторы (AND):")
    results = users.find({
        "bio": "Senior Developer",
        "age": {"$gte": 28}
    })
    print("Активные пользователи старше 28 лет:")
    for user in results:
        print(f"{user['name']} (Возраст: {user['age']}, Био: {user['bio']})")
    
    print("\n5. Работа с массивами (тегами):")
    print("Пользователи с тегом 'admin':")
    for user in users.find({"tags": "admin"}):
        print(f"- {user['name']} ({user['tags']})")
    
    print("\n6. Комбинированные условия с $or:")
    results = users.find({
        "$or": [
            {"age": {"$gte": 30}},
            {"email": {"$lower": "david@example.com"}}
        ]
    })
    for user in results:
        print(f"- {user['name']} (Age: {user['age']}, Email: {user['email']})")
    
    print("\n7. Строковые функции:")
    print("Поиск по email без учета регистра:")
    for user in users.find({"email": {"$lower": "alice@example.com"}}):
        print(f"- {user['name']} ({user['email']})")
    
    print("\nПоиск по регулярному выражению:")
    for user in users.find({"bio": {"$regex": r"Developer$"}}):
        print(f"- {user['name']} ({user['bio']})")
    
    print("\nПоиск по длине строки:")
    for user in users.find({"bio": {"$length": 11}}):
        print(f"- {user['name']} ({len(user['bio'])} chars: {user['bio']})")