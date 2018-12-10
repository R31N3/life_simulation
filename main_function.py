# coding: utf-8
from __future__ import unicode_literals
import random, json
import database_module

Named = False
handler = ""

def read_data():
    with open("words.json", encoding="utf-8") as file:
        data = json.loads(file.read())
        return data

def read_answers_data():
    with open("answers_dict_example.json", encoding="utf-8") as file:
        data = json.loads(file.read())
        return data

aliceAnswers = read_answers_data()

def aliceSpeakMap(myAns,withAccent=False):
    if(withAccent): return  myAns.strip()
    else: return myAns.replace("+","").strip()

def map_answer(myAns,withAccent=False):
    if(withAccent): return  myAns.replace(".", "").replace(";","").strip()
    else: return myAns.replace(".", "").replace(";", "").replace("+","").strip()


def handle_dialog(request, response, user_storage, database):
    global Named, handler
    if request.is_new_session or "name" not in user_storage.keys():
        if request.is_new_session and not database.get_entry(request.user_id):
            message = "Приветствую, немеханический. Не получается стать программистом? " \
                      "Есть вопросы о нашей нелёгкой жизни? Запускай симулятор! " \
                      "#для продолжения необходимо пройти авторизацию, введите имя пользователя..."
            response.set_text(aliceSpeakMap(message))
            response.set_tts(aliceSpeakMap(message))
            handler = "asking name"
            return response, user_storage
        if handler == "asking name":
            Named = True
            user_storage["name"] = request.command
            database.add_user(request.user_id, user_storage["name"])
            database.update_score(request.user_id, 0)

        buttons, user_storage = get_suggests(user_storage)
        response.set_buttons(buttons)
        user_storage['suggests']= [
            "Помощь"
        ]
        buttons, user_storage = get_suggests(user_storage)
        if not Named:
            choice = random.choice(aliceAnswers["helloTextVariations"]).capitalize()+" Доступные команды: " \
                     + ", ".join(user_storage['suggests'])
        else:
            choice = random.choice(aliceAnswers["continueTextVariations"]).capitalize()+" Доступные команды: " \
                     + ", ".join(user_storage['suggests'])
        response.set_text(aliceSpeakMap(choice))
        response.set_tts(aliceSpeakMap(choice,True))
        response.set_buttons(buttons)
        return response, user_storage


    if request.command.lower().strip("?!.") in ['помощь', 'что ты умеешь', 'что за симулятор']:
        #Вот эти строчки отвечают за саджесты(кнопочкииии)
        buttons, user_storage = get_suggests(user_storage)
        response.set_buttons(buttons)
        user_storage['suggests'] = [
            "Основные механики",
            "Обратная связь",
        ]
        handler = "help"
        buttons, user_storage = get_suggests(user_storage)
        #Вот тут заканчиваются эти строчки и кнопочкииии
        message = 'Нужна помощь? Укажи нужный раздел! Доступные: ' + ", ".join(user_storage["suggests"])
        response.set_text(message)
        response.set_tts(message)
        buttons, user_storage = get_suggests(user_storage)
        response.set_buttons(buttons)
        return response, user_storage

    if request.command.lower().strip("?!.") in ['обратная связь', 'связь'] and handler == "help":
        # Вот эти строчки отвечают за саджесты(кнопочкииии)
        buttons, user_storage = get_suggests(user_storage)
        response.set_buttons(buttons)
        user_storage['suggests'] = [
            "Основные механики",
            "Обратная связь",
        ]
        handler = "help"
        buttons, user_storage = get_suggests(user_storage)
        # Вот тут заканчиваются эти строчки и кнопочкииии
        # Ха-ха-ха
        message = 'Для того, чтобы связаться с нами, стучите на адрес example@example.com, ваше мнение важно' \
                  ' для нас! Доступные разделы: ' + ", ".join(user_storage["suggests"])
        response.set_text(message)
        response.set_tts(message)
        buttons, user_storage = get_suggests(user_storage)
        response.set_buttons(buttons)
        return response, user_storage

    if request.command.lower().strip("?!.") in ['механики', 'основные механики'] and handler == "help":
        # Вот эти строчки отвечают за саджесты(кнопочкииии)
        buttons, user_storage = get_suggests(user_storage)
        response.set_buttons(buttons)
        user_storage['suggests'] = [
            "Время в игре"
        ]
        handler = "mechanics"
        buttons, user_storage = get_suggests(user_storage)
        # Вот тут заканчиваются эти строчки и кнопочкииии
        # Ха-ха-ха
        message = 'Какая именно механика вас интересует? Реализованные(ХА-ХА-ХА, НЕТ) механики: ' + ", ".join(user_storage["suggests"])
        response.set_text(message)
        response.set_tts(message)
        buttons, user_storage = get_suggests(user_storage)
        response.set_buttons(buttons)
        return response, user_storage

    if request.command.lower().strip("?!.") in ['механики', 'основные механики'] and handler == "help":
        # Вот эти строчки отвечают за саджесты(кнопочкииии)
        buttons, user_storage = get_suggests(user_storage)
        response.set_buttons(buttons)
        user_storage['suggests'] = [
            "Время в игре"
        ]
        handler = "mechanics"
        buttons, user_storage = get_suggests(user_storage)
        # Вот тут заканчиваются эти строчки и кнопочкииии
        # Ха-ха-ха
        message = 'Какая именно механика вас интересует? Реализованные(ХА-ХА-ХА, НЕТ) механики: ' + ", ".join(user_storage["suggests"])
        response.set_text(message)
        response.set_tts(message)
        buttons, user_storage = get_suggests(user_storage)
        response.set_buttons(buttons)
        return response, user_storage

    if request.command.lower().strip("?!.") in ['механики', 'основные механики'] and handler == "help":
        # Вот эти строчки отвечают за саджесты(кнопочкииии)
        buttons, user_storage = get_suggests(user_storage)
        response.set_buttons(buttons)
        user_storage['suggests'] = [
            "К началу",
            "Обратно к помощи"
        ]
        handler = "mechanics"
        buttons, user_storage = get_suggests(user_storage)
        # Вот тут заканчиваются эти строчки и кнопочкииии
        # Ха-ха-ха
        message = 'sample_text' + ", ".join(
            user_storage["suggests"])
        response.set_text(message)
        response.set_tts(message)
        buttons, user_storage = get_suggests(user_storage)
        response.set_buttons(buttons)
        return response, user_storage

    if request.command.lower().strip("?!.") in ['нет', 'не хочется', 'в следующий раз', 'выход', "не хочу", 'выйти']:
        answered = True
        choice = random.choice(aliceAnswers["quitTextVariations"])
        response.set_text(aliceSpeakMap(choice))
        response.set_tts(aliceSpeakMap(choice,True))
        response.end_session = True
        return response, user_storage

    choice = random.choice(aliceAnswers["cantTranslate"])
    response.set_text(aliceSpeakMap(choice))
    response.set_tts(aliceSpeakMap(choice, True))
    buttons, user_storage = get_suggests(user_storage)
    response.set_buttons(buttons)
    return response, user_storage


def get_suggests(user_storage):
    if "suggests" in user_storage.keys():
        suggests = [
            {'title': suggest, 'hide': True}
            for suggest in user_storage['suggests']
        ]
    else:
        suggests = []

    return suggests, user_storage
