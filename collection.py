import os
import uuid
import json
from datetime import datetime
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
            values = self._get_index_values(document, field)
            for value in values:
                index.btree.insert(value, doc_id)
        return doc_id

    def create_index(self, field):
        if field in self.indexes:
            return
        index = Index(field)
        for doc_id, doc in self._get_all_docs_with_ids():
            values = self._get_index_values(doc, field)
            for value in values:
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
            if isinstance(doc_val, str):
                return doc_val.lower() == value.lower()
            return False
        return check

    def _create_upper_condition(self, field, value):
        def check(doc):
            doc_val = self._get_nested_field(doc, field)
            if isinstance(doc_val, str):
                return doc_val.upper() == value.upper()
            return False
        return check
    
    def _get_index_values(self, doc, field):
        value = self._get_nested_field(doc, field)
        if isinstance(value, list):
            return value
        return [value] if value is not None else []
