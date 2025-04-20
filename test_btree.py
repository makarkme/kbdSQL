import unittest
from btree import Node, BTree


class TestNode(unittest.TestCase):
    def test_append_and_get(self):
        node = Node(leaf=True)

        node.append_pair('a', '1')
        self.assertEqual(node.get_keys(), ['a'])
        self.assertEqual(node.get_values(), [['1']])
        node.append_pair('a', '2')
        self.assertEqual(node.get_values(), [['1', '2']])

        node.insert_pair(0, 'b', '3')
        self.assertEqual(node.get_keys(), ['b', 'a'])
        self.assertEqual(node.get_values(), [['3'], ['1', '2']])

        node.pop_pair(1)
        self.assertEqual(node.get_keys(), ['b'])
        self.assertEqual(node.get_values(), [['3']])

    def test_slice_and_replace(self):
        node = Node(leaf=True)

        for i in range(5):
            node.append_pair(f'k{i}', str(i))

        original_keys = node.get_keys()[:]
        node.slice_data(1, 4)
        self.assertEqual(node.get_keys(), original_keys[1:4])

        node.replace_data(1, 'x', '9')
        key, value = node.get_pair(1)
        self.assertEqual((key, value), ('x', '9'))


class TestBTreeInsert(unittest.TestCase):
    def setUp(self):
        self.tree = BTree(2)

    def test_insert_and_search(self):
        self.tree.insert('k1', 'v1')
        self.assertEqual(self.tree.search('k1'), ['v1'])
        self.tree.insert('k1', 'v2')
        self.assertCountEqual(self.tree.search('k1'), ['v1', 'v2'])
        self.assertEqual(self.tree.search('none'), [])

    def test_duplicate_insertions(self):
        self.tree.insert('dup', 'first')
        self.tree.insert('dup', 'second')
        self.assertCountEqual(self.tree.search('dup'), ['first', 'second'])

    def test_split_root(self):
        # при вставке 4 ключей с t=2 корень должен разделиться
        for key in ['a', 'b', 'c', 'd']:
            self.tree.insert(key, key)
        root = self.tree.root
        self.assertFalse(root.leaf)
        self.assertGreaterEqual(len(root.children), 2)
        self.assertEqual(self.tree.search('c'), ['c'])


class TestBTreeDelete(unittest.TestCase):
    def setUp(self):
        leaves_data = [
            ([1, 9], [['doc1'], ['doc9']]),
            ([17, 19, 21], [['doc17'], ['doc19'], ['doc21']]),
            ([23, 25, 27], [['doc23'], ['doc25'], ['doc27']]),
            ([31, 32, 39], [['doc31'], ['doc32'], ['doc39']]),
            ([41, 47, 50], [['doc41'], ['doc47'], ['doc50']]),
            ([56, 60], [['doc56'], ['doc60']]),
            ([72, 90], [['doc72'], ['doc90']]),
        ]
        self.leaves = []
        for keys, vals in leaves_data:
            leaf = Node(leaf=True)
            leaf.data = [keys, vals]
            self.leaves.append(leaf)

        self.left = Node()
        self.left.data = [[15, 22, 30], [['doc15'], ['doc22'], ['doc30']]]
        self.left.children = self.leaves[:4]

        self.right = Node()
        self.right.data = [[55, 63], [['doc55'], ['doc63']]]
        self.right.children = self.leaves[4:]

        self.root = Node()
        self.root.data = [[40], [['doc40']]]
        self.root.children = [self.left, self.right]

        self.tree = BTree(3)
        self.tree.root = self.root

    def test_delete_21(self):
        self.assertEqual(self.tree.search(21), ['doc21'])
        self.tree.delete(21)
        self.assertEqual(self.tree.search(21), [])
        self.assertEqual(self.tree.search(19), ['doc19'])

    def test_delete_30(self):
        self.assertEqual(self.tree.search(30), ['doc30'])
        self.tree.delete(30)
        self.assertEqual(self.tree.search(30), [])
        self.assertEqual(self.tree.search(22), ['doc22'])

    def test_delete_sequence(self):
        for key in [22, 27, 17, 9]:
            self.assertEqual(self.tree.search(key), [f'doc{key}'])
            self.tree.delete(key)
            self.assertEqual(self.tree.search(key), [])


if __name__ == '__main__':
    unittest.main()
