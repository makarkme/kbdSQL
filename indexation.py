import pickle
import os

from btree import BTree


class Index:
    def __init__(self, field, btree=None):
        if btree is None:
            btree = BTree(3)
        self.field = field
        self.btree = btree


class Indexation:
    def __init__(self, collection):
        self.collection = collection

        self.path_to_indexes = os.path.join(self.collection.path_to_collection, "indexes")
        os.makedirs(self.path_to_indexes, exist_ok=True)

        self.indexes = self.load_indexes()                          # Загружаем с диска проиндексированные поля {key=field; value=value}

        self.query_engine = self.collection.query_engine

    def get_indexes(self):
        return self.indexes

    def load_indexes(self):
        indexes = {}
        for filename in os.listdir(self.path_to_indexes):
            if filename.endswith(".pkl"):
                field = filename[:-len(".pkl")]                     # Убираем ".pkl" в конце имени файла (получаем поле, по которому индексировали)
                path_to_index = os.path.join(self.path_to_indexes, filename)
                with open(path_to_index, "rb") as file:
                    btree = pickle.load(file)
                indexes[field] = Index(field, btree)
        return indexes

    def create_index(self, field: str) -> int:
        index = Index(field)

        count = 0
        for filename, json_document in self.collection.get_jsons():
            values = self.collection.get_value(json_document, field)    # Получаем значение из каждого json-документа по указанному полю
            for value in values:
                index.btree.insert(value, filename)
                count += 1

        path_to_index = os.path.join(self.path_to_indexes, f"{field}.pkl")
        with open(path_to_index, "wb") as file:
            pickle.dump(index.btree, file)

        self.indexes[field] = index                                 # Записываем проиндексированное
        return count

    def indexed_search(self, field: str, query: dict) -> list:      # Поиск производится по индексированным полям
        index = self.indexes[field]                                 # B-дерево, в котором будет вестить поиск
        condition = query.get(field)

        if condition is None:
            return []

        if isinstance(condition, dict):
            operator, value = next(iter(condition.items()))
        else:
            operator, value = "$eq", condition

        filenames = index.btree.search(value)                       # Список подходящих документов по значению
        query_func = self.query_engine.parse_query(query)

        json_documents = []
        for filename in filenames:
            json_document = self.collection.get_json(filename)
            if json_document and query_func(json_document):
                json_documents.append(json_document)
        return json_documents