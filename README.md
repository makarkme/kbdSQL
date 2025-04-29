# kbdSQL
**Educational database management system; student project of LETI - Krivonosov, Bugrov, Dolgiy**

# Требования: 
*Разработать СУБД на основе JSON, предназначенную для хранения, управления и запроса JSON-документов.*

## Что она должна уметь?
1. Хранить JSON-объекты
2. Записывать JSON-объекты
3. Индексировать JSON-объекты
4. Обрабатывать запросы пользователя (язык запросов на основе SQL)

## 1. Хранение:
    
    - постоянная память
    - файловая директория по усмотрению пользователя
    - каждая коллекция хранится в отдельной директории
    - каждый документ сохраняется в отдельном JSON-файле
    - уникальный идентификатор документа генерируется автоматически

## 2. Запись:

    - как один JSON, так и коллекция JSON-документов в одном файле
    - JSON разных типов (int, str, float и т. п.)

## 3. Индексация:

    - использование индексов для ускорения поиска
    - реализация B-дерева для индексации
    - поддержка индексации по любым полям документа

## 4. Язык запросов:

    - поддержка операторов сравнения (eq,ne,gt,lt,gte,lte)
    - поддержка логических операторов (and, or, not)
    - поддержка операторов для работы со строками (length) 
    - поддержка операторов для работы со числами (abs, round) 
    - поддержка операторов для работы с регулярными выражениями (regex)
    - поддержка операторов для работы с датами (year, month, day)

## 5. Особенности реализации:

    - легковесная архитектура без внешних зависимостей
    - простая расширяемость для добавления новых функций
    - поддержка сложных структур данных JSON


## 6. Использование:

### Общие указания

Все команды запускаются через:

```bash
python -m code.cli_core [опции] [действие]
```

Параметр `--storage-path` является необязательным. По умолчанию папка хранения — `/databases`.

---

### Операции с базами данных

#### Вывод списка всех баз данных

```bash
python -m code.cli_core list
```

С указанием пути:

```bash
python -m code.cli_core --storage-path "E:\PyCharmProjects\kbdSQL\storage" list
```

#### Создание базы данных

```bash
python -m code.cli_core create mydb
```

С указанием пути:

```bash
python -m code.cli_core --storage-path "E:\PyCharmProjects\kbdSQL\storage" create mydb
```

#### Удаление базы данных

```bash
python -m code.cli_core delete mydb
```

С указанием пути:

```bash
python -m code.cli_core --storage-path "E:\PyCharmProjects\kbdSQL\storage" delete mydb
```

---

### Операции с коллекциями

#### Вставка JSON-объекта

```bash
python -m code.cli_core db mydb/users insert "{'name': 'Иван', 'age': 18}"
```

С указанием пути:

```bash
python -m code.cli_core --storage-path "E:\PyCharmProjects\kbdSQL\storage" db mydb/users insert "{'name': 'Иван', 'age': 18}"
```

#### Удаление JSON-документа

```bash
python -m code.cli_core db mydb/users delete "531b4cdd-bc58-4aa9-aca5-5d1b7c44715f"
```

С указанием пути:

```bash
python -m code.cli_core --storage-path "E:\PyCharmProjects\kbdSQL\storage" db mydb/users delete "531b4cdd-bc58-4aa9-aca5-5d1b7c44715f"
```

#### Индексация поля

```bash
python -m code.cli_core db mydb/users index age
```

С указанием пути:

```bash
python -m code.cli_core --storage-path "E:\PyCharmProjects\kbdSQL\storage" db mydb/users index age
```

#### Поиск по условию

```bash
python -m code.cli_core db mydb/users condition "{'age': {'@eq': 18}}"
```

С указанием пути:

```bash
python -m code.cli_core --storage-path "E:\PyCharmProjects\kbdSQL\storage" db mydb/users condition "{'age': {'@eq': 18}}"
```

#### Вывод списка всех JSON-документов

```bash
python -m code.cli_core db mydb/users list_jsons
```

С указанием пути:

```bash
python -m code.cli_core --storage-path "E:\PyCharmProjects\kbdSQL\storage" db mydb/users list_jsons
```

---

### Примечания

- Синтаксис JSON-запросов обязательно в кавычках.
- Имена баз данных и коллекций регистрозависимы.
- При ошибках ввода система сообщит о некорректности запроса.
