# coding: utf-8
import sqlite3
import os
import threading


class DatabaseManager:
    def __init__(self):
        if 'data' not in os.listdir('.'):
            os.mkdir('data')
        self.connection = sqlite3.connect("data/alisa_users.db", isolation_level=None)
        cursor = self.connection.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS users '
                       '(user_id INTEGER NOT NULL, email TEXT, score INTEGER)')
        # cursor.close()
        print(threading.current_thread(), 'init')
        # self.connection.commit()

    def __del__(self):
        print(threading.current_thread(), '__del__')
        self.connection.close()

    def add_user(self, user_id, email, score=0):
        print(threading.current_thread(), 'add_user')
        cursor = self.connection.cursor()
        try:
            if not self.get_entry(user_id):
                print('Пользователь {} добавлен.'.format(user_id))
                cursor.execute("""INSERT INTO users 
                                VALUES(:user_id, :email, :score)""", {
                    'user_id': user_id, 'email': email, 'score': score
                })
            else:
                print('Пользователь {} уже существует!'.format(user_id))
                cursor.close()
                return False
        except sqlite3.DatabaseError as error:
            print('Error: ', error)
        # else:
        #     self.connection.commit()
        cursor.close()
        return True

    def update_score(self, user_id, add_to_the_score):
        print(threading.current_thread(), 'update_score')
        cursor = self.connection.cursor()
        try:
            exist_entry = self.get_entry(user_id)
            if not exist_entry:
                print('Пользователь с номером {} не существует!'.format(user_id))
            else:
                print(exist_entry, 'else update_score')
                cursor.execute("""UPDATE users
                                SET user_id = :user_id, score = :score""",
                               {
                                   'user_id': user_id, 'score': exist_entry[0][2] + add_to_the_score,
                               })
        except sqlite3.DatabaseError as error:
            print('Error: ', error)
        # else:
        #     self.connection.commit()
        cursor.close()

    def delete_user(self, user_id):
        print(threading.current_thread(), 'delete_user')
        cursor = self.connection.cursor()
        try:
            exist_entry = self.get_entry(user_id)
            if not exist_entry:
                print('Пользователь с номером {} не существует!'.format(user_id))
            else:
                cursor.execute("""DELETE FROM users
                                WHERE user_id = :user_id""",
                               {
                                   'user_id': user_id
                               })
        except sqlite3.DatabaseError as error:
            print('Error: ', error)
        # else:
            # self.connection.commit()
        cursor.close()

    def get_entry(self,  user_id):
        print(threading.current_thread(), 'get_entry')
        cursor = self.connection.cursor()
        result = None
        try:
            cursor.execute("""SELECT * FROM users
                            WHERE user_id = :user_id""",
                           {
                               'user_id': user_id,
                           })
        except sqlite3.DatabaseError as error:
            print('Error: ', error)
        else:
            # self.connection.commit()
            result = cursor.fetchall()
        cursor.close()
        return result

    def get_all_entries(self):
        print(threading.current_thread(), 'get_all')
        cursor = self.connection.cursor()
        result = None
        try:
            cursor.execute("""SELECT * FROM users
                           """)
        except sqlite3.DatabaseError as error:
            print('Error: ', error)
        else:
            # self.connection.commit()
            result = cursor.fetchall()
        cursor.close()
        return result


def main():  # for tests only!
    base = DatabaseManager()
    base.update_score(1, 5)
    base.add_user(1, 'goshan.chamor@yandex.ru')
    print(base.get_entry(1))
    base.update_score(1, 2)
    base.add_user(3, 'dimalox@yandex.ru')
    base.add_user(3, 'dimalox@yandex.ru')
    print(base.get_entry(1))
    print(base.get_entry(3))
    base.add_user(3, 'dimalox@yandex.ru')
    base.add_user(24, 'testuser@mail.ru')
    print(base.get_entry(24))
    base.add_user(1, 'sas')
    print(base.get_all_entries())


if __name__ == '__main__':
    main()


def show_score(base, user_id):
    # base = DatabaseManager()
    # entry = [(1, 'goshan.chamor@yandex.ru', 21)]
    entry = base.get_entry(user_id)[0][1:3]
    #print('Счет пользователя {} равен {}.'.format(entry[0][1], entry[0][2]))
    return entry


def show_leaderboard(base, top_number):
    # base = DatabaseManager()
    entries = base.get_all_entries()
    if top_number > len(entries):
        top_number = len(entries)
    entries = sorted([entry[::-1] for entry in entries], reverse=True)
    lst = [{entries[i][1]:entries[i][0]} for i in range(top_number)]
    return lst
