class BTreeNode:
    def __init__(self, leaf=False):
        self.leaf = leaf
        self.keys = []
        self.values = []
        self.children = []

class BTree:
    def __init__(self, order=3):
        self.root = BTreeNode(leaf=True)
        self.order = order

    def insert(self, key, doc_id):
        found = self._search_node(self.root, key)
        if found:
            node, idx = found
            if doc_id not in node.values[idx]:
                node.values[idx].append(doc_id)
        else:
            self._insert_key_value(key, [doc_id])

    def search(self, operator, value):
        results = []
        self._traverse_tree(self.root, operator, value, results)
        return [doc_id for sublist in results for doc_id in sublist]

    def _search_node(self, node, key):
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]:
            return (node, i)
        elif node.leaf:
            return None
        else:
            return self._search_node(node.children[i], key)

    def _insert_key_value(self, key, value):
        root = self.root
        if len(root.keys) >= 2*self.order - 1:
            new_root = BTreeNode()
            new_root.children.append(root)
            self._split_child(new_root, 0)
            self.root = new_root
            self._insert_non_full(new_root, key, value)
        else:
            self._insert_non_full(root, key, value)

    def _insert_non_full(self, node, key, value):
        i = len(node.keys) - 1
        if node.leaf:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            node.keys.insert(i+1, key)
            node.values.insert(i+1, value)
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if len(node.children[i].keys) >= 2*self.order - 1:
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], key, value)

    def _split_child(self, parent, idx):
        child = parent.children[idx]
        new_node = BTreeNode(leaf=child.leaf)
        split = self.order - 1
        
        parent.keys.insert(idx, child.keys[split])
        parent.values.insert(idx, child.values[split])
        
        new_node.keys = child.keys[split+1:]
        new_node.values = child.values[split+1:]
        child.keys = child.keys[:split]
        child.values = child.values[:split]
        
        if not child.leaf:
            new_node.children = child.children[split+1:]
            child.children = child.children[:split+1]
        
        parent.children.insert(idx+1, new_node)

    def _traverse_tree(self, node, operator, target, results):
        i = 0
        while i < len(node.keys):
            key = node.keys[i]
            
            if not node.leaf:
                self._traverse_tree(node.children[i], operator, target, results)

            if (
                (operator == "$eq" and key == target) or
                (operator == "$gt" and key > target) or
                (operator == "$gte" and key >= target) or
                (operator == "$lt" and key < target) or
                (operator == "$lte" and key <= target)
            ):
                results.append(node.values[i])
            
            i += 1

        if not node.leaf:
            self._traverse_tree(node.children[i], operator, target, results)
