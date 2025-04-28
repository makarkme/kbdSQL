import re
from datetime import datetime


class QueryEngine:
    def __init__(self, collection):
        self.collection = collection

    def parse_query(self, query: dict):
        # Преобразует запрос в функцию-предикат.
        # Обрабатываем сначала все логические операторы (@or, @and, @not), добавляя их в список условий, а затем – все поля.

        conditions = []  # Все условия, которые были заданы

        # Обработка логических операторов
        if "@or" in query:
            or_operators = [self.parse_query(sub_query) for sub_query in
                            query["@or"]]  # Сбор всех подусловий как функций

            def or_predicate(json_document: dict) -> bool:  # Возвращает True, если хоть одна подфункция вернула True
                return any(or_operator(json_document) for or_operator in or_operators)

            conditions.append(or_predicate)

        if "@and" in query:
            and_operators = [self.parse_query(sub_query) for sub_query in query["@and"]]

            def and_predicate(json_document: dict) -> bool:  # Возвращающает True, если все подфункции вернут True
                return all(and_operator(json_document) for and_operator in and_operators)

            conditions.append(and_predicate)

        if "@not" in query:
            not_operator = self.parse_query(query["@not"])

            def not_predicate(json_document: dict) -> bool:
                return not not_operator(json_document)

            conditions.append(not_predicate)

        # Обработка полей и условий
        for field, condition in query.items():
            if field in ("@or", "@and", "@not"):
                continue

            if isinstance(condition, dict):  # Если условие в словаре
                for operator, value in condition.items():
                    if operator == "@regex":
                        conditions.append(self._regex_condition(field, value))
                    elif operator == "@length":
                        conditions.append(self._length_condition(field, value))
                    # elif operator == "@lower":
                    #     conditions.append(self.lower_condition(field, value))
                    # elif operator == "@upper":
                    #     conditions.append(self.upper_condition(field, value))
                    else:  # Всё, что не является специальными функциями
                        conditions.append(self._create_condition(field, operator, value))
            else:
                if isinstance(condition, (str, int, float, bool)):
                    conditions.append(self._list_variable_condition(field, condition))
                else:
                    conditions.append(self._create_condition(field, "@eq", condition))

        return lambda json_document: all(cond(json_document) for cond in conditions)

    def _create_condition(self, field, operator: str, value):
        # Для поля field и операции operator создаёт предикат, сравнивающий реальное значение из документа с value.

        def check(json_document):  # Будет вызываться для каждого документа
            doc_value = self.collection.get_value(json_document, field)
            if doc_value is None:
                return False

            if isinstance(doc_value, list):
                if operator == "@eq":  # Оператор ==
                    return value in doc_value  # True, если искомое значение есть в списке
                elif operator == "@ne":  # Оператор !=
                    return value not in doc_value  # True, если искомого значения нет в списке

                # Для всех остальных операторов пробегаем по элементам и сравниваем
                return any(self._compare_items(item, operator, value) for item in doc_value)

            # Если значение не список (одно значение), используем общий метод сравнения
            return self._compare_items(doc_value, operator, value)

        return check

    def _compare_items(self, doc_value, operator: str, value) -> bool:
        # Сравнивает между собой значение в документе и заданное значение

        # Числовые специальные операторы
        if isinstance(doc_value, (int, float)):
            if operator == "@abs":
                return abs(doc_value) == value
            if operator == "@round":
                return round(doc_value) == value

        # Общие сравнения: =, !=, >, <, >=, <=
        try:
            if operator == "@eq": return doc_value == value
            if operator == "@ne": return doc_value != value
            if operator == "@gt": return doc_value > value
            if operator == "@lt": return doc_value < value
            if operator == "@gte": return doc_value >= value
            if operator == "@lte": return doc_value <= value
        except TypeError:  # Если типы несравнимы (например, str > int)
            return False

        # Строковые операции и работа с датами
        if isinstance(doc_value, str):
            # Регистр
            # if operator == "@lower":
            #     return doc_value.lower() == value.lower()
            # if operator == "@upper":
            #     return doc_value.upper() == value.upper()

            # Подстроковые операции
            # if operator == "@contains":
            #     return value.lower() in doc_value.lower()
            # if operator == "@startswith":
            #     return doc_value.lower().startswith(value.lower())
            # if operator == "@endswith":
            #     return doc_value.lower().endswith(value.lower())

            try:  # Для работы с датами (как ISO-строка)
                doc_date = datetime.fromisoformat(doc_value)
                if operator == "@year":
                    return doc_date.year == value
                if operator == "@month":
                    return doc_date.month == value
                if operator == "@day":
                    return doc_date.day == value
            except ValueError:  # Не дата
                pass

        return False  # Если не сработало ни одно условие

    def _list_variable_condition(self, field, value):
        # Если значение в документе - список или простое значение (пример: "field": value, а не {"@op": ...})

        def check(json_document: dict) -> bool:
            doc_value = self.collection.get_value(json_document, field)
            if not doc_value:
                return False

            if len(doc_value) == 1:
                single = doc_value[0]
                if isinstance(single, list):
                    return value in single  # распаковываем список-значение
                return single == value  # обычное сравнение для скаляра
                # несколько отдельных совпадений
            return value in doc_value

        return check

    def _regex_condition(self, field, pattern):
        # Предикат: True, если в любом из значений поля field найдено совпадение с регуляркой pattern

        try:
            prog = re.compile(pattern)
        except re.error:
            # Некорректное регулярное выражение — всегда False
            return lambda json_document: False

        def check(json_document: dict) -> bool:
            doc_value = self.collection.get_value(json_document, field)
            if not doc_value:
                return False
            for value in doc_value:
                if prog.search(str(value)):
                    return True
            return False

        return check

    def _length_condition(self, field, length):
        # Предикат: True, если длина значения поля равна length
        # – 1 значение в doc_value: len(doc_value[0])
        # – несколько значений: len(doc_value) == length

        def check(json_document: dict) -> bool:
            doc_value = self.collection.get_value(json_document, field)
            if not doc_value:
                return False
            # один результат — проверяем длину самого объекта
            if len(doc_value) == 1:
                value = doc_value[0]
                if isinstance(value, (str, list)):
                    return len(value) == length
                if isinstance(value, (int, float)):
                    return len(str(value)) == length
                return False

            # несколько результатов — проверяем размер списка
            return len(doc_value) == length

        return check

    # def lower_condition(self, field, value):
    #     # Предикат: True, если первое значение поля (строка) в lower() равно value.lower()
    #     # – 1 значение в поле (строка или число): его lower() равен value.lower()
    #     # – несколько значений: всё элементы (строка) при lower() равен value.lower()
    #
    #     target = value.lower()
    #
    #     def check(json_document: dict) -> bool:
    #         doc_value = self.collection.get_value(json_document, field)[0]
    #         if not doc_value:
    #             return False
    #
    #         for v in doc_value:
    #             if isinstance(v, str):
    #                 if v.lower() != target:
    #                     return False
    #             elif isinstance(v, (int, float)):
    #                 if str(v).lower() != target:
    #                     return False
    #             else:
    #                 return False  # неподдерживаемый тип
    #         return True  # все значения прошли проверку
    #
    #     return check
    #
    # def upper_condition(self, field, value):
    #     def check(json_document: dict) -> bool:
    #         doc_value = self.collection.get_value(json_document, field)[0]
    #         if isinstance(doc_value, str):
    #             return doc_value.upper() == value.upper()
    #         return False
    #
    #     return check
