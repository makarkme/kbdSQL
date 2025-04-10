# CLI - это интерфейс командной строки, способ взаимодействия с программой с помощью ввода текста в терминале.
# Чтоб не писать реализацию cli руками, можно использовать удобную альтернативу - typer

import typer
import os
import shutil
import json

from database import Database

# Зачем MainCLI? - Впоследствии расширение функционала для работы с разными бд - пересохранение/копирование/переименование и тд.
class Storage:
    def __init__(self):
        pass

    def list_databases(self, path_to_storage: str = "./databases"):             # Пример: python cli_core.py list или python cli_core.py --storage-path "E:\PyCharmProjects\kbdSQL\storage" list

        if not os.path.exists(path_to_storage):                                 # Проверка, если путь не существует
            typer.echo(f"[ERROR]: Directory '{path_to_storage}' not found.")
            raise typer.Exit()

        databases = os.listdir(path_to_storage)
        if not databases:
            typer.echo(f"[WARNING]: Databases not found in '{path_to_storage}'.")
        else:
            typer.echo(f"[DATABASES IN]: '{path_to_storage}'")
            for database in databases:
                typer.echo(f" -- {database}")

    def create_database(self, database_name: str, path_to_storage: str = "./databases"):    # Пример: python cli_core.py create mydb или python cli_core.py --storage-path "E:\PyCharmProjects\kbdSQL\storage" create mydb
        path_to_database = os.path.join(path_to_storage, database_name)
        if not os.path.exists(path_to_database):                                # Проверка, если путь не существует
            os.makedirs(path_to_database)                                       # Создание директории
            typer.echo(f"[CREATED]: '{database_name}' at '{path_to_storage}'")
        else:
            typer.echo(f"[WARNING]: Database '{database_name}' already exists.")

    def delete_database(self, database_name: str, path_to_storage: str = "./databases"):    # Пример: python cli_core.py delete mydb или python cli_core.py --storage-path "E:\PyCharmProjects\kbdSQL\storage" delete mydb
        path_to_database = os.path.join(path_to_storage, database_name)
        if not os.path.exists(path_to_database):                                # Проверка, если путь не существует
            typer.echo(f"[ERROR]: Database '{path_to_storage}' not found.")
            raise typer.Exit()

        shutil.rmtree(path_to_database)                                         # Рекурсивно удаляет файл и всё её содержимое
        typer.echo(f"[DELETED]: '{database_name}'")


class DB:
    def __init__(self, current_database, path_to_storage, current_collection):
        self.path_to_database = os.path.join(path_to_storage, current_database)
        if not os.path.exists(self.path_to_database):                           # Проверка, если путь не существует
            typer.echo(f"[ERROR]: Database '{current_database}' at '{path_to_storage}' not found.")
            raise typer.Exit()

        self.database = Database(self.path_to_database, current_collection)

    def insert(self, string):                                                   # Пример: python cli_core.py db mydb/users insert "{'name': 'Иван', 'age': 18}" или python cli_core.py --storage-path "E:\PyCharmProjects\kbdSQL\storage" db mydb/users insert "{'name': 'Иван', 'age': 18}"
        try:
            self.database.insert(string)
            typer.echo("[INSERTED]: Successfully.")
        except json.JSONDecodeError:
            typer.echo("[ERROR]: Invalid JSON.")
        except Exception as e:
            typer.echo(f"[ERROR]: {e}")

    def index(self, field):                                                     # Пример: python cli_core.py db mydb/users index age или python cli_core.py --storage-path "E:\PyCharmProjects\kbdSQL\storage" db mydb/users index age
        try:
            count = self.database.index(field)
            typer.echo(f"[INDEXED]: {count} entries indexed by field '{field}'.")
        except Exception as e:
            typer.echo(f"[ERROR]: {e}")

    def search_by_condition(self, query):                                       # Пример: python cli_core.py db mydb/users condition "{'age': {'@eq': 18}}" или python cli_core.py --storage-path "E:\PyCharmProjects\kbdSQL\storage" db mydb/users condition "{'age': {'@eq': 18}}"
        try:
            json_documents = self.database.search_by_condition(query)           # Список "подходящих" json-документов
            typer.echo("[FOUND]:")
            for json_document in json_documents:
                typer.echo(json_document)
        except Exception as e:
            typer.echo(f"[ERROR]: {e}")


app = typer.Typer()
db_app = typer.Typer()

@app.callback()
def main(ctx: typer.Context, storage_path: str = typer.Option("./databases", "--storage-path", "-s", help="Путь к директории хранения баз данных.")):
    ctx.obj = {"storage_path": storage_path}

@app.command("list", help="Show databases.")
def list_dbs(ctx: typer.Context):
    storage_path = ctx.obj["storage_path"]
    Storage().list_databases(storage_path)

@app.command("create", help="Create database.")
def create_db(database_name: str, ctx: typer.Context):
    storage_path = ctx.obj["storage_path"]
    Storage().create_database(database_name, storage_path)

@app.command("delete", help="Delete database.")
def delete_db(database_name: str, ctx: typer.Context):
    storage_path = ctx.obj["storage_path"]
    Storage().delete_database(database_name, storage_path)


@db_app.callback()
def db_callback(ctx: typer.Context, database_and_collection: str = typer.Argument(..., help="Формат: 'database_name/current_collection'"), path_to_storage: str = typer.Option(None, help="Путь к директории хранения баз данных.")):
    # Если параметр path_to_storage не указан явно для команды db, берем глобальное значение
    if path_to_storage is None:
        path_to_storage = ctx.obj["storage_path"]
    if "/" not in database_and_collection:
        typer.echo("[ERROR]: Please use format 'database_name/current_collection'")
        raise typer.Exit()
    current_database, current_collection = database_and_collection.split("/", 1)
    ctx.obj = DB(current_database, path_to_storage, current_collection)

@db_app.command("insert", help="Insert json-object in collection.")
def insert(ctx: typer.Context, string: str):
    ctx.obj.insert(string)

@db_app.command("index", help="Index json-object in collection.")
def index(ctx: typer.Context, field: str):
    ctx.obj.index(field)

@db_app.command("condition", help="Search by condition in collection.")
def search_by_condition(ctx: typer.Context, query: str):
    ctx.obj.search_by_condition(query)


app.add_typer(db_app, name="db")


if __name__ == "__main__":
    app()