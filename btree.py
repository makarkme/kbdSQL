class Node:
    def __init__(self, leaf=False):
        self.data = [[], []]                                        # Самопичный итерируемый словарь [[keys], [values]] ВАЖНО: на 1 ключ может быть несколько values(id), поэтому key: [id1, id2, id3...]
        self.children = []                                          # Массив дочерних узлов [key]
        self.leaf = leaf                                            # Проверка на дочерний узел
                                                                    # t - 1 <= keys <= 2 * t - 1
                                                                    # t <= children_keys <= 2 * t

    def get_keys(self) -> list:                                     # Возвращает [key_1, key_2,...]
        return self.data[0]

    def get_values(self) -> list:                                   # Возвращает [[id1_1, id2_1,...], [id1_2, id2_2,...]...]
        return self.data[1]

    def get_pair(self, index: int) -> tuple:
        return self.data[0][index], self.data[1][index]

    def append_pair(self, key, value):
        if isinstance(value, str):                                  # Если value: str (стандартный случай)
            if key not in self.data[0]:
                self.data[0].append(key)
                self.data[1].append([value])
            else:
                i = self.data[0].index(key)
                self.data[1][i].append(value)
        if isinstance(value, list):                                 # Если value: list (например из get_pair())
            if key not in self.data[0]:
                self.data[0].append(key)
                self.data[1].append(value)
            else:
                i = self.data[0].index(key)
                for j in range(len(value)):
                    self.data[1][i].append(value[j])

    def insert_pair(self, index: int, key, value):
        if isinstance(value, str):                                  # Если value: str (стандартный случай)
            if key not in self.data[0]:
                self.data[0].insert(index, key)
                self.data[1].insert(index, [value])
            else:
                i = self.data[0].index(key)
                self.data[1][i].append(value)
        if isinstance(value, list):                                 # Если value: list (например из get_pair())
            if key not in self.data[0]:
                self.data[0].insert(index, key)
                self.data[1].insert(index, value)
            else:
                i = self.data[0].index(key)
                for j in range(len(value)):
                    self.data[1][i].append(value[j])

    def pop_pair(self, index: int):
        self.data[0].pop(index)
        self.data[1].pop(index)

    def slice_data(self, start: int, end: int):
        temp_data = [[], []]
        for i in range(start, end):
            key, value = self.get_pair(i)
            temp_data[0].append(key)
            temp_data[1].append(value)
        self.data.clear()
        self.data = temp_data

    def replace_data(self, index: int, key, value: str):
        self.data[0][index] = key
        self.data[1][index] = value


class BTree:
    def __init__(self, t):                                          # t - степень B-дерева; t >= 3
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
            return node.get_values()[i]                             # Возвращает [[id1_i, id2_i,...]
        elif node.leaf:                                             # Если не нашли key в B-дереве
            return None
        else:
            return self.search(key, node.children[i])               # Переходим к нужному дочернему узлу

    def insert(self, key, value: str):
        root = self.root
        if len(root.get_keys()) == (2 * self.t) - 1:                # Если при вставке переполняется корень
            new_root = Node()                                       # Создаем новый корень
            self.root = new_root
            new_root.children.append(root)                          # Старый корень становится ребенком нового корня
            self._split_child(new_root, 0)
            self._insert_non_full(new_root, key, value)             # Вставляем в новый корень значение
        else:
            self._insert_non_full(root, key, value)                 # Вставляем в новый корень значение

    def _insert_non_full(self, node, key, value: str):
        i = len(node.get_keys()) - 1

        if node.leaf:                                               # Листовая вставка
            while i >= 0 and key < node.get_keys()[i]:              # Находим нужный интервал для вставки
                i -= 1
            node.insert_pair(i + 1, key, value)
        else:                                                       # Узловая вставка (нелистовая)
            while i >= 0 and key < node.get_keys()[i]:              # Ищем нужный интервал, в который потом перейдем
                i -= 1
            i += 1
            if len(node.children[i].get_keys()) == (2 * self.t) - 1:# Если дочерний узел заполнен
                self._split_child(node, i)                          # Разделяем дочерний узел на 2 узла
                if key > node.get_keys()[i]:
                    i += 1
            self._insert_non_full(node.children[i], key, value)     # Рекурсивно доходим до листового узла

    def _split_child(self, parent, i):
        child = parent.children[i]

        new_child_node = Node(leaf=child.leaf)                      # Создаем 2 дочерний узел и копируем в него значения из 1 узла
        new_child_node.data = [child.data[0][:], child.data[1][:]]
        new_child_node.children = child.children[:]

        parent.children.insert(i + 1, new_child_node)               # Связываем родительский и новый дочерний узлы

        split = self.t - 1                                          # Уменьшаем степень, ибо теперь у нас 2 дочерних узла, вместо 1

        middle_key, middle_value = child.get_pair(split)            # Берем средний ключ у дочернего узла и вставляем его в родительский узел
        parent.insert_pair(i, middle_key, middle_value)

        child.slice_data(0, split)                                  # Разделяем значения между 2 дочерними узлами (учитываем, что перекинули центральное значение в родительский узел)
        new_child_node.slice_data(split + 1, len(new_child_node.get_keys()))
        # new_child_node.slice_data(split + 1, 2 * (split + 1) - 1)

        if not child.leaf:                                          # Разделяем дочерние узлы между 2 узлами
            child.children = child.children[:split + 1]
            new_child_node.children = child.children[split + 1:]

    def delete(self, key, node=None, key_exists=None):
        if key_exists is None:
            if self.search(key) is None:
                return -1                                           # Возвращаем исключение - удаляемого ключа не существует в дереве
            else:
                key_exists = True

        if node is None:
            node = self.root

        i = 0                                                       # Номер интервала, в котором может находиться key (удаляемое значение)
        while i < len(node.get_keys()) and key > node.get_keys()[i]:
            i += 1
        if node.leaf:                                               # Если нашли key и он находится в листе - просто удаляем его
            if i < len(node.get_keys()) and node.get_keys()[i] == key:
                node.pop_pair(i)
            return

        if i < len(node.get_keys()) and node.get_keys()[i] == key:  # Если нашли key в текущем узле
            return self._delete_internal_node(node, key, i)
        elif len(node.children[i].get_keys()) >= self.t:            # Если не нашли key в текущем узле и условие с t выполняется, рекурсивно ищем в дочернем узле
            self.delete(key, node.children[i], key_exists)
        else:                                                       # Если не нашли key в текущем узле и условие с t не выполняется
            if i != 0 and i + 2 < len(node.children):               # Если у текущего узла есть сосед слева и справа
                if len(node.children[i - 1].get_keys()) >= self.t:  # Если у левого соседа можно одолжить ключ - перемещаем этот ключ
                    self._delete_sibling(node, i, i - 1)
                elif len(node.children[i + 1].get_keys()) >= self.t:# Если у правого соседа можно одолжить ключ - перемещаем этот ключ
                    self._delete_sibling(node, i, i + 1)
                else:                                               # Если у обоих соседей нельзя одолжить ключ - объединяем узлы
                    self._delete_merge(node, i, i + 1)
            elif i == 0:                                            # Если текущий узел - самый левый
                if len(node.children[i + 1].get_keys()) >= self.t:  # Если у правого соседа можно одолжить ключ - перемещаем этот ключ
                    self._delete_sibling(node, i, i + 1)
                else:                                               # Иначе объединяем узлы
                    self._delete_merge(node, i, i + 1)
            elif i + 1 == len(node.children):                       # Если текущий узел - самый правый
                if len(node.children[i - 1].get_keys()) >= self.t:  # Если у левого соседа можно одолжить ключ - перемещаем этот ключ
                    self._delete_sibling(node, i, i - 1)
                else:                                               # Иначе объединяем узлы
                    self._delete_merge(node, i, i - 1)
            self.delete(key, node.children[i], key_exists)          # Рекурсивный вызов для повторного просмотра и удаления

    def _delete_internal_node(self, node, key, i):
        if node.leaf:                                               # Если нашли key и он находится в листе - просто удаляем его
            if node.get_keys()[i] == key:
                node.pop_pair(i)
            return

        if len(node.children[i].get_keys()) >= self.t:              # Если левый ребёнок имеет хотя бы t ключей - заменяем удаляемый ключ на максимальный ключ в левом поддереве
            predecessor_key, predecessor_value = self._delete_predecessor(node.children[i])
            node.replace_data(i, predecessor_key, predecessor_value)
            return
        elif len(node.children[i + 1].get_keys()) >= self.t:        # Если правый ребёнок имеет хотя бы t ключей - заменяем удаляемый ключ на минимальный ключ в правом поддереве
            successor_key, successor_value = self._delete_successor(node.children[i + 1])
            node.replace_data(i, successor_key, successor_value)
            return
        else:                                                       # Если условие для узлов ломается - объединяем их
            self._delete_merge(node, i, i + 1)
            self._delete_internal_node(node.children[i], key, self.t - 1) # Рекурсивный вызов из дочернего узла

    def _delete_predecessor(self, node):                             # Удаляет из узла максимальное (самое правое) ключ-значение и возвращает его
        if node.leaf:
            key, value = node.get_pair(-1)
            node.pop_pair(-1)
            return key, value

        last_key_index = len(node.get_keys()) - 1                   # Индекс последнего ключа в узле
        if len(node.children[last_key_index].get_keys()) >= self.t: # Проверяем, можно ли забрать у дочернего узла ключ
            self._delete_sibling(node, last_key_index + 1, last_key_index)
        else:                                                       # Если нет - объединяем их
            self._delete_merge(node, last_key_index, last_key_index + 1)
        return self._delete_predecessor(node.children[last_key_index])

    def _delete_successor(self, node):                               # Удаляет из узла минимальное (самое левое) ключ-значение и возвращает его
        if node.leaf:
            key, value = node.get_pair(0)
            node.pop_pair(0)
            return key, value

        if len(node.children[1].get_keys()) >= self.t:              # Аналогично delete_predecessor(self, node)
            self._delete_sibling(node, 0, 1)
        else:
            self._delete_merge(node, 0, 1)
        return self._delete_successor(node.children[0])

    def _delete_merge(self, node, i, j):                            # Когда 2 соседних дочерних узла содержат меньше t ключей, происходит их объединение
        merge_node = node.children[i]                               # i - главый дочерний узел (центральный), j - либо левый, либо правый дочерний узел

        if j > i:                                                   # Если j - правый дочерний узел
            right_child = node.children[j]
            merge_node.append_pair(*node.get_pair(i))               # Записываем ключ-значение, которое разделяет 2 дочерних узла

            for k in range(len(right_child.get_keys())):            # Переносим все ключи-значения и дочерние узлы в merge_node
                merge_node.append_pair(*right_child.get_pair(k))
                if len(right_child.children) > 0:
                    merge_node.children.append(right_child.children[k])
            if len(right_child.children) > 0:
                merge_node.children.append(right_child.children.pop()) # Добавляем последний дочерний узел (его не захватил цикл выше)

            new_node = merge_node
            node.pop_pair(i)                                        # Удаляем ключ-значение, которым разделялись 2 дочерних узла, и который мы опустили
            node.children.pop(j)                                    # Удаляем связь с правым дочерним узлом (он слился с центральным дочерним узлом)
        else:                                                       # Если j - левый дочерний узел
            left_child = node.children[j]
            merge_node.append_pair(*node.get_pair(j))

            for i in range(len(merge_node.get_keys())):             # Всё то же самое, но слияние в другую сторону
                left_child.append_pair(*merge_node.get_pair(i))
                if len(left_child.children) > 0:
                    left_child.children.append(merge_node.children[i])
            if len(left_child.children) > 0:
                left_child.children.append(merge_node.children.pop())

            new_node = left_child
            node.pop_pair(j)
            node.children.pop(i)

        if node == self.root and len(node.get_keys()) == 0:         # Если после слияния в корне больше нет data — дерево уменьшилось в высоту, и new_node становится новым корнем
            self.root = new_node

    def _delete_sibling(self, node, i, j):                          # Отбираем ключ у соседнего дочернего узла, если в текущем дочернем узле не хватает ключей, а у соседа их достаточно
        add_node = node.children[i]                                 # i - узел, которому добавляем ключи, j - узел, у которого забираем ключи
        if i < j:                                                   # Если сосед справа (по аналогии с delete_merge(self, node, i, j))
            right_child = node.children[j]
            add_node.append_pair(*node.get_pair(i))                 # Переносим родительское ключ-значение в дочерний узел
            node.replace_data(i, *right_child.get_pair(0))          # Поднимаем первое ключ-значение правого дочернего узла в родительский узел
                                                                    # Получилось что-то вроде малого левого поворота
            if len(right_child.children) > 0:
                add_node.children.append(right_child.children[0])   # Переносим первого ребёнка правого дочернего узла
                right_child.children.pop(0)
            right_child.pop_pair(0)
        else:                                                       # Если сосед слева
            left_child = node.children[j]
            add_node.insert_pair(0, *node.get_pair(i - 1))          # Переносим ключ-значение из родителя в начало
            node.replace_data(i - 1, *left_child.get_pair(-1))      # Переносим последние ключ-значение из правого дочернего узла в родителя
            left_child.pop_pair(-1)
            if len(left_child.children) > 0:                        # Если есть дочерние узлы, переносим последнего ребёнка из левого соседа в начало
                add_node.children.insert(0, left_child.children.pop())

    # def print_tree(self, node=None, level=0):
    #     if node is None:
    #         node = self.root
    #
    #     print(f'Level {level}', end=": ")
    #     for i in range(len(node.get_keys())):
    #         print(node.get_pair(i), end=" ")
    #     print()
    #     level += 1
    #
    #     if len(node.children) > 0:
    #         for i in node.children:
    #             self.print_tree(i, level)