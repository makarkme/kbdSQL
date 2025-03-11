import os
import uuid
import json
from datetime import datetime
from btree import *
from indexation import *
from collection import *
from database import *

if __name__ == "__main__":
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
    
    users.insert({
        "name": "Bob",
        "age": 35,
        "email": "BOB@WORK.COM",
        "tags": ["manager"],
        "bio": "Team Lead"
    })
    
    users.insert({
        "name": "Charlie",
        "age": 28,
        "email": "charlie@test.org",
        "tags": ["user", "tester"],
        "bio": "QA Engineer"
    })
    
    users.insert({
        "name": "David",
        "age": 40,
        "email": "DAVID@example.com",
        "tags": ["admin", "manager"],
        "bio": "Senior Developer"
    })
    
    print("1. Базовый выбор всех документов:")
    for user in users.find({}):
        print(f"{user['name']} ({user['age']} лет)")
    
    print("\n2. Фильтр по точному совпадению (email):")
    results = users.find({"email": "charlie@test.org"})
    for user in results:
        print(user)
    
    print("\n3. Операторы сравнения для чисел:")
    print("Пользователи старше 30:")
    for user in users.find({"age": {"$gt": 30}}):
        print(f"{user['name']} ({user['age']})")
    
    print("\nПользователи младше или равные 35:")
    for user in users.find({"age": {"$lte": 35}}):
        print(f"{user['name']} ({user['age']})")
    
    print("\n4. Логические операторы (AND):")
    results = users.find({
        "bio": "Senior Developer",
        "age": {"$gte": 28}
    })
    print("Активные пользователи старше 28 лет:")
    for user in results:
        print(f"{user['name']} (Возраст: {user['age']}, Био: {user['bio']})")
    
    print("\n5. Работа с массивами (тегами):")
    print("Пользователи с тегом 'admin':")
    for user in users.find({"tags": "admin"}):
        print(f"- {user['name']} ({user['tags']})")
    
    print("\n6. Комбинированные условия с $or:")
    results = users.find({
        "$or": [
            {"age": {"$gte": 30}},
            {"email": {"$lower": "david@example.com"}}
        ]
    })
    for user in results:
        print(f"- {user['name']} (Age: {user['age']}, Email: {user['email']})")
    
    print("\n7. Строковые функции:")
    print("Поиск по email без учета регистра:")
    for user in users.find({"email": {"$lower": "alice@example.com"}}):
        print(f"- {user['name']} ({user['email']})")
    
    print("\nПоиск по регулярному выражению:")
    for user in users.find({"bio": {"$regex": r"Developer$"}}):
        print(f"- {user['name']} ({user['bio']})")
    
    print("\nПоиск по длине строки:")
    for user in users.find({"bio": {"$length": 11}}):
        print(f"- {user['name']} ({len(user['bio'])} chars: {user['bio']})")