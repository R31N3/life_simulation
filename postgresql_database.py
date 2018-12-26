# -*- coding: utf-8 -*-

import threading
import psycopg2
import time

class DatabaseManager:
    def __init__(self, host: str, user: str, password: str, dbname: str,
                 port: str ='5432', require_autocommit: bool = True):
        """
        Производит первичное подключение к базе данных при инициализации
        ================================================================================
        :param host: database server address e.g., localhost or an IP address
        :param user: the username used to authenticate.
        :param password: password used to authenticate.
        :param dbname: the name of the database that you want to connect.
        :param port: the port number that defaults to 5432 if it is not provided.
        """
        # if 'data' not in os.listdir('.'):
        #     __import__('os').mkdir('data')  # очень плохой импорт!

        server_params = {'host': host,       'user': user, 'password': password,
                         'database': dbname, 'port': port}
        '''               host='localhost', user='shagonru', password='13082000'
                          dbname='programmer_simulator', port='5432'         '''
        self.connection = psycopg2.connect(**server_params)
        self.require_autocommit = require_autocommit
        self.connection.autocommit = self.require_autocommit
        print(threading.current_thread(), '__init__')

    def __del__(self):
        print(threading.current_thread(), '__del__')
        if self.require_autocommit is False:
            self.connection.commit()
        self.connection.close()

    @staticmethod
    def check_sql_injection(str_for_check: str) -> str:
        """
        Проверяет строку на наличие в ней SQL-подобного кода
        ================================================================================
        :param str_for_check: строка для проверки на SQL-синтаксис
        :return: строку, если всё хорошо; предупреждение, если плохо
        ================================================================================
        !!! будет сделано в ближайшее никогда !!!
        """
        some_code = 'some_code' + str_for_check
        return some_code

    @staticmethod
    def convert_pytype_to_sqltype(unconverted_type_string: str) -> str:
        """
        Превращает типы в пригодные для SQL, если они были указаны неверно
        ================================================================================
        :param unconverted_type_string: строка с названием типа в python
        :return: строка с типом, пригодным для SQL
        """
        converted_type = ''
        types_dict = {'serial':  'SERIAL',   'str':    'TEXT',   'int':     'INTEGER',
                      'float':   'REAL',     'string': 'TEXT',   'integer': 'INTEGER',
                      'list':    'TEXT',     'bytes':  'BYTEA',  'bool':    'BOOLEAN'}

        if unconverted_type_string.split()[0].upper() in types_dict.values():
            converted_type += unconverted_type_string.split()[0].upper()
        else:
            converted_type += types_dict[unconverted_type_string.split()[0]]

        if 'primary' in unconverted_type_string.lower():
            converted_type += ' PRIMARY KEY'

        if 'default' in unconverted_type_string.lower():
            converted_type += " DEFAULT " + ' '.join(unconverted_type_string.split()[2:])

        if 'not null' in unconverted_type_string.lower():
            converted_type += ' NOT NULL'

        if 'unique' in unconverted_type_string.lower():
            converted_type += ' UNIQUE'

        return converted_type

    def convert_dict_to_string(self, unconverted_dict: dict, separator=' ') -> str:
        """
        Превращает словарь в строку, которую можно использовать
        для конкатенации в SQL-запросах
        ================================================================================
        :param unconverted_dict: словарь со значениями
        :param separator: разделитель, стоящий между бывших словарных пар
        :return: строку, преобразованную по образцу
        ================================================================================
        Пример:
        было:  {'user_id': *значение1*, 'score': *значение2*}
        стало: 'user_id = *значение1*, score = *значение2*'
        при значении sep = ' = '
        """
        converted_string = ''
        count = 0
        dict_len = unconverted_dict.__len__()
        for item in unconverted_dict.items():
            count += 1
            comma = ', ' if count < dict_len else ''
            if len(item) > 1:  # строку с пробелами необходимо обраймлять в ' ', не строку - не надо
                if item[1].__class__ is not str or \
                        any([sqltype in item[1] for sqltype in
                             ['SERIAL', 'INTEGER', 'TEXT', 'REAL', 'BOOLEAN', 'BYTEA']]):
                    converted_string += str(item[0]) + separator + str(item[1]) + comma
                else:
                    converted_string += str(item[0]) + separator + self.cover_with_braces(str(item[1]), "'") + comma
        return converted_string

    @staticmethod
    def convert_digits_to_string(iterable_obj) -> list:
        """
        Превращает все элементы итерируемого объекта в строки и возвращает как лист.
        ================================================================================
        :param iterable_obj: получаем на вход итерируемый объект
        :return: возвращаем список, где все элементы приняли тип str
        """
        return [str(item) for item in iterable_obj]

    @staticmethod
    def add_dicts(*dicts) -> dict:
        """
        Складывает словари с одинаковыми ключами путём сложенния их значений, 
        возвращает словарь с результатами сложения и теми же ключами
        ================================================================================
        :param dicts: любое количество словарей, поданных позиционно
        :return: один словарь, результат их сложения типа dict
        """
        from collections import Counter  # Counter из collections - вид словаря, который позволяет нам считать
        result_dict = Counter()          # количество неизменяемых объектов (в большинстве случаев, строк)
        for dictionary in dicts:
            result_dict += Counter(dictionary)
        return dict(result_dict)

    @staticmethod
    def cover_with_braces(string: str, braces_type='''"''') -> str:
        """
        Оборачиваем строки в дополнительные скобки для адекватной
        подстановки в exec/eval или куда-либо ещё
        ================================================================================
        :param string: изначальная строка
        :param braces_type: необходимый тип скобок для обёртки
        :return: строку, где строковые элементы дополнительно обёрнуты
        в строку типа braces_type
        """
        if string != 'True' and string != 'False':
            return braces_type + string + braces_type
        else:
            return string[:]


        # result_list = []
        # for item in string.split(', '):  # если есть хотя бы 1 буква, то строка не число, но может быть bool
        #     if item != 'True' and item != 'False':
        #         result_list.append(braces_type + item + braces_type)
        #     else:  # в случае если не нужно обрамлять, оставляем как есть
        #         result_list.append(item)
        # return (', '.join(result_list) if len(result_list) > 1 else result_list[0]).replace("\\", "")

    @staticmethod
    def check_for_hidden_list_sequence(input_obj, sequence='#&%') -> bool:
        """
        Специфическая функция. Позволяет искать некую подстроку в
        записях, взятых из базы данных
        ================================================================================
        :param input_obj: объект вида [(), ()]. Вложенность не глубже
        двух уровней и НЕ МЕНЬШЕ двух уровней. Подстроено под
        стандартный возврат из базы данных методом SELECT
        :param sequence: искомая последовательность
        :return: значение True / False от нашёл / не нашёл
        """
        for outer_item in input_obj:
            for inner_item in outer_item:
                if type(inner_item) is str:
                    if inner_item.find(sequence) != -1:
                        return True
        return False

    @staticmethod
    def convert_strange_str_to_list(string: str, separator: str) -> list:
        """
        Специфическая функция. Конвертирует странную строку в лист.
        ================================================================================
        :param string: строка вида '[entry1#&% запись2 #&% "3"]'; [] опциональны
        :param separator: разделитель, по которому список будет образован
        :return: список
        """
        return string[1:len(string)-1].split(separator) if '[' and ']' in string else string.split(separator)

    def create_table(self, table_name: str, columns_dict: dict):
        """
        Создаём таблицу, если такой ещё нет.
        ================================================================================
        :param table_name: название создаваемой таблицы; Английский
        :param columns_dict: словарь, содержащий название столбца и его тип.
        Пример: {'score': 'int', 'username':'text'}
        value может содержать указатель primary, тогда при конвертации к ключу будет
        добавлено ключевое слово PRIMARY KEY для однозначной идентификации
        ================================================================================
        Запрос имеет SQL-синтаксис вида
        CREATE TABLE IF NOT EXISTS *название_таблицы*
        (user_id = *значение1*, score = *значение2*)
        """
        columns_dict = {key: self.convert_pytype_to_sqltype(value) for key, value in columns_dict.items()}
        # try:
        with self.connection.cursor() as cursor:
            cursor.execute(
                'CREATE TABLE IF NOT EXISTS {0}({1})'
                .format(table_name, self.convert_dict_to_string(columns_dict))
                )
        # except Exception as exc:
        #     print('Дата: {0}\nОШИБКА:{1}'.format(time.strftime("%d.%m.%Y - %H.%M.%S", time.localtime()), exc))

    def add_entries(self, table_name: str, values_dict: dict):
        """
        Создаём следующий по порядку столбец с указанными в value_dict данными
        ================================================================================
        :param table_name: название таблицы, в которую вставляем
        :param values_dict: словарь, содержащий название столбца
        и начальные данные.
        """
        # try:
        with self.connection.cursor() as cursor:
            columns, values = ', '.join(list(values_dict.keys())), \
                              ', '.join(self.convert_digits_to_string(list(values_dict.values())))
            parentheses = '{}, ' * (values.count(',') + 1)
            query = " 'INSERT INTO " + table_name + "(" + columns + ") VALUES(" + parentheses + ")'.format({})"\
                .format(self.cover_with_braces(self.cover_with_braces(values, braces_type="'")))
            query = eval(query.replace(', )', ')'))

            cursor.execute(query)
        # except Exception as exc:
        #     self.connection.rollback()
        #     print('Дата: {0}\nОШИБКА:{1}'.format(time.strftime("%d.%m.%Y - %H.%M.%S", time.localtime()), exc))

    def get_entry(self, table_name: str, required_values: list, where_condition: dict = None):
        """
        Позволяет получить 1(одну) запись, исходя из введённых параметров
        и/или условий WHERE
        ================================================================================
        :param table_name: название таблицы с нужными значениями
        :param required_values: список строковых значений названий
        необходимый для извлечения столбцов
        :param where_condition: опционально, если требуется выборка
        по конкретным параметрам
        :return: возвращает result - list of tuples со значениями
        из базы данных, расположенными по порядку, вида:
        [('1', 'Name', '0'), ('2', 'Dima', '228')]
        ================================================================================

        """
        cursor = self.connection.cursor()
        result = ''
        # try:
        query = 'SELECT {0} FROM {1}'\
            .format(', '.join(required_values), table_name)
        query += " WHERE " + " AND ".join(self.convert_dict_to_string(where_condition, "=").split(", ")) \
            if where_condition else ""

        cursor.execute(query)
        # except Exception as exc:
        #     cursor.close()
        #     print('Дата: {0}\nОШИБКА:{1}'.format(time.strftime("%d.%m.%Y - %H.%M.%S", time.localtime()), exc))
        # else:
        result = cursor.fetchall()
        cursor.close()
        return result \
            if not self.check_for_hidden_list_sequence(result) \
            else self.convert_strange_str_to_list(result, '#&%')

    def get_all_entries(self, table_name: str, where_condition: dict = None):
        """
        Возвращает все записи при специфическом user_id
        БЕЗ СПЕЦИФИКАЦИИ ОТДАСТ ВСЮ ТАБЛИЦУ, ОСТОРОЖНО!
        ================================================================================
        :param table_name: название таблицы
        :param where_condition: опционально; если необходимы все записи
        по конкретноым условиям
        :return: возвращает result -  list кортежей со значениями
        из базы данных, расположенными по порядку
        ================================================================================
        !NOTE
        user_id спорный частный параметр, лучше специфицировать
        условия иначе через WHERE
        """
        cursor = self.connection.cursor()
        result = ''
        # try:
        query = 'SELECT * FROM ' + table_name
        query += " WHERE " + " AND ".join(self.convert_dict_to_string(where_condition, "=").split(", ")) \
            if where_condition else ""

        cursor.execute(query)
        # except Exception as exc:
        #     cursor.close()
        #     print('Дата: {0}\nОШИБКА:{1}'.format(time.strftime("%d.%m.%Y - %H.%M.%S", time.localtime()), exc))
        # else:
        result = cursor.fetchall()
        cursor.close()
        return result \
            if not self.check_for_hidden_list_sequence(result) \
            else self.convert_strange_str_to_list(result, '#&%')

    def update_entries(self, table_name: str, user_id: str, values_dict: dict,
                       update_type='rewrite', separator='|'):
        """
        Обновляет запись одним из возможных способов
        ================================================================================
        :param table_name: название таблицы, в которой обновляем
        :param user_id: порядковый ID человека в БД
        :param values_dict: Словарь значений следующего вида:
        {'название поля': 'новое значение'}
        :param update_type: Применяемый тип обновления записи; применяется для всех
        переданных в values_dict значений.
        > rewrite - DEFAULT - заменить старое значение в ячейке на новое
        > add - прибавить новое значение к старому (для числовых данных)
        > concat - соединить существующую строку с новой,
        возможно с использованием разделителя
        :param separator: разделитель строк, используемый при
        обновлении типа concat
        """
        # try:
        with self.connection.cursor() as cursor:
            exist_entry = self.get_entry(table_name, list(values_dict.keys()),
                                         where_condition={'request_id': user_id})
            # !!! ЗАМЕНИТЬ user_id на where_condition !!!
            if not exist_entry:
                raise psycopg2.DataError('Запись не существует.')
            else:
                if update_type == 'rewrite':
                    result_dict = values_dict.copy()
                else:  # поступившим данным присваиваются ключи запрошенных
                    exist_entry_dict = {list(values_dict.keys())[i]: exist_entry[0][i]
                                        for i in range(len(values_dict.keys()))}

                    if update_type == 'add':  # складываем словари с одинаковыми ключами
                        result_dict = self.add_dicts(values_dict, exist_entry_dict)
                    elif update_type == 'concat':
                        # складываем существующую строку и новую, +- разделитель
                        result_dict = {
                            key: str(exist_entry_dict[key]) + separator + str(values_dict[key])
                            for key in values_dict.keys()
                        }

                query = "UPDATE " + table_name + \
                        " SET " + self.convert_dict_to_string(result_dict, separator=' = ') + \
                        " WHERE request_id = '" + user_id + "'"
                # !!! ЗАМЕНИТЬ user_id на
                # " AND ".join(self.convert_dict_to_string(where_condition, "=").split(", ")) !!!
                cursor.execute(query)
        # except Exception as exc:
        #     self.connection.rollback()
        #     print('Дата: {0}\nОШИБКА:{1}'.format(time.strftime("%d.%m.%Y - %H.%M.%S", time.localtime()), exc))

    def delete_entry(self, table_name: str, columns_dict: dict):
        """
        Удалить 1(одну) запись.
        ================================================================================
        :param table_name: название таблицы
        :param columns_dict: словарь с парой столбец : запись из удаляемая строка,
        то есть удалена будет строка, в стобце которой есть такая запись
        """
        # try:
        with self.connection.cursor() as cursor:
            query = 'DELETE FROM {0} WHERE {1}'\
                .format(table_name, self.convert_dict_to_string(columns_dict, separator='='))

            cursor.execute(query)
        # except Exception as exc:
        #     self.connection.rollback()
        #     print('Дата: {0}\nОШИБКА:{1}'.format(time.strftime("%d.%m.%Y - %H.%M.%S", time.localtime()), exc))

    def drop_table(self, table_name: str):
        """
        Функция УДАЛЯЕТ таблицу. Вообще. Полностью
        ================================================================================
        :param table_name: название УДАЛЯЕМОЙ таблицы
        """
        # try:
        with self.connection.cursor() as cursor:
            query = 'DROP TABLE ' + table_name
            cursor.execute(query)
        # except Exception as exc:
        #     self.connection.rollback()
        #     print('Дата: {0}\nОШИБКА:{1}'.format(time.strftime("%d.%m.%Y - %H.%M.%S", time.localtime()), exc))
        # else:
        print('Операция очистки таблицы завершена, информация помечена как пригодная для перезаписи.')

    def execute_any_query(self, query: str):
        """
        Позволяет запустить любой запрос.
        ~~~ ! Расширить функционал ! ~~~
        ================================================================================
        :param query: строка, содержащая полный запрос
        ================================================================================
        !НИ В КОЕМ СЛУЧАЕ НЕ ПОДАВАТЬ СТРОКУ, КОТОРАЯ МОЖЕТ СОДЕРЖАТЬ ДАННЫЕ,
        ВВЕДЁННЫЕ ПОЛЬЗОВАТЕЛЕМ!
        """
        # try:
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            if 'select' in query.lower():
                result = cursor.fetchall()
                return result
        # except Exception as exc:
        #     self.connection.rollback()
        #     print('Дата: {0}\nОШИБКА:{1}'.format(time.strftime("%d.%m.%Y - %H.%M.%S", time.localtime()), exc))


def basic_functionality_test(host, user, password, dbname, port='5432'):
    print('================================================================================'
          '\nTest has been started.\n'
          '================================================================================')
    db_obj = DatabaseManager(host=host, user=user, password=password,
                             port=port, dbname=dbname)
    db_obj.create_table('users',
                        {'user_id': 'serial primary',
                         'StringTest': "str DEFAULT 'дефолт string'", 'IntTest': 'int DEFAULT 0',
                         'FloatTest': 'float', 'BoolTest': 'bool'
                         })
    db_obj.add_entries('users',
                       {'FloatTest': 3.14, 'BoolTest': True
                        })
    db_obj.add_entries('users',
                       {'StringTest': 'Dima', 'IntTest': 17, 'FloatTest': 13.37,
                        'BoolTest': False
                        })
    print(db_obj.get_entry('users', ['StringTest', 'IntTest']))
    print(db_obj.get_all_entries('users'))
    print(db_obj.get_all_entries('users'))
    db_obj.update_entries('users', '2', {'IntTest': 228282}, update_type='rewrite')
    db_obj.update_entries('users', '2', {'FloatTest': 12.21}, update_type='add')
    db_obj.update_entries('users', '2', {'StringTest': 'concat this'}, update_type='concat')
    db_obj.update_entries('users', '2', {'BoolTest': True}, update_type='rewrite')
    print(db_obj.get_all_entries('users'))
    db_obj.delete_entry('users', {'user_id': '1'})
    print(db_obj.get_all_entries('users'))
    db_obj.drop_table('users')
    print('================================================================================'
          '\nTest has been canceled.\n'
          '================================================================================')


def main():
    # answer = input('Запустить тест базового функционала?\n')
    # if answer.lower() in ['да', 'запуск', 'запустить', '1']:
    #     host, user, password, dbname =
    #     input('Введите host, имя, пароль и название БД, разделяя их пробелами\n').split()
    #     basic_functionality_test(host, user, password, dbname)
    user_data_sosha = dict(host='localhost', user='shagonru', password='13082000',
                           dbname='programmer_simulator', port='5432')
    
    # user_data_dima = dict(host='localhost', user='', password='',
    #                        dbname='programmer_simulator', port='5432')
    
    basic_functionality_test(*user_data_sosha.values())


if __name__ == '__main__':
    main()
