import os
import uuid
import json
import jsonpath_ng
import jsonpath_ng.exceptions

from query_engine import QueryEngine
from indexation import Indexation


class Collection:
    def __init__(self, path_to_collection: str):
        self.MAX_DEPTH = 50                                         # Максимальная глубина вложений в json-документе


        self.path_to_collection = path_to_collection

        self.path_to_indexes = os.path.join(self.path_to_collection, "indexes")
        os.makedirs(self.path_to_indexes, exist_ok=True)

        self.query_engine = QueryEngine(self)
        self.indexation = Indexation(self)

    def insert(self, json_document: dict) -> str:
        filename = str(uuid.uuid4())                                # Генерация уникального id документа

        path_to_json_document = os.path.join(self.path_to_collection, f"{filename}.json")
        with open(path_to_json_document, "w", encoding="utf-8") as file:
            json.dump(json_document, file, indent=2, ensure_ascii=False)

        return filename

    def search_by_condition(self, query: dict) -> list:
        indexes = self.indexation.get_indexes()

        search_field = None
        for field in query:
            if field in indexes:
                search_field = field
                break

        if search_field:
            return self.indexation.indexed_search(search_field, query)
        return self._complete_search(query)

    def _complete_search(self, query: dict) -> list:                # Поиск производится по всем документам
        condition = self.query_engine.parse_query(query)

        json_documents = []
        for filename, json_document in self.get_jsons():            # Список всех документов (распаковываем кортеж)
            if json_document and condition(json_document):
                json_documents.append(json_document)
        return json_documents

    def get_jsons(self) -> list:                                    # Возвращает массив json-документов
        json_documents = []
        for file in os.listdir(self.path_to_collection):
            if file.endswith(".json"):
                filename = file[:-len(".json")]                     # Убираем ".json" в конце имени файла
                json_document = self.get_json(filename)
                if json_document:
                    json_documents.append((filename, json_document))
        return json_documents

    def get_json(self, filename: str):                              # Возвращает json-документ
        path_to_json_document = os.path.join(self.path_to_collection, f"{filename}.json")
        if not os.path.exists(path_to_json_document):
            return None
        with open(path_to_json_document, encoding="utf-8") as file:
            return json.load(file)

    def get_value(self, json_document, field: str) -> list:         # Находит вложенное значение
        if field.count(".") > self.MAX_DEPTH:                       # Ограничиваем максмальное число вложенностей
            return []

        try:
            matches = jsonpath_ng.parse(field).find(json_document)
            return [match.value for match in matches]
        except jsonpath_ng.exceptions.JsonPathParserError:          # Некорректный синтаксис пути
            return []
        except (AttributeError, KeyError, TypeError, IndexError):
            return []
