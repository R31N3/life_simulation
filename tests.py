import postgresql_database
#
user_data_sosha = dict(host='localhost', user='shagonru', password='13082000',
                        dbname='programmer_simulator', port='5432')
#
# if 'data' not in __import__('os').listdir('.'):
#     __import__('os').mkdir('data')  # очень плохой импорт!
#
# # у меня testspace
# # CREATE TABLESPACE dbspace LOCATION '/home/shagonru/PycharmProjects/life_simulation/data';
# # CREATE TABLE something (......) TABLESPACE dbspace;
# # CREATE TABLE otherthing (......) TABLESPACE dbspace;
#
# psdb = postgresql_database.DatabaseManager(*user_data_sosha.values())
# # psdb.execute_any_query("CREATE TABLESPACE testspace LOCATION '/home/shagonru/PycharmProjects/life_simulation/data'")
# psdb.execute_any_query('CREATE TABLE IF NOT EXISTS testtable(StringCol TEXT, IntCol INT) TABLESPACE testspace')
# # psdb.create_table('testtable', {'StringCol': 'str', 'IntCol': 'int'})
# psdb.add_entries('testtable', {'StringCol': 'entry string type'})
# res = psdb.execute_any_query("SELECT pg_relation_filepath('testtable')")
#
# print(res)

# psdb = postgresql_database.DatabaseManager(*user_data_sosha.values())
#
# psdb.create_table('test_table_1', {"user_id": "serial primary", "StringTest": "str default 'StringTest str default'",
#                                    "IntTest": "int default 10", 'BoolTest': 'bool',
#                                    "UniqueStrTest": "str unique not null "})
#
# psdb.add_entries('test_table_1', {"StringTest": "entry 1 non default",
#                                   "IntTest": 111, 'BoolTest': False,
#                                   "UniqueStrTest": "thats unique!"})
#
# psdb.add_entries('test_table_1', {"UniqueStrTest": "2 all entries default but this is unqie and not null"})
#
# psdb.add_entries('test_table_1', {"StringTest": "entry 3",
#                                   "IntTest": 333, 'BoolTest': False,
#                                   "UniqueStrTest": "thats not unique!"})
# print(psdb.get_all_entries('test_table_1'))
# psdb.__del__()
# print('del был')
# __import__('time').sleep(2)
# psdb1 = postgresql_database.DatabaseManager(*user_data_sosha.values())
# print(psdb1.get_all_entries('test_table_1'))
#
# a = 2
# b = 2
# c = 1 if a > b else -1
# d = 1 if a > b else -1 if a < b else 0
# print(c, d)
# #    -1  0

ses = [('money', 'exp', 'food')]
print(*ses)
money, exp, food = ses[0]
print(money, exp, food)
