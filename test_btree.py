import unittest
from btree import Node, BTree


class TestNode(unittest.TestCase):
    def setUp(self):
        self.node = Node()

        self.node.data = [
            [1, 2, 3, 4, 5],
            [
                ["id1_1", "id1_2", "id1_3"],
                ["id2_1", "id2_2"],
                ["id3_1", "id3_2", "id3_3", "id3_4"],
                [],
                ["id5_1", "id5_2"]]]

    def test_get_keys(self):
        self.assertEqual(self.node.get_keys(), [1, 2, 3, 4, 5])
        self.assertNotEqual(self.node.get_keys(), [1, 2, 3, 4, 5, 6])

    def test_get_values(self):
        self.assertEqual(self.node.get_values(), [
            ["id1_1", "id1_2", "id1_3"],
            ["id2_1", "id2_2"],
            ["id3_1", "id3_2", "id3_3", "id3_4"],
            [],
            ["id5_1", "id5_2"]])
        self.assertNotEqual(self.node.get_keys(), [
            ["id1_1", "id1_2", "id1_3"],
            ["id2_1", "id2_2"],
            ["id3_1", "id3_2", "id3_3", "id3_4"],
            ["id5_1", "id5_2"]])

    def test_get_pair(self):
        self.assertEqual(self.node.get_pair(0), (1, ["id1_1", "id1_2", "id1_3"]))
        self.assertEqual(self.node.get_pair(3), (4, []))

        # нет обработки для index out of range

    def test_append_pair(self):
        self.node.append_pair(6, "id6_1")
        self.node.append_pair(6, "id6_1")
        self.node.append_pair(6, "id6_1")
        self.assertEqual(self.node.data, [
            [1, 2, 3, 4, 5, 6],
            [
                ["id1_1", "id1_2", "id1_3"],
                ["id2_1", "id2_2"],
                ["id3_1", "id3_2", "id3_3", "id3_4"],
                [],
                ["id5_1", "id5_2"],
                ["id6_1", "id6_1", "id6_1"]
            ]])

        self.node.append_pair(6, "id6_2")
        self.assertEqual(self.node.data, [
            [1, 2, 3, 4, 5, 6],
            [
                ["id1_1", "id1_2", "id1_3"],
                ["id2_1", "id2_2"],
                ["id3_1", "id3_2", "id3_3", "id3_4"],
                [],
                ["id5_1", "id5_2"],
                ["id6_1", "id6_1", "id6_1", "id6_2"]
            ]])

        self.node.append_pair(6, ["id6_3", "id6_4"])
        self.assertEqual(self.node.data, [
            [1, 2, 3, 4, 5, 6],
            [
                ["id1_1", "id1_2", "id1_3"],
                ["id2_1", "id2_2"],
                ["id3_1", "id3_2", "id3_3", "id3_4"],
                [],
                ["id5_1", "id5_2"],
                ["id6_1", "id6_1", "id6_1", "id6_2", "id6_3", "id6_4"]
            ]])

        self.node.append_pair(7, "id7_1")
        self.assertEqual(self.node.data, [
            [1, 2, 3, 4, 5, 6, 7],
            [
                ["id1_1", "id1_2", "id1_3"],
                ["id2_1", "id2_2"],
                ["id3_1", "id3_2", "id3_3", "id3_4"],
                [],
                ["id5_1", "id5_2"],
                ["id6_1", "id6_1", "id6_1", "id6_2", "id6_3", "id6_4"],
                ["id7_1"]
            ]])

    def test_insert_pair(self):
        self.node.insert_pair(0, 100, "id100_1")
        self.assertEqual(self.node.data, [
            [100, 1, 2, 3, 4, 5],
            [
                ["id100_1"],
                ["id1_1", "id1_2", "id1_3"],
                ["id2_1", "id2_2"],
                ["id3_1", "id3_2", "id3_3", "id3_4"],
                [],
                ["id5_1", "id5_2"]]])

        self.node.insert_pair(0, 100, ["id100_1", "id100_2"])
        self.assertEqual(self.node.data, [
            [100, 1, 2, 3, 4, 5],
            [
                ["id100_1", "id100_1", "id100_2"],
                ["id1_1", "id1_2", "id1_3"],
                ["id2_1", "id2_2"],
                ["id3_1", "id3_2", "id3_3", "id3_4"],
                [],
                ["id5_1", "id5_2"]]])

        # нет обработки для index out of range

    def test_pop_pair(self):
        self.node.pop_pair(0)
        self.assertEqual(self.node.data, [
            [2, 3, 4, 5],
            [
                ["id2_1", "id2_2"],
                ["id3_1", "id3_2", "id3_3", "id3_4"],
                [],
                ["id5_1", "id5_2"]]])

    def test_remove_value(self):
        self.node.remove_value(3, "id3_3")
        self.assertEqual(self.node.data, [
            [1, 2, 3, 4, 5],
            [
                ["id1_1", "id1_2", "id1_3"],
                ["id2_1", "id2_2"],
                ["id3_1", "id3_2", "id3_4"],
                [],
                ["id5_1", "id5_2"]]])

        self.node.remove_value(3, "id3_1")
        self.node.remove_value(3, "id3_2")
        self.node.remove_value(3, "id3_4")
        self.assertEqual(self.node.data, [
            [1, 2, 3, 4, 5],
            [
                ["id1_1", "id1_2", "id1_3"],
                ["id2_1", "id2_2"],
                [],
                [],
                ["id5_1", "id5_2"]]])

        # нет обработки для index out of range

    def test_slice_data(self):
        self.node.slice_data(2, 5)

        self.assertEqual(self.node.data, [
            [3, 4, 5],
            [
                ["id3_1", "id3_2", "id3_3", "id3_4"],
                [],
                ["id5_1", "id5_2"]]])

        self.node.slice_data(0, 2)
        self.assertEqual(self.node.data, [
            [3, 4],
            [
                ["id3_1", "id3_2", "id3_3", "id3_4"],
                []]])

        # нет обработки для index out of range

    def test_replace_data(self):
        self.node.replace_data(1, 100, ["id100_1", "id100_2"])

        self.assertEqual(self.node.data, [
            [1, 100, 3, 4, 5],
            [
                ["id1_1", "id1_2", "id1_3"],
                ["id100_1", "id100_2"],
                ["id3_1", "id3_2", "id3_3", "id3_4"],
                [],
                ["id5_1", "id5_2"]]])


class TestBTreeInsert(unittest.TestCase):
    def setUp(self):
        self.btree = BTree(3)

        self.root = Node(leaf=False)
        self.root.append_pair("G", ["idG_1", "idG_2", "idG_3"])
        self.root.append_pair("M", ["idM_1", "idM_2"])
        self.root.append_pair("P", ["idP_1", "idP_2", "idP_3", "idP_4"])
        self.root.append_pair("X", "idX_1")

        self.leaf1_1 = Node(leaf=True)
        self.leaf1_1.append_pair("A", ["idA_1", "idA_2", "idA_3"])
        self.leaf1_1.append_pair("C", ["idC_1", "idC_2"])
        self.leaf1_1.append_pair("D", ["idD_1", "idD_2", "idD_3", "idD_4"])
        self.leaf1_1.append_pair("E", "idE_1")

        self.leaf1_2 = Node(leaf=True)
        self.leaf1_2.append_pair("J", ["idJ_1", "idJ_2", "idJ_3"])
        self.leaf1_2.append_pair("K", ["idK_1", "idK_2"])

        self.leaf1_3 = Node(leaf=True)
        self.leaf1_3.append_pair("N", ["idN_1", "idN_2", "idN_3"])
        self.leaf1_3.append_pair("O", ["idO_1", "idO_2"])

        self.leaf1_4 = Node(leaf=True)
        self.leaf1_4.append_pair("R", ["idR_1", "idR_2", "idR_3"])
        self.leaf1_4.append_pair("S", ["idS_1", "idS_2"])
        self.leaf1_4.append_pair("T", ["idT_1", "idT_2", "idT_3", "idT_4"])
        self.leaf1_4.append_pair("U", "idU_1")
        self.leaf1_4.append_pair("V", ["idV_1", "idV_2", "idV_3"])

        self.leaf1_5 = Node(leaf=True)
        self.leaf1_5.append_pair("Y", ["idY_1", "idY_2", "idY_3"])
        self.leaf1_5.append_pair("Z", ["idZ_1", "idZ_2"])

        self.root.children = [self.leaf1_1, self.leaf1_2, self.leaf1_3, self.leaf1_4, self.leaf1_5]
        self.btree.root = self.root

        # [
        #   [['G','M','P','X']],
        #   [['A','C','D','E'], ['J','K'], ['N','O'], ['R','S','T','U','V'], ['Y','Z']]
        # ]

        print("SETUP:", self.btree.print_tree())

    def test_insert(self):
        self.assertEqual(self.btree.search("B"), [])
        self.btree.insert("B", "idB_1")
        # [
        #   [['G','M','P','X']],
        #   [['A','B','C','D','E'], ['J','K'], ['N','O'], ['R','S','T','U','V'], ['Y','Z']]
        # ]
        self.assertIn("B", self.leaf1_1.data[0])
        self.assertEqual(self.btree.search("B"), ["idB_1"])
        print("INSERT B:", self.btree.print_tree())

        self.assertEqual(self.btree.search("Q"), [])
        self.btree.insert("Q", "idQ_1")
        # [
        #   [['G','M','P','T','X']],
        #   [['A','B','C','D','E'], ['J','K'], ['N','O'], ['Q','R','S'] ['U','V'], ['Y','Z']]
        # ]
        self.assertIn("Q", self.btree.print_tree()[1][3])
        self.assertEqual(self.btree.search("Q"), ["idQ_1"])
        print("INSERT Q:", self.btree.print_tree())

        self.assertEqual(self.btree.search("L"), [])
        self.btree.insert("L", "idL_1")
        # [
        #   [['P']],
        #   [['G','M'], ['T','X']],
        #   [[['A','B','C','D','E'], ['J','K','L'], ['N','O']], [['Q','R','S'] ['U','V'], ['Y','Z']]]
        # ]
        self.assertIn("L", self.btree.print_tree()[2][0][1])
        self.assertEqual(self.btree.search("L"), ["idL_1"])
        print("INSERT L:", self.btree.print_tree())


class TestBTreeDelete(unittest.TestCase):
    def setUp(self):
        self.btree = BTree(3)

        self.root = Node(leaf=False)
        self.root.append_pair("P", ["idP_1"])

        self.leaf1_1 = Node(leaf=False)
        self.leaf1_1.append_pair("C", ["idC_1"])
        self.leaf1_1.append_pair("G", ["idG_1"])
        self.leaf1_1.append_pair("M", ["idM_1"])

        self.leaf1_2 = Node(leaf=False)
        self.leaf1_2.append_pair("T", ["idT_1"])
        self.leaf1_2.append_pair("X", ["idX_1"])

        self.leaf2_1 = Node(leaf=True)
        self.leaf2_1.append_pair("A", ["idA_1"])
        self.leaf2_1.append_pair("B", ["idB_1"])

        self.leaf2_2 = Node(leaf=True)
        self.leaf2_2.append_pair("D", ["idD_1"])
        self.leaf2_2.append_pair("E", ["idE_1"])
        self.leaf2_2.append_pair("F", ["idF_1"])

        self.leaf2_3 = Node(leaf=True)
        self.leaf2_3.append_pair("J", ["idJ_1"])
        self.leaf2_3.append_pair("K", ["idK_1"])
        self.leaf2_3.append_pair("L", ["idL_1"])

        self.leaf2_4 = Node(leaf=True)
        self.leaf2_4.append_pair("N", ["idN_1"])
        self.leaf2_4.append_pair("O", ["idO_1"])

        self.leaf2_5 = Node(leaf=True)
        self.leaf2_5.append_pair("Q", ["idQ_1"])
        self.leaf2_5.append_pair("R", ["idR_1"])
        self.leaf2_5.append_pair("S", ["idS_1"])

        self.leaf2_6 = Node(leaf=True)
        self.leaf2_6.append_pair("U", ["idU_1"])
        self.leaf2_6.append_pair("V", ["idV_1"])

        self.leaf2_7 = Node(leaf=True)
        self.leaf2_7.append_pair("Y", ["idY_1"])
        self.leaf2_7.append_pair("Z", ["idZ_1"])

        self.root.children = [self.leaf1_1, self.leaf1_2]
        self.leaf1_1.children = [self.leaf2_1, self.leaf2_2, self.leaf2_3, self.leaf2_4]
        self.leaf1_2.children = [self.leaf2_5, self.leaf2_6, self.leaf2_7]
        self.btree.root = self.root

        # [
        #   [['P']],
        #   [['C','G','M'], ['T','X']],
        #   [[['A','B'], ['D','E','F'], ['J','K','L'], ['N','O']], [['Q','R','S'], ['U','V'], ['Y','Z']]]
        # ]

        print("SETUP:", self.btree.print_tree())

    def test_delete(self):
        self.assertEqual(self.btree.search("F"), ["idF_1"])
        self.btree.delete("F")
        # [
        #   [['P']],
        #   [['C','G','M'], ['T','X']],
        #   [[['A','B'], ['D','E'], ['J','K','L'], ['N','O']], [['Q','R','S'], ['U','V'], ['Y','Z']]]
        # ]
        self.assertEqual(self.btree.search("F"), [])
        print("DELETE F:", self.btree.print_tree())

        self.assertEqual(self.btree.search("M"), ["idM_1"])
        self.btree.delete("M")
        # [
        #   [['P']],
        #   [['C','G','L'], ['T','X']],
        #   [[['A','B'], ['D','E'], ['J','K'], ['N','O']], [['Q','R','S'], ['U','V'], ['Y','Z']]]
        # ]
        self.assertEqual(self.btree.search("M"), [])
        print("DELETE M:", self.btree.print_tree())

        self.assertEqual(self.btree.search("G"), ["idG_1"])
        self.btree.delete("G")
        # [
        #   [['P']],
        #   [['C','L'], ['T','X']],
        #   [[['A','B'], ['D','E', 'J','K'], ['N','O']], [['Q','R','S'], ['U','V'], ['Y','Z']]]
        # ]
        self.assertEqual(self.btree.search("G"), [])
        print("DELETE G:", self.btree.print_tree())


class TestBTreeRemoveID(unittest.TestCase):
    def setUp(self):
        self.btree = BTree(3)

        self.root = Node(leaf=False)
        self.root.append_pair("G", ["idG_1", "idG_2", "idG_3"])
        self.root.append_pair("M", ["idM_1", "idM_2", "idG_1"])
        self.root.append_pair("P", ["idP_1", "idP_2", "idG_1", "idP_3", "idP_4"])
        self.root.append_pair("X", "idX_1")

        self.leaf1_1 = Node(leaf=True)
        self.leaf1_1.append_pair("A", ["idA_1", "idG_1", "idA_2", "idA_3"])
        self.leaf1_1.append_pair("C", ["idC_1", "idC_2"])
        self.leaf1_1.append_pair("D", ["idD_1", "idD_2", "idD_3", "idD_4"])
        self.leaf1_1.append_pair("E", "idE_1")

        self.leaf1_2 = Node(leaf=True)
        self.leaf1_2.append_pair("J", ["idJ_1", "idJ_2", "idG_1", "idJ_3"])
        self.leaf1_2.append_pair("K", ["idK_1", "idK_2"])

        self.leaf1_3 = Node(leaf=True)
        self.leaf1_3.append_pair("N", ["idN_1", "idN_2", "idG_1", "idN_3"])
        self.leaf1_3.append_pair("O", ["idO_1", "idO_2"])

        self.leaf1_4 = Node(leaf=True)
        self.leaf1_4.append_pair("R", ["idR_1", "idR_2", "idR_3"])
        self.leaf1_4.append_pair("S", ["idS_1", "idG_1", "idS_2"])
        self.leaf1_4.append_pair("T", ["idT_1", "idT_2", "idT_3", "idT_4"])
        self.leaf1_4.append_pair("U", "idU_1")
        self.leaf1_4.append_pair("V", ["idV_1", "idV_2", "idV_3"])

        self.leaf1_5 = Node(leaf=True)
        self.leaf1_5.append_pair("Y", ["idY_1", "idY_2", "idG_1", "idY_3"])
        self.leaf1_5.append_pair("Z", ["idG_1", "idZ_1", "idZ_2"])

        self.root.children = [self.leaf1_1, self.leaf1_2, self.leaf1_3, self.leaf1_4, self.leaf1_5]
        self.btree.root = self.root

    def test_remove_value(self):
        self.btree.remove_value("idG_1")
        self.assertEqual(self.btree.search("G"), ["idG_2", "idG_3"])
        self.assertEqual(self.btree.search("M"), ["idM_1", "idM_2"])
        self.assertEqual(self.btree.search("P"), ["idP_1", "idP_2", "idP_3", "idP_4"])
        self.assertEqual(self.btree.search("A"), ["idA_1", "idA_2", "idA_3"])
        self.assertEqual(self.btree.search("J"), ["idJ_1", "idJ_2", "idJ_3"])


if __name__ == '__main__':
    unittest.main()
