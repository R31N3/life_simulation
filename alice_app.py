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
    """
    =================================================================
    Значения по умолчанию подавать по следующему шаблону:
    'column_name': "type DEFAULT value", где value в зависомости от
    типа ДОЛЖНО принимать следующие значения:
    INTEGER -> 0; REAL -> 0.00; TEXT -> 'text here'; BOOLEAN -> True;
    list -> '[entry1#&% запись2 #&% "3"]' - ТОЛЬКО ТАК на вход
    И угадывайте как хотите, лист чего нам пришёл, туплей или нет,
    тех или не тех. УДОБНО, ДА? Как просили, так и сделали.
    =================================================================
    """
    psdb = postgresql_database.DatabaseManager(host, user, password, dbname)
    psdb.create_table("users_info",
                      {"handler": "string DEFAULT ''", "Named": "bool DEFAULT False", "Experience": "int DEFAULT 0",
                       "Money": "int DEFAULT 1000", "Food": "int DEFAULT 100",
                       "Mood": "int DEFAULT 100", "Health": "int DEFAULT 100", "Money_Waste": "int DEFAULT 0",
                       "Food_Waste": "int DEFAULT 20", "Mood_Waste": "int DEFAULT 20",
                       "Health_Waste": "int DEFAULT 0", "Date": "str DEFAULT '01.01.1970'",
                       "CPU": "str DEFAULT 'Pentagnome 1488'", "RAM": "str DEFAULT '10MB'",
                       "Disk": "str DEFAULT '10GB'", "VRAM": "str", "Monitor": "str DEFAULT 'MONITORCHEK'",
                       "LAN": "str DEFAULT '10kbps'", "Operation_System": "str DEFAULT 'SHINDOWS'",
                       "Antivirus": "str DEFAULT 'Cashpersky'", "Programmes": "list", "Education": "list",
                       "Courses": "list", "Books": "list", "Job": "str", "Second_Job": "list", "credit": "list",
                       "Vehicle": "str DEFAULT 'kostyleped'", "Business": "str DEFAULT ''", "Events": "list"})
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
