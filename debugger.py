from main_function import *
<<<<<<< HEAD
import postgresql_database
=======

>>>>>>> f8348a1... Special for GeyOrgy(debug please)
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
                      {'user_id': "serial primary", "request_id": "str NOT NULL UNIQUE", "handler": "str DEFAULT 'null'",
<<<<<<< HEAD
                       "Name": "str DEFAULT 'null'", "Named": "bool DEFAULT False", "Experience": "int DEFAULT 0",
                       "Money": "int DEFAULT 1000", "Food": "int DEFAULT 70", "Exp": "int DEFAULT 0",
                       "Lvl": "str DEFAULT '1'", "Job": "str DEFAULT 'Безработный#$0#$0#$1'",
                       "Freelance": "str DEFAULT 'Безделие#$бесценный опыт о потери времени#$бесконечность'",
                       "Day": "int DEFAULT 0", "Credit": "str DEFAULT '0#$0#$0'",
                       "Deposit": "str DEFAULT '0#$1'", "Mood": "int DEFAULT 70",
                       "Health": "int DEFAULT 70", "Waste": "str DEFAULT '20#$5#$0#$0'",
                       "books": "str DEFAULT 'null'", "Day_changed": "bool DEFAULT False",
                       "Is_Dead": "bool DEFAULT False", "current_education": "str DEFAULT 'null'",
                       "education": "str DEFAULT 'null'", "current_course": "str DEFAULT 'null'",
                       "course": "str DEFAULT 'null'"})
=======
                       "Named": "bool DEFAULT False", "Experience": "int DEFAULT 0",
                       "Money": "int DEFAULT 1000", "Food": "int DEFAULT 100", "Exp": "int DEFAULT 0",
                       "Lvl": "str DEFAULT '0'", "Job": "str DEFAULT '0'",
                       "Freelance": "list DEFAULT '[zp#&%time#&%exp]'",
                       "credit" : "list DEFAULT '[index#&%money#&%time]'", "deposit" : "int DEFAULT 0",
                       "Mood": "int DEFAULT 100", "Health": "int DEFAULT 100", "Money_Waste": "int DEFAULT 0",
                       "Food_Waste": "int DEFAULT 20", "Mood_Waste": "int DEFAULT 20" })
>>>>>>> f8348a1... Special for GeyOrgy(debug please)
    return psdb



class DeRequest:
    def __init__(self, isNewSession, userID):
        self.is_new_session = isNewSession
        self.user_id = userID
        self.command = ""


class DeResponse:
    def __init__(self):
        self.text = ""
        self.tss = ""
        self.buttons = []
        self.end_session = False

    def set_text(self, text):
        self.text = text

    def set_tts(self, text):
        self.tss = text

    def set_buttons(self, buttons):
        self.buttons = buttons


def printResponce(response):
    print("Текст: " + response.text)
    print("Алиса говорит: " + response.tss)
    print("Кнопки:")
    for button in response.buttons:
        print("----")
        print("Текст: " + button["title"], "; Видно: " + "да" if button['hide'] else "нет")
    print("----")


def main():
    print("DE: Введите ID пользователя")
    id = input()
    stResponce = DeResponse()
    database = init_database(host='localhost', user='postgres', password='1488',
<<<<<<< HEAD
                             dbname='programmer_simulator')
=======
                           dbname='programmer_simulator')
>>>>>>> f8348a1... Special for GeyOrgy(debug please)
    responce, userStorage = handle_dialog(DeRequest(True, id), stResponce, {}, database)
    printResponce(responce)
    while True:
        res = input()
        if res == "/leave":
            quit("Произошёл /leave...")
        stResponce = DeResponse()
        mRequest = DeRequest(False, id)
        mRequest.command = res
        responce, userStorage = handle_dialog(mRequest, stResponce, userStorage, database)
        printResponce(stResponce)
        if stResponce.end_session:
            quit("Выход из навыка")


if __name__ == '__main__':
    main()

