# coding: utf-8
from __future__ import unicode_literals
import random, json
import database_module

Named = False

#В хэндлере мы записываем путь по разделам, который прокладывает пользователь, начиная от основных разделов
handler = ""

def read_data():
    with open("words.json", encoding="utf-8") as file:
        data = json.loads(file.read())
        return data

def read_answers_data(name):
    with open(name+".json", encoding="utf-8") as file:
        data = json.loads(file.read())
        return data

aliceAnswers = read_answers_data("data/answers_dict_example")

def aliceSpeakMap(myAns,withAccent=False):
    if(withAccent): return  myAns.strip()
    else: return myAns.replace("+","").strip()

def map_answer(myAns,withAccent=False):
    if(withAccent): return  myAns.replace(".", "").replace(";","").strip()
    else: return myAns.replace(".", "").replace(";", "").replace("+","").strip()

#Ну вот эта функция всем функциям функция, ага. Замена постоянному формированию ответа, ага, экономит 4 строчки!!
def НуПридумаемНазваниеПотом(респунсь, юсер_стораждж, мэссаждж, буттоньсы, флажок = False):
    #ща будет магия
    if флажок:
        респунсь.set_text(aliceSpeakMap(мэссаждж))
        респунсь.set_tts(aliceSpeakMap(мэссаждж, True))
    else:
        респунсь.set_text(мэссаждж)
        респунсь.set_tts(мэссаждж)
    buttons, user_storage = get_suggests(юсер_стораждж)
    респунсь.set_buttons(буттоньсы)
    return респунсь, user_storage




def handle_dialog(request, response, user_storage, database):
    global Named, handler
    #request.command - сообщение от пользователя
    #!!handler = "ну вот тут ты забираешь хэндлер из бд, ага"
    input_message = request.command.lower().strip("?!.")
    #первый запуск/перезапуск диалога
    if request.is_new_session or "name" not in user_storage.keys() and not handler == "named_already":
        if request.is_new_session and not database.get_entry(request.user_id):
            output_message = "Приветствую, немеханический. Не получается стать программистом? " \
                      "Есть вопросы о нашей нелёгкой жизни? Запускай симулятор! " \
                      "#для продолжения необходимо пройти авторизацию, введите имя пользователя..."
            response.set_text(aliceSpeakMap(output_message))
            response.set_tts(aliceSpeakMap(output_message))
            handler = "asking name"
            return response, user_storage
        if handler == "asking name":
            Named = True
            user_storage["name"] = request.command
            database.add_user(request.user_id, user_storage["name"])
            database.update_score(request.user_id, 0)

        user_storage['suggests']= [
            "Начинаем",
            "Помощь"
        ]
        if not Named:
            output_message = random.choice(aliceAnswers["helloTextVariations"]).capitalize()+" Доступные команды: " \
                     + ", ".join(user_storage['suggests'])
        else:
            handler = "named_already"
            output_message = random.choice(aliceAnswers["continueTextVariations"]).capitalize()+" Доступные команды: " \
                     + ", ".join(user_storage['suggests'])

        buttons, user_storage = get_suggests(user_storage)
        return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, True)
        # Вот эти вот строчечки я оставил, чтобы, если оказался слишком туп и неправильно сделал ту самую функцию, можно было поправить
        # response.set_text(aliceSpeakMap(output_message))
        # response.set_tts(aliceSpeakMap(output_message,True))
        # response.set_buttons(buttons)
        # return response, user_storage

    #первая проверка после начала
    #!!Необходимо вынести подобную проверку в отдельную функцию для вызова в других разделах
    if handler.endswith("first_step_pass") or handler.endswith("named_already"):
        if input_message == "основная информация" or input_message == "информация":
            handler = "start_page"
        elif input_message == "помощь":
            handler = "help_page"
        elif input_message == "источник дохода" or input_message == "доход":
            handler = "profit_page"
        elif input_message == "образование и курсы" or input_message == "образование" or input_message == "курсы":
            handler = "education_page"
        elif input_message == "конфигурация рабочей системы" or input_message == "конфигурация":
            handler = "system_page"

    #условие на случай, если пользователь хендлером вышел из основных разделов
    if handler == "null":
        handler = "first_step_pass"
        user_storage['suggests'] = [
            "Основная информация",
            "Источник дохода",
            "Образование и курсы",
            "Конфигурация рабочей системы",
            "Помощь"
        ]

        output_message = "Похоже мы вернулись в начало. \n Доступные опции: {}".format(", ".join(user_storage['suggests']))

        buttons, user_storage = get_suggests(user_storage)
        return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons)

    #Основная стартовая страница с основными данными игрока(основной раздел data)
    if handler.startswith("start_page"):
        #start_page
        print(handler)
        if input_message == "назад":
            print(handler)
            splited = handler.split("->")
            if len(splited) > 1:
                handler = "->".join(splited[:-1])
            else:
                handler = "null"

        if handler == "start_page":
            money = "сюда вставить получение денег пользователя"
            exp = "сюда вставить получение опыта пользователя"
            food = "сюда вставить получение голода пользователя"
            mood = "сюда вставить получение настроения пользователя"
            health = "сюда вставить получение здоровья пользователя"
            date = "сюда вставить получение текущей даты пользователя"

            user_storage['suggests'] = [
                "Восполнение голода",
                "Восполнение здоровья",
                "Восполнение настроения",
                "Другие основные разделы",
                "Назад"
            ]

            handler += "->start_next"

            output_message = "Ваши деньги: {} \n Ваш накопленный опыт: {} \n Ваш голод: {} \n Ваше настроение: {}" \
                             " \n Ваше здоровье: {} Текущая дата: {} \n Доступные опции: {}".format(money, exp, food, mood,
                                    health, date, ", ".join(user_storage['suggests']))

            buttons, user_storage = get_suggests(user_storage)
            return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons)

        #start_page->start_next
        if handler.endswith("start_next"):
            if input_message == "восполнение голода":
                handler += "->food_recharge"
            elif input_message == "восполнение здоровья":
                handler += "->health_recharge"
            elif input_message == "восполнение настроения":
                handler += "->mood_recharge"
            elif input_message == "другие основные разделы":
                handler += "->other"

        #start_page->other
        if handler.endswith("other"):
            user_storage['suggests'] = [
                "Источник дохода",
                "Образование и курсы",
                "Конфигурация рабочей системы",
                "Помощь",
                "Назад"
            ]

            handler += "->other_next"

            output_message = "Доступные опции: {}".format(", ".join(user_storage['suggests']))

            buttons, user_storage = get_suggests(user_storage)
            return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons)

        #Возвращает хендлер к основному разделу
        #!!Необходимо вынести подобную проверку в отдельную функцию для вызова в других разделах
        if handler.endswith("other_next"):
            if input_message == "источник дохода" or input_message == "доход":
                handler = "profit_page"
            elif input_message == "образование и курсы" or input_message == "образование" or input_message == "курсы":
                handler = "education_page"
            elif input_message == "конфигурация рабочей системы" or input_message == "конфигурация":
                handler = "system_page"
        #!!Нужно сделать дальше другие основные разделы

        #start_page->start_next->food_recharge
        if handler.endswith("food_recharge"):
            food = "сюда вставить получение голода пользователя"

            user_storage['suggests'] = [
                "Наименование первого продукта/цена/процент восполнения",
                "Наименование второго продукта/цена/процент восполнения",
                "Наименование третьего продукта/цена/процент восполнения",
                "Наименование четвертого продукта/цена/процент восполнения",
                "Назад"
            ]

            handler += "->food_next"

            output_message = "Ваш голод: {} Доступные продукты: \n {}".format(food,
                            ",\n".join(user_storage['suggests'][:-1])+"\n Доступные опции: Назад")

            buttons, user_storage = get_suggests(user_storage)
            return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons)

        #start_page->start_next->food_recharge->food_next
        if handler.endswith("->food_next"):
            #!!Необходимо добавить в БД уровень игрока, который я потом буду подсчитывать, стартовый - первый.
            #!!Этот уровень и есть индекс, агааа.
            index = "1"
            product = ""
            food_list = read_answers_data("data/list")["food"][index]
            for i in food_list.keys():
                if i.lower().startswith(input_message):
                    product = i
                    product_price = food_list[i][0]
                    product_weight = food_list[i][1]

            if product:
                #!!Дальше мы проверяем, можем ли мы купить этот продукт, поэтому пока что тут просто будет очередной флажок
                flag = True
                #Потом возвращаем хендлером к предыдущему этапу
                handler = "->".join(handler.split("->")[:-1])
                if flag == True:
                    output_message = "Продукт {} успешно преобретен. \n Доступные продукты: {}".format(product,
                        ",\n".join(user_storage['suggests'][:-1]) + "\n Доступная команда: Назад")
                else:
                    output_message = "Продукт {} нельзя преобрести, нехватает денег. \n Доступные продукты:{} ".format(product,
                        ",\n".join(user_storage['suggests'][:-1]) + "\n Доступная команда: Назад")
            else:
                output_message = "Продукт {} не найден, повторите запрос".format(input_message)

            buttons, user_storage = get_suggests(user_storage)
            return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons)

        # start_page->start_next->food_recharge->health_recharge
        if handler.endswith("health_recharge"):
            health = "сюда вставить получение здоровья пользователя"

            user_storage['suggests'] = [
                "Наименование первого продукта/цена/процент восполнения",
                "Наименование второго продукта/цена/процент восполнения",
                "Наименование третьего продукта/цена/процент восполнения",
                "Наименование четвертого продукта/цена/процент восполнения",
                "Назад"
            ]

            handler += "->health_next"

            output_message = "Ваше здоровье {} \n Доступные методы восстановления здоровья: \n {}".format(health,
                ",\n".join(user_storage['suggests'][:-1])+ "\n Доступная команда: Назад")

            buttons, user_storage = get_suggests(user_storage)
            return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons)

        #start_page->start_next->food_recharge->health_next
        if handler.endswith("->health_next"):
            # !!Необходимо добавить в БД уровень игрока, который я потом буду подсчитывать, стартовый - первый.
            # !!Этот уровень и есть индекс, агааа.
            index = 1
            product = ""
            food_list = read_answers_data("data/list")["health"][index]
            for i in food_list.keys():
                if i.lower().startswith(input_message):
                    product = i
                    product_price = food_list[i][0]
                    product_weight = food_list[i][1]

            if product:
                # !!Дальше мы проверяем, можем ли мы купить этот продукт, поэтому пока что тут просто будет очередной флажок
                flag = True
                # Потом возвращаем хендлером к предыдущему этапу
                handler = "->".join(handler.split("->")[:-1])
                if flag == True:
                    output_message = "Метод {} успешно оплачен. \n Доступные методы восстановления здоровья: {}".format(product,
                        ",\n".join(user_storage['suggests'][:-1])+ "\n Доступная команда: Назад")
                else:
                    output_message = "Метод {} нельзя оплатить, нехватает денег. \n Доступные методы восстановления" \
                                     " здоровья: {}".format(product,
                        ",\n".join(user_storage['suggests'][:-1])+ "\n Доступная команда: Назад")
            else:
                output_message = "Метод {} не найден, повторите запрос. \n Доступные методы восстановления здоровья:" \
                                 " {}".format(input_message, ",\n".join(user_storage['suggests'][:-1])+ "\n Доступная команда: Назад")

            buttons, user_storage = get_suggests(user_storage)
            return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons)

        #start_page->start_next->food_recharge->mood_recharge
        if handler.endswith("mood_recharge"):
            mood = "сюда вставить получение здоровья пользователя"

            user_storage['suggests'] = [
                "Наименование первого продукта/цена/процент восполнения",
                "Наименование второго продукта/цена/процент восполнения",
                "Наименование третьего продукта/цена/процент восполнения",
                "Наименование четвертого продукта/цена/процент восполнения",
                "Назад"
            ]

            handler += "->mood_next"

            output_message = "Ваше настроение {} \n Доступные методы восстановления настроения: \n {}".format(mood,
                ",\n".join(user_storage['suggests'][:-1])+ "\n Доступная команда: Назад")

            buttons, user_storage = get_suggests(user_storage)
            return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons)

        # start_page->start_next->food_recharge->food_next
        if handler.endswith("->mood_next"):
            # !!Необходимо добавить в БД уровень игрока, который я потом буду подсчитывать, стартовый - первый.
            # !!Этот уровень и есть индекс, агааа.
            index = 1
            product = ""
            food_list = read_answers_data("data/list")["mood"][index]
            for i in food_list.keys():
                if i.lower().startswith(input_message):
                    product = i
                    product_price = food_list[i][0]
                    product_weight = food_list[i][1]

            if product:
                # !!Дальше мы проверяем, можем ли мы купить этот продукт, поэтому пока что тут просто будет очередной флажок
                flag = True
                # Потом возвращаем хендлером к предыдущему этапу
                handler = "->".join(handler.split("->")[:-1])
                if flag == True:
                    output_message = "Метод {} успешно оплачен. \n Доступные методы восстановления настроения: {}".format(product,
                        ",\n".join(user_storage['suggests'][:-1])+ "\n Доступная команда: Назад")
                else:
                    output_message = "Метод {} нельзя оплатить, нехватает денег. \n Доступные методы восстановления" \
                                     " настроения: {}".format(product,
                        ",\n".join(user_storage['suggests'][:-1])+ "\n Доступная команда: Назад")
            else:
                output_message = "Метод {} не найден, повторите запрос. \n Доступные методы восстановления здоровья:" \
                                 " {}".format(input_message, ",\n".join(user_storage['suggests'][:-1])+ "\n Доступная команда: Назад")

            buttons, user_storage = get_suggests(user_storage)
            return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons)



    if handler == "help_page":
        #Вот эти строчки отвечают за саджесты(кнопочкииии)
        buttons, user_storage = get_suggests(user_storage)
        response.set_buttons(buttons)
        user_storage['suggests'] = [
            "Основные механики",
            "Обратная связь",
        ]
        buttons, user_storage = get_suggests(user_storage)
        #Вот тут заканчиваются эти строчки и кнопочкииии
        output_message = 'Нужна помощь? Укажи нужный раздел! Доступные: ' + ", ".join(user_storage["suggests"])
        buttons, user_storage = get_suggests(user_storage)
        return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons)

    if input_message in ['обратная связь', 'связь'] and handler == "help":
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
        output_message = 'Для того, чтобы связаться с нами, стучите на адрес example@example.com, ваше мнение важно' \
                  ' для нас! Доступные разделы: ' + ", ".join(user_storage["suggests"])
        buttons, user_storage = get_suggests(user_storage)
        return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons)

    if input_message in ['механики', 'основные механики'] and handler == "help":
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
        output_message = 'Какая именно механика вас интересует? Реализованные(ХА-ХА-ХА, НЕТ) механики: ' + ", ".join(user_storage["suggests"])
        buttons, user_storage = get_suggests(user_storage)
        return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons)

    if input_message in ['механики', 'основные механики'] and handler == "help":
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
        output_message = 'Какая именно механика вас интересует? Реализованные(ХА-ХА-ХА, НЕТ) механики: ' + ", ".join(user_storage["suggests"])
        buttons, user_storage = get_suggests(user_storage)
        return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons)

    if input_message in ['время', 'время в игре'] and handler == "help":
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
        output_message = 'sample_text' + ", ".join(
            user_storage["suggests"])
        buttons, user_storage = get_suggests(user_storage)
        return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons)

    if input_message in ['нет', 'не хочется', 'в следующий раз', 'выход', "не хочу", 'выйти']:
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
