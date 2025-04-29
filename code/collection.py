import os
import uuid
import json
import jsonpath_ng
import jsonpath_ng.exceptions

from code.query_engine import QueryEngine
from code.indexation import Indexation


class Collection:
    def __init__(self, path_to_collection: str):
        self.path_to_collection = path_to_collection

        self.path_to_indexes = os.path.join(self.path_to_collection, "./indexes")
        os.makedirs(self.path_to_indexes,
                    exist_ok=True)  # Создаст path_to_indexes если его нет, либо проигнорирует, есть пусть уже создан

        self.query_engine = QueryEngine(self)
        self.indexation = Indexation(self)

    def insert(self, json_document: dict) -> str:
        # Вставка json-объекта в выбранную базу данных.
        # Пример 1: python cli_core.py db mydb/users insert "{'name': 'Иван', 'age': 18}"
        # Пример 2: python cli_core.py --storage-path "E:\PyCharmProjects\kbdSQL\storage" db mydb/users insert "{'name': 'Иван', 'age': 18}"

        filename = str(uuid.uuid4())  # Генерация уникального id документа

        path_to_json_document = os.path.join(self.path_to_collection, f"{filename}.json")
        with open(path_to_json_document, "w", encoding="utf-8") as file:
            json.dump(json_document, file, indent=2, ensure_ascii=False)
        return filename

    def delete(self, filename: str) -> str:
        # Удаление json-объекта из выбранной базы данных.
        # Пример 1: python cli_core.py db mydb/users delete "{'name': 'Иван', 'age': 18}"
        # Пример 2: python cli_core.py --storage-path "E:\PyCharmProjects\kbdSQL\storage" db mydb/users delete "{'name': 'Иван', 'age': 18}"

        path_to_json_document = os.path.join(self.path_to_collection, f"{filename}.json")
        if not os.path.exists(path_to_json_document):
            raise FileNotFoundError
        self.indexation.remove_from_index(filename)
        os.remove(path_to_json_document)
        return path_to_json_document

    def search_by_condition(self, query: dict) -> list:
        # Поиск json-документов по заданному условию в выбранной базе данных.
        # Пример 1: python cli_core.py db mydb/users condition "{'age': {'@eq': 18}}"
        # Пример 2: python cli_core.py --storage-path "E:\PyCharmProjects\kbdSQL\storage" db mydb/users condition "{'age': {'@eq': 18}}"

        indexes = self.indexation.get_indexes()
        indexed_fields = []  # проиндексированные поля, которые содержатся в запросе
        for field in query:
            if field in indexes:
                indexed_fields.append(field)

        query_func = self.query_engine.parse_query(query)

        all_eq = True
        for field in indexed_fields:
            condition = query[field]
            if isinstance(condition, dict):
                operator, _ = next(iter(condition.items()))
                if operator != "@eq":
                    all_eq = False
                    break

        if all_eq:
            matched_ids_sets = []
            for field in indexed_fields:
                matched_ids = self.indexation.indexed_search(field, query)
                matched_ids_sets.append(set(matched_ids))
            if matched_ids_sets:
                filenames = set.intersection(*matched_ids_sets)
            else:
                filenames = set(filename for filename, _ in self.get_jsons())
        else:
            # Иначе — перебираем все файлы
            filenames = set(filename for filename, _ in self.get_jsons())

        json_documents = []  # Список всех, подходящих под условие, json-документов
        for filename in filenames:
            json_document = self.get_json(filename)
            if json_document and query_func(json_document):
                json_documents.append(json_document)
        return json_documents


    def get_jsons(self):    # Возвращает массив всех json-документов в коллекции

        for file in os.listdir(self.path_to_collection):
            if file.endswith(".json"):
                filename = file[:-len(".json")]    # Убираем ".json" в конце имени файла
                json_document = self.get_json(filename)
                if json_document:
                    yield (filename, json_document)

    def get_json(self, filename: str):  # Возвращает json-документ
        path_to_json_document = os.path.join(self.path_to_collection, f"{filename}.json")
        if not os.path.exists(path_to_json_document):
            return None
        with open(path_to_json_document, encoding="utf-8") as file:
            return json.load(file)

    def get_value(self, json_document, field: str) -> list:
        # По заданному полю возвращает его значение

        try:
            matches = jsonpath_ng.parse(field).find(json_document)
            values = [match.value for match in matches]
            flattened = []
            for value in values:
                if isinstance(value, list):
                    flattened.extend(value)
                else:
                    flattened.append(value)
            return flattened
        except jsonpath_ng.exceptions.JsonPathParserError as error:  # Некорректный синтаксис пути
            return []
        except (AttributeError, KeyError, TypeError, IndexError) as error:
            return []
