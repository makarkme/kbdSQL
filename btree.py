class Node:
    def __init__(self, leaf=False):
        self.data = [[], []]        # Самопичный итерируемый словарь [[keys], [values]]
        self.children = []          # Массив дочерних узлов [key]
        self.leaf = leaf            # Проверка на дочерний узел
                                    # t - 1 <= keys <= 2 * t - 1
                                    # t <= children_keys <= 2 * t

    def get_data(self, index):
        return self.data[0][index], self.data[1][index]

    def get_keys(self):
        return self.data[0]

    def append_data(self, key, value):
        self.data[0].append(key)
        self.data[1].append(value)

    def insert_data(self, index, key, value):
        self.data[0].insert(index, key)
        self.data[1].insert(index, value)

    def pop_data(self, index):
        self.data[0].pop(index)
        self.data[1].pop(index)

    def remove_data(self, key):
        index = self.index_data(key)
        self.data[0].pop(index)
        self.data[1].pop(index)

    def clear_data(self):
        self.data[0].clear()
        self.data[1].clear()

    def index_data(self, key):
        return self.data[0].index(key)

    def slice_data(self, start, end):
        temp_data = [[], []]
        for i in range(start, end):
            key, value = self.get_data(i)
            temp_data[0].append(key)
            temp_data[1].append(value)
        self.data.clear()
        self.data = temp_data

    def replace_data(self, index, key, value):
        self.data[0][index] = key
        self.data[1][index] = value


class BTree:
    def __init__(self, t):          # t - степень B-дерева; t >= 3
                                    # h - высота b-дерева (буквально количество чтений с диска)
                                    # n - количество элементов

                                    # h <= log(t)[(n + 1) / 2]
        self.root = Node(True)
        self.t = t

    def search(self, key, node=None):                               # key - искомое значение
        if node is None:                                            # Если начало поиска - "курсор" на корень
            node = self.root

        i = 0                                                       # Номер интервала, в котором может находиться key (искомое значение)
        while i < len(node.get_keys()) and key > node.get_keys()[i]:
            i += 1
        if i < len(node.get_keys()) and key == node.get_keys()[i]:  # Если нашли key в текущем узле
            return node, node.get_keys()[i]
        elif node.leaf:                                             # Если не нашли key в B-дереве
            return None
        else:
            return self.search(key, node.children[i])               # Переходим к нужному дочернему узлу

    def insert(self, key, value):
        root = self.root
        if len(root.get_keys()) == (2 * self.t) - 1:                # Если при вставке переполняется корень
            new_root = Node()                                       # Создаем новый корень
            self.root = new_root
            new_root.children.append(root)                          # Старый корень становится ребенком нового корня
            self.split_child(new_root, 0)
            self.insert_non_full(new_root, key, value)              # Вставляем в новый корень значение
        else:
            self.insert_non_full(root, key, value)                  # Вставляем в новый корень значение

    def insert_non_full(self, node, key, value):
        i = len(node.get_keys()) - 1

        if node.leaf:                                               # Листовая вставка
            while i >= 0 and key < node.get_keys()[i]:              # Находим нужный интервал для вставки
                i -= 1
            node.insert_data(i + 1, key, value)
        else:                                                       # Узловая вставка (нелистовая)
            while i >= 0 and key < node.get_keys()[i]:              # Ищем нужный интервал, в который потом перейдем
                i -= 1
            i += 1
            if len(node.children[i].get_keys()) == (2 * self.t) - 1:# Если дочерний узел заполнен
                self.split_child(node, i)                           # Разделяем дочерний узел на 2 узла
                if key > node.get_keys()[i]:
                    i += 1
            self.insert_non_full(node.children[i], key, value)      # Рекурсивно доходим до листового узла

    def split_child(self, parent, i):
        child = parent.children[i]

        new_child_node = Node(leaf=child.leaf)                      # Создаем 2 дочерний узел и копируем в него значения из 1 узла
        new_child_node.data = [child.data[0][:], child.data[1][:]]
        new_child_node.children = child.children[:]

        parent.children.insert(i + 1, new_child_node)               # Связываем родительский и новый дочерний узлы

        split = self.t - 1                                          # Уменьшаем степень, ибо теперь у нас 2 дочерних узла, вместо 1

        middle_key, middle_value = child.get_data(split)            # Берем средний ключ у дочернего узла и вставляем его в родительский узел
        parent.insert_data(i, middle_key, middle_value)

        child.slice_data(0, split)                                  # Разделяем значения между 2 дочерними узлами (учитываем, что перекинули центральное значение в родительский узел)
        new_child_node.slice_data(split + 1, len(new_child_node.get_keys()))

        if not child.leaf:                                          # Разделяем дочерние узлы между 2 узлами
            child.children = child.children[:split + 1]
            new_child_node.children = child.children[split + 1:]

    def delete(self, key, node=None):
        if node is None:
            node = self.root

        i = 0                                                       # Номер интервала, в котором может находиться key (удаляемое значение)
        while i < len(node.get_keys()) and key > node.get_keys()[i]:
            i += 1
        if node.leaf:                                               # Если нашли key и он находится в листе - просто удаляем его
            if i < len(node.get_keys()) and node.get_keys()[i] == key:
                node.pop_data(i)
            return

        if i < len(node.get_keys()) and node.get_keys()[i] == key:  # Если нашли key в текущем узле
            return self.delete_internal_node(node, key, i)
        elif len(node.children[i].get_keys()) >= self.t:            # Если не нашли key в текущем узле и условие с t выполняется, рекурсивно ищем в дочернем узле
            self.delete(key, node.children[i])
        else:                                                       # Если не нашли key в текущем узле и условие с t не выполняется
            if i != 0 and i + 2 < len(node.children):               # Если у текущего узла есть сосед слева и справа
                if len(node.children[i - 1].get_keys()) >= self.t:  # Если у левого соседа можно одолжить ключ - перемещаем этот ключ
                    self.delete_sibling(node, i, i - 1)
                elif len(node.children[i + 1].get_keys()) >= self.t:# Если у правого соседа можно одолжить ключ - перемещаем этот ключ
                    self.delete_sibling(node, i, i + 1)
                else:                                               # Если у обоих соседей нельзя одолжить ключ - объединяем узлы
                    self.delete_merge(node, i, i + 1)
            elif i == 0:                                            # Если текущий узел - самый левый
                if len(node.children[i + 1].get_keys()) >= self.t:  # Если у правого соседа можно одолжить ключ - перемещаем этот ключ
                    self.delete_sibling(node, i, i + 1)
                else:                                               # Иначе объединяем узлы
                    self.delete_merge(node, i, i + 1)
            elif i + 1 == len(node.children):                       # Если текущий узел - самый правый
                if len(node.children[i - 1].get_keys()) >= self.t:  # Если у левого соседа можно одолжить ключ - перемещаем этот ключ
                    self.delete_sibling(node, i, i - 1)
                else:                                               # Иначе объединяем узлы
                    self.delete_merge(node, i, i - 1)
            self.delete(key, node.children[i])                      # Рекурсивный вызов для повторного просмотра и удаления

    def delete_internal_node(self, node, key, i):
        if node.leaf:                                               # Если нашли key и он находится в листе - просто удаляем его
            if node.get_keys()[i] == key:
                node.pop_data(i)
            return

        if len(node.children[i].get_keys()) >= self.t:              # Если левый ребёнок имеет хотя бы t ключей - заменяем удаляемый ключ на максимальный ключ в левом поддереве
            predecessor_key, predecessor_value = self.delete_predecessor(node.children[i])
            node.replace_data(i, predecessor_key, predecessor_value)
            return
        elif len(node.children[i + 1].get_keys()) >= self.t:        # Если правый ребёнок имеет хотя бы t ключей - заменяем удаляемый ключ на минимальный ключ в правом поддереве
            successor_key, successor_value = self.delete_successor(node.children[i])
            node.replace_data(i, successor_key, successor_value)
            return
        else:                                                       # Если условие для узлов ломается - объединяем их
            self.delete_merge(node, i, i + 1)
            self.delete_internal_node(node.children[i], key, self.t - 1) # Рекурсивный вызов из дочернего узла

    def delete_predecessor(self, node):                             # Удаляет из узла максимальное (самое правое) ключ-значение и возвращает его
        if node.leaf:
            key, value = node.get_data(-1)
            node.pop_data(-1)
            return key, value

        last_key_index = len(node.get_keys()) - 1                   # Индекс последнего ключа в узле
        if len(node.children[last_key_index].get_keys()) >= self.t: # Проверяем, можно ли забрать у дочернего узла ключ
            self.delete_sibling(node, last_key_index + 1, last_key_index)
        else:                                                       # Если нет - объединяем их
            self.delete_merge(node, last_key_index, last_key_index + 1)
        return self.delete_predecessor(node.children[last_key_index])

    def delete_successor(self, node):                               # Удаляет из узла минимальное (самое левое) ключ-значение и возвращает его
        if node.leaf:
            key, value = node.get_data(0)
            node.pop_data(0)
            return key, value

        if len(node.children[1].get_keys()) >= self.t:              # Аналогично delete_predecessor(self, node)
            self.delete_sibling(node, 0, 1)
        else:
            self.delete_merge(node, 0, 1)
        return self.delete_successor(node.children[0])

    def delete_merge(self, node, i, j):                             # Когда 2 соседних дочерних узла содержат меньше t ключей, происходит их объединение
        merge_node = node.children[i]                               # i - главый дочерний узел (центральный), j - либо левый, либо правый дочерний узел

        if j > i:                                                   # Если j - правый дочерний узел
            right_child = node.children[j]
            merge_node.append_data(*node.get_data(i))               # Записываем ключ-значение, которое разделяет 2 дочерних узла

            for k in range(len(right_child.get_keys())):            # Переносим все ключи-значения и дочерние узлы в merge_node
                merge_node.append_data(*right_child.get_data(k))
                if len(right_child.children) > 0:
                    merge_node.children.append(right_child.children[k])
            if len(right_child.children) > 0:
                merge_node.children.append(right_child.children.pop()) # Добавляем последний дочерний узел (его не захватил цикл выше)

            new_node = merge_node
            node.pop_data(i)                                        # Удаляем ключ-значение, которым разделялись 2 дочерних узла, и который мы опустили
            node.children.pop(j)                                    # Удаляем связь с правым дочерним узлом (он слился с центральным дочерним узлом)
        else:                                                       # Если j - левый дочерний узел
            left_child = node.children[j]
            merge_node.append_data(*node.get_data(j))

            for i in range(len(merge_node.get_keys())):             # Всё то же самое, но слияние в другую сторону
                left_child.append_data(*merge_node.get_data(i))
                if len(left_child.children) > 0:
                    left_child.children.append(merge_node.children[i])
            if len(left_child.children) > 0:
                left_child.children.append(merge_node.children.pop())

            new_node = left_child
            node.pop_data(j)
            node.children.pop(i)

        if node == self.root and len(node.get_keys()) == 0:         # Если после слияния в корне больше нет data — дерево уменьшилось в высоту, и new_node становится новым корнем
            self.root = new_node

    def delete_sibling(self, node, i, j):                           # Отбираем ключ у соседнего дочернего узла, если в текущем дочернем узле не хватает ключей, а у соседа их достаточно
        add_node = node.children[i]                                 # i - узел, которому добавляем ключи, j - узел, у которого забираем ключи
        if i < j:                                                   # Если сосед справа (по аналогии с delete_merge(self, node, i, j))
            right_child = node.children[j]
            add_node.append_data(*node.get_data(i))                 # Переносим родительское ключ-значение в дочерний узел
            node.replace_data(i, *right_child.get_data(0))          # Поднимаем первое ключ-значение правого дочернего узла в родительский узел
                                                                    # Получилось что-то вроде малого левого поворота
            if len(right_child.children) > 0:
                add_node.children.append(right_child.children[0])   # Переносим первого ребёнка правого дочернего узла
                right_child.children.pop(0)
            right_child.pop_data(0)
        else:                                                       # Если сосед слева
            left_child = node.children[j]
            add_node.insert_data(0, *node.get_data(i - 1))          # Переносим ключ-значение из родителя в начало
            node.replace_data(i - 1, *left_child.get_data(-1))      # Переносим последние ключ-значение из правого дочернего узла в родителя
            left_child.pop_data(-1)
            if len(left_child.children) > 0:                        # Если есть дочерние узлы, переносим последнего ребёнка из левого соседа в начало
                add_node.children.insert(0, left_child.children.pop())

    def print_tree(self, node, level=0):
        print(f'Level {level}', end=": ")
        for i in range(len(node.get_keys())):
            print(node.get_data(i), end=" ")
        print()
        level += 1

        if len(node.children) > 0:
            for i in node.children:
                self.print_tree(i, level)


# Тестирование
def delete_example():
    # Создаём листья с key-value
    first_leaf = Node(True)
    first_leaf.data = [[1, 9], ["doc1", "doc9"]]

    second_leaf = Node(True)
    second_leaf.data = [[17, 19, 21], ["doc17", "doc19", "doc21"]]

    third_leaf = Node(True)
    third_leaf.data = [[23, 25, 27], ["doc23", "doc25", "doc27"]]

    fourth_leaf = Node(True)
    fourth_leaf.data = [[31, 32, 39], ["doc31", "doc32", "doc39"]]

    fifth_leaf = Node(True)
    fifth_leaf.data = [[41, 47, 50], ["doc41", "doc47", "doc50"]]

    sixth_leaf = Node(True)
    sixth_leaf.data = [[56, 60], ["doc56", "doc60"]]

    seventh_leaf = Node(True)
    seventh_leaf.data = [[72, 90], ["doc72", "doc90"]]

    # Дочерние узлы
    root_left_child = Node()
    root_left_child.data = [[15, 22, 30], ["doc15", "doc22", "doc30"]]
    root_left_child.children = [first_leaf, second_leaf, third_leaf, fourth_leaf]

    root_right_child = Node()
    root_right_child.data = [[55, 63], ["doc55", "doc63"]]
    root_right_child.children = [fifth_leaf, sixth_leaf, seventh_leaf]

    # Корень
    root = Node()
    root.data = [[40], ["doc40"]]
    root.children = [root_left_child, root_right_child]

    B = BTree(3)
    B.root = root

    print('\n--- Original B-Tree ---\n')
    B.print_tree(B.root)

    print('\n--- Case 1: DELETED 21 ---\n')
    B.delete(21)
    B.print_tree(B.root)

    print('\n--- Case 2a: DELETED 30 ---\n')
    B.delete(30)
    B.print_tree(B.root)

    print('\n--- Case 2b: DELETED 27 ---\n')
    B.delete(27)
    B.print_tree(B.root)

    print('\n--- Case 2c: DELETED 22 ---\n')
    B.delete(22)
    B.print_tree(B.root)

    print('\n--- Case 3b: DELETED 17 ---\n')
    B.delete(17)
    B.print_tree(B.root)

    print('\n--- Case 3a: DELETED 9 ---\n')
    B.delete(9)
    B.print_tree(B.root)


def insert_and_search_example():
    B = BTree(3)

    for i in range(10):
        B.insert(i, f"doc{i}")

    print("\n--- Tree after insertions ---")
    B.print_tree(B.root)

    print()
    keys_to_search_for = [2, 9, 11, 4]
    for key in keys_to_search_for:
        result = B.search(key)
        if result is not None:
            node, found_key = result
            value = node.data[1][node.index_data(found_key)]
            print(f'{key} is in the tree with value "{value}"')
        else:
            print(f'{key} is NOT in the tree')


def main():
    print('\n--- INSERT & SEARCH ---\n')
    insert_and_search_example()

    print('\n--- DELETE TESTS ---\n')
    delete_example()

main()
