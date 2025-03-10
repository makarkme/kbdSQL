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

## 2. Запись:

    - как один JSON, так и коллекция JSON-документов в одном файле
    - JSON разных типов (int, str, float и т. п.)

## 3. Индексация:

    - по одному или нескольким полям документа

## 4. Язык запросов:

    - базовые команды, например, SELECT, WHERE
    - операторы сравнения, например, =, >, <, >=, <=, !=
    - логические операторы, например, AND, OR, NOT

## Использование:

# Добавление эл-ов в БД

db = Database("test_db")
    users = db.get_collection("users")
    
    # Очищаем коллекцию
    for f in os.listdir(users.path):
        os.remove(os.path.join(users.path, f))
    
    # Новые тестовые данные
    users.insert({
        "name": "Alice",
        "age": 25,
        "email": "Alice@Example.com",
        "tags": ["admin", "user"],
        "bio": "Python developer"
    })

# Получение из БД

print("\nПользователи младше или равные 35:")
    for user in users.find({"age": {"$lte": 35}}):
        print(f"{user['name']} ({user['age']})")