# -*- coding: utf-8 -*-

import threading
import psycopg2
import os
import time


class DatabaseManager:
    def __init__(self, host, user, password, dbname, port='5432'):
        """
        :param host: database server address e.g., localhost or an IP address
        :param user: the username used to authenticate.
        :param password: password used to authenticate.
        :param dbname: the name of the database that you want to connect.
        :param port: the port number that defaults to 5432 if it is not provided.
        """
        if 'data' not in os.listdir('.'):
            os.mkdir('data')

        server_params = {'host': host, 'user': user, 'password': password,
                         'port': port, 'database': dbname}
        '''               host='localhost', user='shagonru', password='13082000,'
                          port='5432', dbname='programmer_simulator'          '''
        self.connection = psycopg2.connect(**server_params)
        print(threading.current_thread(), '__init__')

    def __del__(self):
        print(threading.current_thread(), '__del__')
        self.connection.close()

    @staticmethod
    def check_sql_injection(str_for_check: str) -> str:
        """
        :param str_for_check: строка для проверки на SQL-синтаксис
        :return: строку, если всё хорошо; предупреждение, если плохо
        =================================================================
        !!! будет сделано в ближайшее никогда !!!
        """
        some_code = 'some_code' + str_for_check
        return some_code

    @staticmethod
    def convert_type(non_converted_type: str) -> str:
        """
        :param non_converted_type: строка с названием типа в python
        :return: строка с типом, пригодным для SQL
        """
        converted_type = ''
        types_dict = {'str': 'TEXT', 'int': 'INTEGER', 'float': 'REAL', 'bytes': 'BYTEA', 'bool': 'BOOLEAN'}

        if non_converted_type.split()[0].upper() in types_dict.values():
            converted_type += non_converted_type.split()[0].upper()
        else:
            converted_type += types_dict[non_converted_type.split()[0]]

        if 'primary' in non_converted_type.lower():
            converted_type += ' PRIMARY KEY'

        return converted_type

    @staticmethod
    def convert_dict_to_string(non_converted_dict: dict, separator=' ') -> str:
        """
        Превращает словарь в строку, которую можно использовать
        для конкатенации в SQL-запросах
        =================================================================
        :param non_converted_dict: словарь со значениями
        :param separator: разделитель, стоящий между бывших словарных пар
        :return: строку, преобразованную по образцу
        =================================================================
        Пример:
        было:  {'user_id': *значение1*, 'score': *значение2*}
        стало: 'user_id = *значение1*, score = *значение2*'
        при значении sep = ' = '
        """
        converted_string = ''
        count = 0
        dict_len = non_converted_dict.__len__()
        for item in non_converted_dict.items():
            count += 1
            comma = ',' if count < dict_len else ''
            if len(item) > 1:
                converted_string += item[0] + separator + item[1] + comma
        return converted_string

    @staticmethod
    def convert_digits_to_string(iterable_obj):
        return [str(item) for item in iterable_obj]

    @staticmethod
    def add_dicts(*dicts):
        """
        :param dicts: любое количество словарей
        :return: результат их сложения типа dict
        """
        from collections import Counter
        result_dict = Counter()
        for dictionary in dicts:
            result_dict += Counter(dictionary)
        return dict(result_dict)

    def create_table(self, table_name: str, columns: dict):
        """
        :param table_name: название создаваемой таблицы; Английский
        :param columns: словарь, содержащий название столбца
        и его тип. Пример: {'score': 'int', 'username':'text'}
        value может содержать указатель primary, тогда при
        конвертации к ключу будет добавлено ключевое слово
        PRIMARY KEY для однозначной идентификации
        =================================================================
        Запрос имеет SQL-синтаксис вида
        CREATE TABLE IF NOT EXISTS *название_таблицы*
        (user_id = *значение1*, score = *значение2*)
        """
        columns = {key: self.convert_type(value) for key, value in columns.items()}
        try:
            with self.connection.cursor() as cursor:
                cursor.execute('CREATE TABLE IF NOT EXISTS ' + table_name +
                               '(' + self.convert_dict_to_string(columns) + ')'
                               )
        except Exception as exc:
            print('ОШИБКА: ', exc, '\nДата: ', time.strftime("%H.%M.%S - %d.%m.%Y", time.localtime()))

    def add_entries(self, table_name, values_dict):
        """
        :param table_name: название таблицы, в которую вставляем
        :param values_dict: словарь, содержащий название столбца
        и начальные данные. Подробнее смотрите в: create_table
        """
        # try:
        with self.connection.cursor() as cursor:
            print(list(values_dict.keys()), list(values_dict.values()))
            columns, values = ', '.join(list(values_dict.keys())), \
                              ', '.join(self.convert_digits_to_string(list(values_dict.values())))
            query = 'INSERT INTO ' + table_name + '(' + columns + ')' +\
                    'VALUES(' + '%s'*len(values) + ')'

            cursor.execute(query, values)
        # except Exception as exc:
        #     print('ОШИБКА: ', exc, '\nДата: ', time.strftime("%H.%M.%S - %d.%m.%Y", time.localtime()))

    def get_entry(self, table_name: str, required_values: list, user_id=''):
        """
        :param table_name: название таблицы с нужными значениями
        :param required_values: список строковых значений названий
        необходимый для извлечения столбцов
        :param user_id: опционально, если требуется выборка
        по конкретному пользователю
        :return: возвращает result -  list кортежей со значениями
        из базы данных, расположенными по порядку
        =================================================================
        !NOTE
        user_id спорный параметр т.к. является частным случаем,
        возможна переделка под нормальный специфический поиск
        для любых других категорий для большей гибкости;
        тогда необходимо указать переменную where и уже в ней
        хранить строку необходимых условий поиска
        """
        cursor = self.connection.cursor()
        result = ''
        try:
            query = 'SELECT' + ', '.join(required_values) \
                    + 'FROM' + table_name
            query += 'WHERE user_id=' + user_id if user_id else ''

            cursor.execute(query)
        except Exception as exc:
            cursor.close()
            print('ОШИБКА: ', exc, '\nДата: ', time.strftime("%H.%M.%S - %d.%m.%Y", time.localtime()))
        else:
            result = cursor.fetchall()
            cursor.close()
        return result

    def get_all_entries(self, table_name, user_id=''):
        """
        Возвращает все записи при специфическом user_id
        БЕЗ СПЕЦИФИКАЦИИ ОТДАСТ ВСЮ ТАБЛИЦУ, ОСТОРОЖНО!
        =================================================================
        :param table_name: название таблицы
        :param user_id: опционально; если необходимы все
        записи по конкретному пользователю
        :return: возвращает result -  list кортежей со значениями
        из базы данных, расположенными по порядку
        =================================================================
        !NOTE
        user_id спорный частный параметр, лучше специфицировать
        условия иначе через WHERE
        """
        cursor = self.connection.cursor()
        result = ''
        try:
            query = 'SELECT * FROM ' + table_name
            query += 'WHERE user_id=' + user_id if user_id else ''

            cursor.execute(query)
        except Exception as exc:
            cursor.close()
            print('ОШИБКА: ', exc, '\nДата: ', time.strftime("%H.%M.%S - %d.%m.%Y", time.localtime()))
        else:
            result = cursor.fetchall()
            cursor.close()
        return result

    def update_entries(self, table_name: str, user_id: str, values_dict: dict,
                       update_type='rewrite', separator='|'):
        """
        :param table_name: название таблицы, в которой обновляем
        :param user_id: порядковый ID человека в БД
        :param values_dict: Словарь значений следующего вида:
        {'название поля': 'новое значение'}
        :param update_type: Применяемый тип обновления записи;
        применяется для всех переданных в values_dict значений.
        > rewrite - DEFAULT - заменить старое значение в ячейке на новое
        > add - прибавить новое значение к старому (для числовых данных)
        > concat - соединить существующую строку с новой,
        возможно с использованием разделителя
        :param separator: разделитель строк, используемый при
        обновлении типа concat
        """
        try:
            with self.connection.cursor() as cursor:
                exist_entry = self.get_entry(table_name, list(values_dict.keys()), user_id=user_id)
                if not exist_entry:
                    raise psycopg2.DataError('Запись не существует.')
                else:
                    if update_type == 'rewrite':
                        res_dict = values_dict.copy()
                    else:
                        exist_entry_dict = {list(values_dict.keys())[i]: exist_entry[0][i + 1]
                                            for i in range(len(values_dict.keys()))}

                        if update_type == 'add':
                            res_dict = self.add_dicts(values_dict, exist_entry_dict)
                        elif update_type == 'concat':
                            res_dict = {key: str(exist_entry_dict[key]) + separator + str(values_dict[key])
                                        for key in values_dict.keys()}

                    query = 'UPDATE' + table_name + \
                            'SET' + self.convert_dict_to_string(res_dict, separator='=') + \
                            'WHERE user_id = ' + user_id
                    cursor.execute(query)
        except Exception as exc:
            print('ОШИБКА: ', exc, '\nДата: ', time.strftime("%H.%M.%S - %d.%m.%Y", time.localtime()))

    def delete_entry(self, table_name: str, columns_dict: dict):
        try:
            with self.connection.cursor() as cursor:
                query = 'DELETE FROM ' + table_name + \
                        'WHERE' + self.convert_dict_to_string(columns_dict, separator='=') + ')'

                cursor.execute(query)
        except Exception as exc:
            print('ОШИБКА: ', exc, '\nДата: ', time.strftime("%H.%M.%S - %d.%m.%Y", time.localtime()))

    def drop_table(self, table_name):
        """
        Функция УДАЛЯЕТ таблицу. Вообще. Полностью
        :param table_name: название УДАЛЯЕМОЙ таблицы
        """
        try:
            with self.connection.cursor() as cursor:
                query = 'DROP TABLE' + table_name
                cursor.execute(query)
        except Exception as exc:
            print('ОШИБКА: ', exc, '\nДата: ', time.strftime("%H.%M.%S - %d.%m.%Y", time.localtime()))


def basic_functionality_test():
    db_obj = DatabaseManager(host='localhost', user='shagonru', password='13082000',
                             port='5432', dbname='programmer_simulator')
    db_obj.create_table('users',
                        {'StringTest': 'str', 'IntTest': 'int', 'FloatTest': 'float',
                         'BoolTest': 'bool', 'ByteTest': 'bytes',
                         'ListStrTest': 'str'
                         })
    db_obj.add_entries('users',
                       {'StringTest': 'strings wow', 'IntTest': 1, 'FloatTest': 3.14,
                        'BoolTest': True, 'ByteTest': b'bytes',
                        'ListStrTest': 'maybe its a list'
                        })
    db_obj.add_entries('users',
                       {'StringTest': 'Dima', 'IntTest': 17, 'FloatTest': 13.37,
                        'BoolTest': False, 'ByteTest': b'still bytes',
                        'ListStrTest': 'maybe not'
                        })
    print(db_obj.get_entry('users', ['StringTest', 'IntTest', 'FloatTest']))
    print(db_obj.get_all_entries('users'))
    print(db_obj.get_all_entries('users', user_id='2'))
    db_obj.update_entries('users', '2', {'IntTest': 228282}, update_type='rewrite')
    db_obj.update_entries('users', '2', {'FloatTest': 12.21}, update_type='add')
    db_obj.update_entries('users', '2', {'StrTest': 'concat that to previous entry'}, update_type='concat')
    print(db_obj.get_all_entries('users'))
    db_obj.delete_entry('users', {'user_id': '1'})
    print(db_obj.get_all_entries('users'))
    print('========================================\nTest had been canceled.')


def main():
    # answer = input('Запустить тест базового функционала?\n')
    # if answer.lower() in ['да', 'запуск', 'запустить', '1']:
    #     basic_functionality_test()
    basic_functionality_test()


if __name__ == '__main__':
    main()
