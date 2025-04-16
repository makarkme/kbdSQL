import unittest
import os
import shutil
from typer.testing import CliRunner
from cli_core import app

runner = CliRunner()

TEST_STORAGE_PATH = "./test_databases"

class TestCLI(unittest.TestCase):
    def setUp(self):
        # Создаем тестовую директорию
        if not os.path.exists(TEST_STORAGE_PATH):
            os.makedirs(TEST_STORAGE_PATH)

    def tearDown(self):
        # Удаляем тестовую директорию после каждого теста
        if os.path.exists(TEST_STORAGE_PATH):
            shutil.rmtree(TEST_STORAGE_PATH)

    def test_create_and_list_database(self):
        # Создание базы данных
        result_create = runner.invoke(app, ["--storage-path", TEST_STORAGE_PATH, "create", "mydb"])
        self.assertIn("[CREATED]: 'mydb'", result_create.output)

        # Проверка наличия базы данных
        result_list = runner.invoke(app, ["--storage-path", TEST_STORAGE_PATH, "list"])
        self.assertIn(" -- mydb", result_list.output)

    def test_create_existing_database(self):
        os.makedirs(os.path.join(TEST_STORAGE_PATH, "mydb"))
        result = runner.invoke(app, ["--storage-path", TEST_STORAGE_PATH, "create", "mydb"])
        self.assertIn("[WARNING]: Database 'mydb' already exists.", result.output)

    def test_delete_database(self):
        os.makedirs(os.path.join(TEST_STORAGE_PATH, "mydb"))
        result = runner.invoke(app, ["--storage-path", TEST_STORAGE_PATH, "delete", "mydb"])
        self.assertIn("[DELETED]: 'mydb'", result.output)
        self.assertFalse(os.path.exists(os.path.join(TEST_STORAGE_PATH, "mydb")))

    def test_delete_nonexistent_database(self):
        result = runner.invoke(app, ["--storage-path", TEST_STORAGE_PATH, "delete", "ghost_db"])
        self.assertIn("[ERROR]: Database", result.output)
        self.assertNotEqual(result.exit_code, 0) # в cli_core надо raise typer.Exit(code=1)

    def test_list_on_empty_storage(self):
        result = runner.invoke(app, ["--storage-path", TEST_STORAGE_PATH, "list"])
        self.assertIn("[WARNING]: Databases not found", result.output)

    def test_db_insert_invalid_json(self):
        os.makedirs(os.path.join(TEST_STORAGE_PATH, "mydb", "users"))
        # Создаем пустой JSON-файл, чтобы не падал Database.__init__
        with open(os.path.join(TEST_STORAGE_PATH, "mydb", "users", "data.json"), "w") as f:
            f.write("[]")

        result = runner.invoke(app, [
            "--storage-path", TEST_STORAGE_PATH,
            "db", "mydb/users", "insert", "{invalid json}"
        ])
        self.assertIn("[ERROR]: Invalid JSON.", result.output) # не проходит т.к. прокает SyntaxError потому что "{invalid json}" парсится как строка
        # варианта 2: либо фиксить cli_core либо заменить строку 61 на строку 63
        # строка 63: self.assertIn("[ERROR]", result.output)

if __name__ == "__main__":
    unittest.main()
