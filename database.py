import os
import json
import ast

from collection import Collection
from indexation import  Indexation


class Database:
    def __init__(self, path_to_database, current_collection: str):
        self.path_to_collection = os.path.join(path_to_database, current_collection)
        os.makedirs(self.path_to_collection, exist_ok=True)

        self.collection = Collection(self.path_to_collection)
        self.indexation = Indexation(self.collection)

    def insert(self, string: str):                                  # Пример: python cli_core.py db mydb/users insert "{'name': 'Иван', 'age': 18}"
        try:
            json_document = json.loads(string)
        except json.JSONDecodeError:
            json_document = ast.literal_eval(string)
        return self.collection.insert(json_document)

    def index(self, field: str):                                    # Пример: python cli_core.py db mydb/users index age
        return self.indexation.create_index(field)                  # Возвращает количество проиндексированных значений

    def search_by_condition(self, query: str):                      # Пример: python cli_core.py db mydb/users condition "{'age': {'@eq': 18}}"
        try:
            query_dict = json.loads(query)
        except json.JSONDecodeError:
            query_dict = ast.literal_eval(query)                    # Превращает "{'age': {'`$gt': 18}}" в словарь
        return self.collection.search_by_condition(query_dict)      # Возвращает список "подходящих" json-документов


    # (нужно дописать реализацию)
    # (удаляет документ по id)
    # def delete(self, doc_id: str):
    #     pass

    # (вывожит все коллекции)
    # def list_collections(self):
    #     pass