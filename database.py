import os
from collection import *

class Database:
    def __init__(self, name, storage_path='./data'):
        self.path = os.path.join(storage_path, name)
        os.makedirs(self.path, exist_ok=True)
        self.collections = {}

    def get_collection(self, name):
        if name not in self.collections:
            self.collections[name] = Collection(name, self.path)
        return self.collections[name]