import uuid
import random
from datetime import datetime, timedelta
from faker import Faker
from collections import OrderedDict
from database import *

# Импорт ранее созданных классов Database и Collection
# Предполагается, что классы Database и Collection уже определены

fake = Faker()

def generate_complex_data(collection_type):
    """Генерация сложного объекта со всеми типами данных"""
    data = OrderedDict()
    
    # Общие поля для всех типов коллекций
    data['uuid'] = str(uuid.uuid4())
    data['string'] = fake.sentence()
    data['number'] = random.randint(1, 1000)
    data['float'] = round(random.uniform(1.0, 100.0), 2)
    data['boolean'] = random.choice([True, False])
    data['datetime'] = fake.date_time_this_decade().isoformat()
    data['array'] = [fake.word() for _ in range(random.randint(1, 5))]
    data['nested'] = {
        'nested_string': fake.city(),
        'nested_number': random.randint(100, 200),
        'nested_array': [random.random() for _ in range(3)]
    }
    
    # Специфичные поля для разных типов коллекций
    if collection_type == 'users':
        data['name'] = fake.name()
        data['email'] = fake.email()
        data['phone'] = fake.phone_number()
        data['address'] = {
            'street': fake.street_address(),
            'city': fake.city(),
            'zipcode': fake.zipcode()
        }
        data['metadata'] = {
            'created_at': fake.iso8601(),
            'updated_at': fake.iso8601(),
            'login_count': random.randint(0, 100)
        }
        
    elif collection_type == 'products':
        data['product_name'] = fake.catch_phrase()
        data['price'] = round(random.uniform(10.0, 1000.0), 2)
        data['in_stock'] = random.choice([True, False])
        data['categories'] = [fake.word() for _ in range(3)]
        data['manufacturer'] = {
            'name': fake.company(),
            'country': fake.country_code()
        }
        
    # Удаляем сгенерированный UUID, так как он будет добавлен автоматически
    del data['uuid']
    return data

def seed_database(db_name, collections):
    """Заполнение базы данных тестовыми данными"""
    db = Database(db_name)
    
    for collection_name in collections:
        coll = db.get_collection(collection_name)
        print(f"Генерация данных для {db_name}/{collection_name}...")
        
        # Генерация 100 документов
        for _ in range(100):
            doc = generate_complex_data(collection_name)
            
            # Вставка документа с автоматическим UUID
            coll.insert(doc)
            
        # Создание индексов
        coll.create_index('number')
        coll.create_index('datetime')
        coll.create_index('nested.nested_number')
        
    print(f"База данных {db_name} успешно заполнена!\n")

if __name__ == "__main__":
    # Генерация данных для двух баз данных
    databases = {
        "social_network": ["users", "posts", "comments"],
        "ecommerce": ["products", "orders", "reviews"]
    }
    
    for db_name, collections in databases.items():
        seed_database(db_name, collections)
    
    print("Все базы данных успешно созданы и заполнены!")