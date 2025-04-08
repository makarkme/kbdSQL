import os
import uuid
import json
import pickle

from btree import BTree
from query_engine import QueryEngine

class Index:
    def __init__(self, field, btree=BTree(3)):
        self.field = field
        self.btree = btree



class Collection:
    def __init__(self, collection: str, path_to_database: str):
        self.query_engine = QueryEngine(self.get_value)
        self.name_collection = collection

        self.path_to_collection = os.path.join(path_to_database, self.name_collection)
        self.path_to_indexes = os.path.join(self.path_to_collection, "./indexes")
        os.makedirs(self.path_to_collection, exist_ok=True)
        os.makedirs(self.path_to_indexes, exist_ok=True)

        self.indexes = self.load_indexes()                              # Загружаем с диска проиндексированные поля {key=field; value=value}

        self.MAX_DEPTH = 50                                             # Максимальная глубина вложений в json-документе

    def load_indexes(self):
        indexes = {}
        for filename in os.listdir(self.path_to_indexes):
            if filename.endswith(".pkl"):
                field = filename[:-len(".pkl")]                         # Убираем ".pkl" в конце имени файла (получаем поле, по которому индексировали)
                path_to_index = os.path.join(self.path_to_indexes, filename)
                with open(path_to_index, "rb") as file:
                    btree = pickle.load(file)
                indexes[field] = Index(field, btree)
        return indexes

    def create_index(self, field: str) -> int:
        if field in self.indexes:
            return 0

        index = Index(field)
        count = 0
        for doc_id, doc in self.get_docs():
            values = self.wrap_in_list(doc, field)                      # Получаю значение из каждого json-документа по указанному полю
            for value in values:                                        # Если это список значений, а не одно значение
                index.btree.insert(value, doc_id)
                count += 1

        path_to_index = os.path.join(self.path_to_indexes, f"{field}.pkl")
        with open(path_to_index, "wb") as file:
            pickle.dump(index.btree, file)

        self.indexes[field] = index                                     # То, что проиндексировано
        return count

    def get_docs(self) -> list:                                         # Возвращает массив json-документов
        result = []
        for filename in os.listdir(self.path_to_collection):
            if filename.endswith(".json"):
                doc_id = filename[:-len(".json")]                       # Убираем ".json" в конце имени файла
                doc = self.get_doc(doc_id)
                if doc:
                    result.append((doc_id, doc))
        return result

    def get_doc(self, doc_id: str):                                     # Возвращает json-документ
        path_to_doc = os.path.join(self.path_to_collection, f"{doc_id}.json")

        if not os.path.exists(path_to_doc):                                # Если документ не найден
            return None

        with open(path_to_doc, encoding='utf-8') as file:
            return json.load(file)

    def collection_insert(self, doc: dict) -> str:
        doc_id = str(uuid.uuid4())                                      # Генерации уникальных id документов

        path_to_json = os.path.join(self.path_to_collection, f"{doc_id}.json")
        with open(path_to_json, "w", encoding="utf-8") as file:
            json.dump(doc, file, indent=2, ensure_ascii=False)

        # field - поле, по которому мы смотрим; index - значение, которое отправится в b-дерево
        for field, index in self.indexes.items():
            values = self.wrap_in_list(doc, field)                      # Получаю значение из каждого json-документа по указанному полю
            for value in values:                                        # Если это список значений, а не одно значение
                index.btree.insert(value, doc_id)

            path_to_index = os.path.join(self.path_to_indexes, f"{field}.pkl")  # Сохраняем обновлённое дерево на диск
            with open(path_to_index, "wb") as file:
                pickle.dump(index.btree, file)

        return doc_id

    def wrap_in_list(self, doc, field: str) -> list:                    # Оборачиваем значение в массив
        value = self.get_value(doc, field)
        if isinstance(value, list):
            return value
        elif value is not None:
            return [value]
        else:
            return []

    def get_value(self, doc, field: str):                               # Находит вложенное значение
        parts = field.split(".")
        if len(parts) > self.MAX_DEPTH:                                 # Ограничиваем максмальное число вложенностей
            return None

        for part in parts:
            if isinstance(doc, dict):                                   # Спускаемся на уровень ниже
                doc = doc.get(part)
            elif isinstance(doc, list):                                 # Дошли до конца
                try:
                    index = int(part)
                    if index < len(doc):                                # Проверяем, не указан ли неверный индекс
                        doc = doc[index]
                    else:
                        return None
                except ValueError:                                      # Если part не число
                    return None
            else:
                return None
            if doc is None:
                return None
        return doc


    def find_doc(self, query: dict) -> list:
        index_field = None
        for field in query:
            if field in self.indexes:
                index_field = field
                break

        if index_field:
            return self.index_search(index_field, query)
        return self.all_search(query)

    def index_search(self, field: str, query: dict) -> list:            # Поиск производится индексированным полям
        index = self.indexes[field]                                     # B-дерево, в котором будет вестить поиск
        condition = query.get(field)                                    # Условие

        if condition is None:
            return []

        if isinstance(condition, dict) and condition:
            operator, value = next(iter(condition.items()))
        else:
            operator, value = "$eq", condition

        doc_ids = index.btree.search(operator, value)                   # Список подходящих документов
        query_func = self.query_engine.parse_query(query)

        result = []
        for doc_id in doc_ids:
            doc = self.get_doc(doc_id)
            if doc and query_func(doc):
                result.append(doc)

        return result

    def all_search(self, query: dict) -> list:                          # Поиск производится по всем документам
        query_func = self.query_engine.parse_query(query)
        all_docs = self.get_docs()

        result = []
        for _, doc in all_docs:                                         # Список всех документов (распаковываем кортеж)
            if doc and query_func(doc):
                result.append(doc)
        return result