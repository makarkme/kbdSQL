import typer
import os
import shutil
import json

from code.database import Database


class Storage:
    def __init__(self):
        pass

    def list_databases(self, path_to_storage: str = "./databases"):
        # Вывод списка всех баз данных в заданной папке (по-умолчанию /databases).
        # Пример 1: python -m code.cli_core list
        # Пример 2: python -m code.cli_core --storage-path "E:\PyCharmProjects\kbdSQL\storage" list

        if not os.path.exists(path_to_storage):
            typer.echo(f"[ERROR]: Directory '{path_to_storage}' not found.")
            raise typer.Exit(1)

        databases = os.listdir(path_to_storage)
        if not databases:
            typer.echo(f"[WARNING]: Databases not found in '{path_to_storage}'.")
            raise typer.Exit(0)
        else:
            typer.echo(f"[DATABASES IN]: '{path_to_storage}'")
            for database in databases:
                typer.echo(f" -- {database}")

    def create_database(self, database_name: str, path_to_storage: str = "./databases"):
        # Создание базы данных в заданной папке (по-умолчанию /databases).
        # Пример 1: python -m code.cli_core create mydb
        # Пример 2: python -m code.cli_core --storage-path "E:\PyCharmProjects\kbdSQL\storage" create mydb

        if not os.path.exists(path_to_storage):
            typer.echo(f"[ERROR]: Directory '{path_to_storage}' not found.")
            raise typer.Exit(1)

        path_to_database = os.path.join(path_to_storage, database_name)
        if not os.path.exists(path_to_database):
            os.makedirs(path_to_database)
            typer.echo(f"[CREATED]: '{database_name}' at '{path_to_storage}'")
        else:
            typer.echo(f"[WARNING]: Database '{database_name}' already exists.")

    def delete_database(self, database_name: str, path_to_storage: str = "./databases"):
        # Удаление базы данных в заданной папке (по-умолчанию /databases).
        # Пример 1: python -m code.cli_core delete mydb
        # Пример 2: python -m code.cli_core --storage-path "E:\PyCharmProjects\kbdSQL\storage" delete mydb

        if not os.path.exists(path_to_storage):
            typer.echo(f"[ERROR]: Directory '{path_to_storage}' not found.")
            raise typer.Exit(1)

        path_to_database = os.path.join(path_to_storage, database_name)
        if not os.path.exists(path_to_database):
            typer.echo(f"[ERROR]: Database '{path_to_database}' not found.")
            raise typer.Exit(1)
        else:
            shutil.rmtree(path_to_database)  # Рекурсивно удаляет файл и всё её содержимое
            typer.echo(f"[DELETED]: '{database_name}'")


class DB:
    def __init__(self, current_database: str, path_to_storage: str, current_collection: str):
        self.path_to_database = os.path.join(path_to_storage, current_database)

        if not os.path.exists(self.path_to_database):
            typer.echo(f"[ERROR]: Database '{current_database}' at '{path_to_storage}' not found.")
            raise typer.Exit(1)

        self.database = Database(self.path_to_database, current_collection)

    def insert(self, string: str):
        # Вставка json-объекта в выбранную базу данных.
        # Пример 1: python -m code.cli_core db mydb/users insert "{'name': 'Иван', 'age': 18}"
        # Пример 2: python -m code.cli_core --storage-path "E:\PyCharmProjects\kbdSQL\storage" db mydb/users insert "{'name': 'Иван', 'age': 18}"
        if not string.strip():
            typer.echo("[ERROR]: Empty input.")
            raise typer.Exit(1)

        try:
            self.database.insert(string)
            typer.echo("[INSERTED]: Successfully.")
        except (json.JSONDecodeError, SyntaxError) as error:
            typer.echo(f"[ERROR]: {type(error).__name__}")
            raise typer.Exit(1)
        except Exception as error:
            typer.echo(f"[ERROR]: {type(error).__name__}")
            raise typer.Exit(1)

    def delete(self, filename: str):
        # Удаление json-файла из выбранной базы данных.
        # Пример 1: python -m code.cli_core db mydb/users delete "531b4cdd-bc58-4aa9-aca5-5d1b7c44715f"
        # Пример 2: python -m code.cli_core --storage-path "E:\PyCharmProjects\kbdSQL\storage" db mydb/users delete "531b4cdd-bc58-4aa9-aca5-5d1b7c44715f"
        if not filename.strip():
            typer.echo("[ERROR]: Empty input.")
            raise typer.Exit(1)

        try:
            path_to_json_document = self.database.delete(filename)
            typer.echo(f"[DELETED]: {path_to_json_document} successfully.")
        except Exception as error:
            typer.echo(f"[ERROR]: {type(error).__name__}")
            raise typer.Exit(1)

    def index(self, field: str):
        # Индексация выбранного поля по всем json-объектам в выбранной базе данных.
        # Пример 1: python -m code.cli_core db mydb/users index age
        # Пример 2: python -m code.cli_core --storage-path "E:\PyCharmProjects\kbdSQL\storage" db mydb/users index age
        if not field.strip():
            typer.echo("[ERROR]: Empty field name.")
            raise typer.Exit(1)

        try:
            count = self.database.index(field)
            typer.echo(f"[INDEXED]: {count} entries indexed by field '{field}'.")
            return count
        except Exception as error:
            typer.echo(f"[ERROR]: {type(error).__name__}: {error}")
            raise typer.Exit(1)

    def search_by_condition(self, query: str):
        # Поиск json-документов по заданному условию в выбранной базе данных.
        # Пример 1: python -m code.cli_core db mydb/users condition "{'age': {'@eq': 18}}"
        # Пример 2: python -m code.cli_core --storage-path "E:\PyCharmProjects\kbdSQL\storage" db mydb/users condition "{'age': {'@eq': 18}}"
        if not query.strip():
            typer.echo("[ERROR]: Empty query.")
            raise typer.Exit(1)

        try:
            json_documents = self.database.search_by_condition(query)  # Список "подходящих" json-документов
            if json_documents is None:
                typer.echo("[SEARCH]: Not found json_documents.")
            else:
                typer.echo("[FOUND]:")
                for json_document in json_documents:
                    typer.echo(json_document)
        except Exception as error:
            typer.echo(f"[ERROR]: {type(error).__name__}: {error}")
            raise typer.Exit(1)

    def list_jsons(self):
        # Вывод списка всех json-документов в заданной коллекции.
        # Пример 1: python -m code.cli_core db mydb/users list_jsons
        # Пример 2: python -m code.cli_core --storage-path "E:\PyCharmProjects\kbdSQL\storage" db mydb/users list_jsons
        filenames = self.database.get_filenames()
        if not filenames:
            typer.echo(f"[WARNING]: JSONS not found in '{self.path_to_database}'.")
            raise typer.Exit(0)
        else:
            typer.echo(f"[JSONS IN]: '{self.path_to_database}'")
            for filename, _ in filenames:
                typer.echo(f" -- {filename}")


app = typer.Typer()
db_app = typer.Typer()


@app.callback()
def main(ctx: typer.Context, storage_path: str = typer.Option("./databases", "--storage-path", "-p",
                                                              help="Path to database storage directory.")):
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
def db_callback(ctx: typer.Context,
                database_and_collection: str = typer.Argument(..., help="Format: 'database_name/current_collection'"),
                path_to_storage: str = typer.Option(None, help="Path to database storage directory.")):
    # Если параметр path_to_storage не указан явно для команды db, берем глобальное значение
    if path_to_storage is None:
        path_to_storage = ctx.obj["storage_path"]

    if "/" not in database_and_collection:
        typer.echo("[ERROR]: Please use format 'database_name/current_collection'")
        raise typer.Exit(1)
    current_database, current_collection = database_and_collection.split("/", 1)
    ctx.obj = DB(current_database, path_to_storage, current_collection)


@db_app.command("insert", help="Insert json-object in collection.")
def insert(ctx: typer.Context, string: str):
    ctx.obj.insert(string)


@db_app.command("delete", help="Delete json-object in collection.")
def delete(ctx: typer.Context, filename: str):
    ctx.obj.delete(filename)


@db_app.command("index", help="Index json-object in collection.")
def index(ctx: typer.Context, field: str):
    ctx.obj.index(field)


@db_app.command("condition", help="Search by condition in collection.")
def search_by_condition(ctx: typer.Context, query: str):
    ctx.obj.search_by_condition(query)

@db_app.command("list_jsons", help="Show jsons in collection.")
def list_jsons(ctx: typer.Context):
    ctx.obj.list_jsons()


app.add_typer(db_app, name="db")

if __name__ == "__main__":
    app()
