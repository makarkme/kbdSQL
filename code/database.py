import os
import json
import ast

from collection import Collection


class Database:
    def __init__(self, path_to_database, current_collection: str):
        self.path_to_collection = os.path.join(path_to_database, current_collection)
        os.makedirs(self.path_to_collection,
                    exist_ok=True)  # Создаст path_to_collection если его нет, либо проигнорирует, есть пусть уже создан

        self.collection = Collection(self.path_to_collection)
        self.indexation = self.collection.indexation

    def insert(self, string: str) -> str:
        # Вставка json-объекта в выбранную базу данных.
        # Пример 1: python cli_core.py db mydb/users insert "{'name': 'Иван', 'age': 18}"
        # Пример 2: python cli_core.py --storage-path "E:\PyCharmProjects\kbdSQL\storage" db mydb/users insert "{'name': 'Иван', 'age': 18}"
        try:
            json_document = json.loads(string)
        except json.JSONDecodeError:
            json_document = ast.literal_eval(string)  # type(json_document): dict

        try:
            return self.collection.insert(json_document)  # Возвращает id json-документа
        except Exception as error:
            raise error

    def delete(self, filename: str) -> str:
        # Удаление json-файла из выбранной базы данных.
        # Пример 1: python cli_core.py db mydb/users delete "531b4cdd-bc58-4aa9-aca5-5d1b7c44715f"
        # Пример 2: python cli_core.py --storage-path "E:\PyCharmProjects\kbdSQL\storage" db mydb/users delete "531b4cdd-bc58-4aa9-aca5-5d1b7c44715f"

        try:
            return self.collection.delete(filename)
        except Exception as error:
            raise error

    def index(self, field: str) -> int:
        # Индексация выбранного поля по всем json-объектам в выбранной базе данных.
        # Пример 1: python cli_core.py db mydb/users index age
        # Пример 2: python cli_core.py --storage-path "E:\PyCharmProjects\kbdSQL\storage" db mydb/users index age
        try:
            return self.indexation.create_index(field)  # Возвращает количество проиндексированных значений
        except Exception as error:
            raise error

    def search_by_condition(self, query: str) -> list:
        # Поиск json-документов по заданному условию в выбранной базе данных.
        # Пример 1: python cli_core.py db mydb/users condition "{'age': {'@eq': 18}}"
        # Пример 2: python cli_core.py --storage-path "E:\PyCharmProjects\kbdSQL\storage" db mydb/users condition "{'age': {'@eq': 18}}"

        try:
            query_dict = json.loads(query)
        except json.JSONDecodeError:
            query_dict = ast.literal_eval(query)  # type(query_dict): dict

        try:
            return self.collection.search_by_condition(query_dict)  # Возвращает список "подходящих" json-документов
        except Exception as error:
            raise error

    def get_filenames(self) -> list:
        # Вывод списка всех json-документов в заданной коллекции.
        # Пример 1: python cli_core.py list_jsons
        # Пример 2: python cli_core.py --storage-path "E:\PyCharmProjects\kbdSQL\storage" list_jsons
        return self.collection.get_jsons()
