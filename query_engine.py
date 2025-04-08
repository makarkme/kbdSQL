import re
from datetime import datetime


class QueryEngine:
    def __init__(self, get_value):
        self.get_value = get_value

    def parse_query(self, query: dict):                                 # Проверяет, подходит ли документ под условие
        conditions = []                                                 # Все условия, которые были заданы

        # Обработка логических операторов
        if "@or" in query:
            or_conditions = [self.parse_query(cond) for cond in query["@or"]]   # Рекурсивно вызываем функцию для каждого подзапроса внутри "$or", в итоге получаем список функций-проверок
            return lambda doc: any(cond(doc) for cond in or_conditions)         # Вернет true если хотя бы один подзапрос (cond) вернет true
        if "@and" in query:
            and_conditions = [self.parse_query(cond) for cond in query["@and"]]
            return lambda doc: all(cond(doc) for cond in and_conditions)        # Вернет true если все подзапросы (cond) вернут true
        if "@not" in query:
            not_condition = self.parse_query(query["@not"])
            return lambda doc: not not_condition(doc)

        # Обработка полей и условий
        for field, condition in query.items():
            if isinstance(condition, dict):                             # Если условие в словаре
                for operator, value in condition.items():
                    if operator == "@regex":
                        conditions.append(self.regex_condition(field, value))
                    elif operator == "@length":
                        conditions.append(self.length_condition(field, value))
                    elif operator == "@lower":
                        conditions.append(self.lower_condition(field, value))
                    elif operator == "@upper":
                        conditions.append(self.upper_condition(field, value))
                    else:                                               # Всё, что не является специальными функциями
                        conditions.append(self.create_condition(field, operator, value))
            else:
                if isinstance(condition, (str, int, float, bool)):
                    conditions.append(self.list_variable_condition(field, condition))
                else:
                    conditions.append(self.create_condition(field, "@eq", condition))

        return lambda doc: all(cond(doc) for cond in conditions)


    def create_condition(self, field, operator: str, value):            # field - поле, по которому ишём, value - значение, с которым сравниваем
        def check(doc):                                                 # Будет вызываться для каждого документа
            doc_value = self.get_value(doc, field)
            if doc_value is None:
                return False

            if isinstance(doc_value, list):
                if operator == "@eq":                                   # Оператор ==
                    return value in doc_value
                elif operator == "@ne":                                 # Оператор !=
                    return value not in doc_value
                return any(self.compare_items(item, operator, value) for item in doc_value)

            return self.compare_items(doc_value, operator, value)

        return check

    def compare_items(self, doc_value, operator: str, value) -> bool:   # Сравнивает между собой значение в документе и заданное значение
        if isinstance(doc_value, (int, float)):
            if operator == "@abs":
                return abs(doc_value) == value
            if operator == "@round":
                return round(doc_value) == value

        try:
            if operator == "@eq": return doc_value == value
            if operator == "@ne": return doc_value != value
            if operator == "@gt": return doc_value > value
            if operator == "@lt": return doc_value < value
            if operator == "@gte": return doc_value >= value
            if operator == "@lte": return doc_value <= value
        except TypeError:
            return False

        if isinstance(doc_value, str):
            if operator == "@lower":
                return doc_value.lower() == value.lower()
            if operator == "@upper":
                return doc_value.upper() == value.upper()
            if operator == "@contains":
                return value.lower() in doc_value.lower()
            if operator == "@startswith":
                return doc_value.lower().startswith(value.lower())
            if operator == "@endswith":
                return doc_value.lower().endswith(value.lower())

            try:                                                        # Для работы с датами (как ISO-строка)
                doc_date = datetime.fromisoformat(doc_value)
                if operator == "@year":
                    return doc_date.year == value
                if operator == "@month":
                    return doc_date.month == value
                if operator == "@day":
                    return doc_date.day == value
            except ValueError:
                pass

        return False                                                    # Если не сработало ни одно условие


    def list_variable_condition(self, field, value):                    # Если значение в документе - список или простое значение
        def check(doc):
            doc_value = self.get_value(doc, field)
            if isinstance(doc_value, list):
                return value in doc_value
            return doc_value == value
        return check

    def regex_condition(self, field, pattern):                          # Для работы с регулярными выражениями
        regex = re.compile(pattern)
        def check(doc):
            doc_value = self.get_value(doc, field)
            if doc_value:
                return bool(regex.search(str(doc_value)))
            return False
        return check

    def length_condition(self, field, length):
        def check(doc):
            doc_value = self.get_value(doc, field)
            if isinstance(doc_value, (list, str)):
                return len(doc_value) == length
            return False

        return check

    def lower_condition(self, field, value):
        def check(doc):
            doc_value = self.get_value(doc, field)
            if isinstance(doc_value, str):
                return doc_value.lower() == value.lower()
            return False
        return check

    def upper_condition(self, field, value):
        def check(doc):
            doc_value = self.get_value(doc, field)
            if isinstance(doc_value, str):
                return doc_value.upper() == value.upper()
            return False
        return check