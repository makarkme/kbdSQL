import unittest
from btree import BTree
class TestBTree(unittest.TestCase):

    def setUp(self):
        self.tree = BTree(3)

    def test_insert(self):
        self.tree.insert(10, "id1") # вставка в пустое дерево
        self.tree.insert(20, ["id2", "id0"]) # вставка без разделения узлов
        self.tree.insert(30, ["i","d","3"])
        self.tree.insert(40, "id4")
        self.tree.insert(50, "id5")
        self.tree.insert(60, "id6") # вставка с разделением узла
        self.tree.insert(10, "id10") # вставка повторяющегося ключа
        self.assertEqual(self.tree.search(10), ["id1", "id10"])
        self.assertEqual(self.tree.search(20), ["id2", "id0"])
        self.assertEqual(self.tree.search(30), ["i","d","3"])
        self.assertEqual(self.tree.search(40), ["id4"])
        self.assertEqual(self.tree.search(50), ["id5"])
        self.assertEqual(self.tree.search(60), ["id6"])

    def test_delete(self):
        self.tree.insert(10, "id1")
        self.tree.insert(20, "id2")
        self.tree.insert(30, "id3")
        self.tree.insert(40, "id4")
        self.tree.insert(50, "id5")
        self.tree.insert(60, "id6")
        self.tree.delete(30) #удаление корня
        self.assertIsNone(self.tree.search(30))
        self.assertEqual(self.tree.search(20), ["id2"])
        self.assertEqual(self.tree.search(30), ["id3"])
        self.assertEqual(self.tree.search(40), ["id4"])
        self.assertEqual(self.tree.search(50), ["id5"])
        self.assertEqual(self.tree.search(60), ["id6"])
        self.tree.delete(1000) # try delete non-existent key
    # удаление корня и ключа из листа не проходят

    def test_empty_tree(self):
        # Проверка на пустое дерево
        self.assertIsNone(self.tree.search(10))

    def test_delete_all_elements(self):
        # Удаление всех элементов из дерева
        self.tree.insert(10, "id1")
        self.tree.insert(20, "id2")
        self.tree.insert(30, "id3")

        self.tree.delete(10)
        self.tree.delete(20)
        self.tree.delete(30)

        self.assertIsNone(self.tree.search(10))
        self.assertIsNone(self.tree.search(20))
        self.assertIsNone(self.tree.search(30))

    def test_search(self):
        self.assertIsNone(self.tree.search(100)) # поиск в пустом дереве
        self.tree.insert(10, "id1")
        self.assertEqual(self.tree.search(10), ["id1"]) # поиск сущ. key
        self.assertIsNone(self.tree.search(20)) # поиск не сущ. key

if __name__ == '__main__':
    unittest.main()