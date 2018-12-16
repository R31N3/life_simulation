# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals

# Импортируем модули для работы с логами.
import logging

# Импортируем модуль для работы с API Алисы
from alice_sdk import AliceRequest, AliceResponse

# Импортируем модуль с логикой игры
from function_example import handle_dialog

# Импортируем модуль работы с базами данных
import postgresql_database

# Импортируем модуль грамматического анализа
import pymorphy2

# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request
app = Flask(__name__)


# Хранилище данных о сессиях.
session_storage = {}

logging.basicConfig(level=logging.DEBUG)


def init_database(host, user, password, dbname):
    psdb = postgresql_database.DatabaseManager(host, user, password, dbname)
    psdb.create_table('users_info',
                      {'handler': 'string', 'Named': 'bool', 'Experience': 'int', 'Money': 'int', 'Food': 'int',
                       'Mood': 'int', 'Health': 'int', 'Money_Waste': 'int', 'Food_Waste': 'int', 'Mood_Waste': 'int',
                       'Health_Waste': 'int', 'Date': 'str', 'CPU': 'str', 'RAM': 'str', 'Disk': 'str', 'VRAM': 'str',
                       'Monitor': 'str', 'LAN': 'str', 'Operation_System': 'str', 'Antivirus': 'str',
                       'Programmes': 'list', 'Education': 'list', 'Courses': 'list', 'Books': 'list', 'Job': 'str',
                       'Second_Job': 'list', 'Bank': 'list', 'Vehicle': 'str', 'Business': 'str', 'Events': 'list'})
    return psdb


@app.route("/alice_hackaton/ping")
def mainn():
    return "pong"


# Задаем параметры приложения Flask.
@app.route("/alice_hackaton/", methods=['POST'])
def main():
    morph = pymorphy2.MorphAnalyzer()
    database = init_database('localhost', 'shagonru', '13082000', 'programmer_simulator')

    # Функция получает тело запроса и возвращает ответ.
    alice_request = AliceRequest(request.json)
    logging.info('Request: {}'.format(alice_request))

    alice_response = AliceResponse(alice_request)

    user_id = alice_request.user_id
    print(user_id)
    print(session_storage.get(user_id))
    print(len(session_storage))
    alice_response, session_storage[user_id] = handle_dialog(
        alice_request, alice_response, session_storage.get(user_id), database, morph.parse('очко')[0]
    )

    logging.info('Response: {}'.format(alice_response))

    return alice_response.dumps()


if __name__ == '__main__':
    app.run()
