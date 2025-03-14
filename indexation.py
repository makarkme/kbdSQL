from btree import *

class Index:
    def __init__(self, field):
        self.field = field
        self.btree = BTree()