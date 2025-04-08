# CLI - это интерфейс командной строки, способ взаимодействия с программой с помощью ввода текста в терминале.
# Чтоб не писать реализацию cli руками, можно использовать удобную альтернативу - typer

import typer
import json
import ast
import os
import shutil

from database import Database


# Зачем MainCLI? - Впоследствии расширение функционала для работы с разными бд - пересохранение/копирование/переименование и тд.
class MainCLI:
    def __init__(self):
        pass

    def list_databases(self, path: str = "./databases"):                        # Пример: python cli_core.py list
        if not os.path.exists(path):                                            # Проверка, если путь не существует
            typer.echo(f"[ERROR]: Directory '{path}' not found.")
            raise typer.Exit()

        databases = os.listdir(path)
        if not databases:
            typer.echo(f"[WARNING]: No databases found in '{path}'.")
        else:
            typer.echo(f"[DATABASES FIND IN]: '{path}'")
            for name in databases:
                typer.echo(f" -- {name}")

    def create_database(self, name: str, path: str = "./databases"):            # Пример: python cli_core.py create mydb
        full_path = os.path.join(path, name)
        if not os.path.exists(full_path):                                       # Проверка, если путь не существует
            os.makedirs(full_path)                                              # Создание директории
            typer.echo(f"[CREATED]: '{name}' at '{path}'")
        else:
            typer.echo(f"[WARNING]: Database '{name}' already exists.")

    def delete_database(self, db_name: str, path: str = "./databases"):         # Пример: python cli_core.py delete mydb
        full_path = os.path.join(path, db_name)
        if not os.path.exists(full_path):                                       # Проверка, если путь не существует
            typer.echo(f"[ERROR]: Database '{path}' not found.")
            raise typer.Exit()

        shutil.rmtree(full_path)                                                # Рекурсивно удаляет файл и всё её содержимое
        typer.echo(f"[DELETED]: '{db_name}'")


# Зачем DBCLI? - Для работы с collections внутри бд. Впоследствии расширение функционала.
class DBCLI:
    def __init__(self, db_name: str, collection: str, path: str = "./databases"):
        self.db = Database(db_name, path)
        self.current_collection = self.db.get_collection(collection)
        self.db_name = db_name
        self.collection = collection


    def insert(self, document: str):                                            # Пример: python cli_core.py db mydb/users insert "{'name': 'Иван', 'age': 18}"
        if not self.current_collection:
            typer.echo("[ERROR]: No collection selected! Use 'use' first.")
            raise typer.Exit()

        try:
            doc = json.loads(document.replace("'", '"'))
            doc_id = self.current_collection.collection_insert(doc)
            typer.echo(f"[INSERT ID]: '{doc_id}'")
        except Exception as e:
            typer.echo(f"[ERROR]: {e}")

    def index(self, field: str):                                                # Пример: python cli_core.py db mydb/users index age
        if not self.current_collection:
            typer.echo("[ERROR]: No collection selected! Use 'use' first.")
            raise typer.Exit()

        count = self.current_collection.create_index(field)                     # Количество найденных значений
        if count == 0:
            typer.echo(f"[NOT FOUND]: '{field}'")
        else:
            typer.echo(f"[INDEX CREATE]: '{field}' ({count})")

    def find(self, query: str):                                                 # Пример: python cli_core.py db mydb/users find "{'age': {'@eq': 18}}"
        if not self.current_collection:
            typer.echo("[ERROR]: No collection selected! Use 'use' first.")
            raise typer.Exit()

        try:
            try:
                query_dict = json.loads(query)
            except json.JSONDecodeError:
                query_dict = ast.literal_eval(query)                            # Превращает "{'age': {'`$gt': 18}}" в словарь
                print(query_dict)
            results = self.current_collection.find_doc(query_dict)              # results - список "подходящих" документов
            for json_doc in results:
                typer.echo(json.dumps(json_doc, indent=2, ensure_ascii=False))  # json.dumps - превращает dict обратно в json; indent=2 - многострочное форматирование
            typer.echo(f"[FOUND]: {len(results)} document(s).")
        except Exception as e:
            typer.echo(f"[ERROR]: {e}")

    # (нужно дописать реализацию)
    # (удаляет документ по id)
    def delete(self, doc_id: str):
        pass

    # # (удаляет документ по id)
    # def delete(self, doc_id: str):
    #     pass

    # (вывожит все коллекции)
    def list_collections(self):
        pass


app = typer.Typer()

@app.callback()
def main(ctx: typer.Context):
    ctx.obj = MainCLI()

@app.command("list", help="Show databases.")
def list_dbs(path: str = typer.Option("./databases")):
    MainCLI().list_databases(path)

@app.command("create", help="Create database.")
def create_db(name: str, path: str = typer.Option("./databases")):
    MainCLI().create_database(name, path)

@app.command("delete", help="Delete database.")
def delete_db(name: str, path: str = typer.Option("./databases")):
    MainCLI().delete_database(name, path)

db_app = typer.Typer()
app.add_typer(db_app, name="db")


@db_app.callback()
def db_callback(ctx: typer.Context, db_and_collection: str = typer.Argument(...), path: str = typer.Option("./databases")):
    if "/" not in db_and_collection:
        typer.echo("[ERROR]: Please use format 'name_database/collection'")
        raise typer.Exit()

    db_name, collection = db_and_collection.split("/", 1)
    ctx.obj = DBCLI(db_name, collection, path)

@db_app.command("insert")
def insert(ctx: typer.Context, document: str):
    ctx.obj.insert(document)

@db_app.command("index")
def index(ctx: typer.Context, field: str):
    ctx.obj.index(field)

@db_app.command("find")
def find(ctx: typer.Context, query: str):
    ctx.obj.find(query)


if __name__ == "__main__":
    app()