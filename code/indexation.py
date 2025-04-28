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

        self.indexes = self._load_indexes()  # Загружаем с диска проиндексированные поля {key=field; value=value}

        self.query_engine = self.collection.query_engine

    def get_indexes(self) -> dict:
        return self.indexes

    def _load_indexes(self) -> dict:
        # Загружаем ранее проиндексированные поля

        indexes = {}
        for filename in os.listdir(self.path_to_indexes):
            if filename.endswith(".pkl"):
                field = filename[
                        :-len(".pkl")]  # Убираем ".pkl" в конце имени файла (получаем поле, по которому индексировали)
                path_to_index = os.path.join(self.path_to_indexes, filename)
                with open(path_to_index, "rb") as file:
                    btree = pickle.load(file)
                indexes[field] = Index(field, btree)
        return indexes

    def create_index(self, field: str) -> int:
        # Индексация выбранного поля по всем json-объектам в выбранной базе данных.
        # Пример 1: python cli_core.py db mydb/users index age
        # Пример 2: python cli_core.py --storage-path "E:\PyCharmProjects\kbdSQL\storage" db mydb/users index age

        index = Index(field)

        count = 0
        for filename, json_document in self.collection.get_jsons():
            # Получаем значение из каждого json-документа по указанному полю
            values = self.collection.get_value(json_document, field)
            for value in values:
                try:
                    key = int(value)
                except (ValueError, TypeError):
                    key = str(value)
                index.btree.insert(key, filename)
                count += 1

        path_to_index = os.path.join(self.path_to_indexes, f"{field}.pkl")
        with open(path_to_index, "wb") as file:
            pickle.dump(index.btree, file)

        self.indexes[field] = index  # Записываем проиндексированное
        return count

    def remove_from_index(self, filename: str):
        for field, index in self.indexes.items():
            index.btree.remove_value(filename)

            # Пересохраняем индекс на диск
            path_to_index = os.path.join(self.path_to_indexes, f"{field}.pkl")
            with open(path_to_index, "wb") as file:
                pickle.dump(index.btree, file)

    def indexed_search(self, field: str, query: dict) -> list:
        # Поиск по индексированным полям

        index = self.indexes[field]  # B-дерево, в котором будет вестить поиск
        condition = query.get(field)

        if condition is None:
            return []
        if isinstance(condition, dict):
            operator, value = next(iter(condition.items()))  # Берёт первую пару (ключ; значение) из словаря
        else:
            operator, value = "@eq", condition
        return index.btree.search(value)  # Список подходящих документов по значению
