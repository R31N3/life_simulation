# coding: utf-8
from __future__ import unicode_literals
import random
import json

Named = False

def find_difference(lst1, lst2):
    return [i for i in lst1 if i not in lst2]


def read_data():
    with open("words.json", encoding="utf-8") as file:
        data = json.loads(file.read())
        return data


def read_answers_data(name):
    with open(name+".json", encoding="utf-8") as file:
        data = json.loads(file.read())
        return data


aliceAnswers = read_answers_data("data/answers_dict_example")


def aliceSpeakMap(myAns, withAccent=False):
    if withAccent:
        return myAns.strip()
    return myAns.replace("+", "").strip()


def map_answer(myAns, withAccent=False):
    if withAccent:
        return myAns.replace(".", "").replace(";", "").strip()
    return myAns.replace(".", "").replace(";", "").replace("+", "").strip()

def update_handler(handler, database, request):
    database.update_entries('users_info', request.user_id, {'handler': handler}, update_type='rewrite')
    

def ЯНичегоНеПонял(response, user_storage, buttons = ""):
    мэссаждж = random.choice(aliceAnswers["cantTranslate"])
    response.set_text(aliceSpeakMap(мэссаждж))
    response.set_tts(aliceSpeakMap(мэссаждж, True))
    buttons, user_storage = get_suggests(user_storage)
    response.set_buttons(buttons)
    return response, user_storage

# Ну вот эта функция всем функциям функция, ага. Замена постоянному формированию ответа, ага, экономит 4 строчки!!
def НуПридумаемНазваниеПотом(response, user_storage, мэссаждж, буттоньсы, database, request, handler, флажок=False):
    # ща будет магия
    update_handler(handler, database, request)
    текст_муссаждж = мэссаждж.split("Доступные")[0] if "Доступные" in мэссаждж  and "Подработка" not in мэссаждж and "задолжность" not in мэссаждж else мэссаждж
    if флажок:
        response.set_text(aliceSpeakMap(текст_муссаждж))
        response.set_tts(aliceSpeakMap(мэссаждж, True))
    else:
        response.set_text(текст_муссаждж)
        response.set_tts(мэссаждж)
    buttons, user_storage = get_suggests(user_storage)
    response.set_buttons(буттоньсы)
    return response, user_storage


def handle_dialog(request, response, user_storage, database):
    # request.command - сообщение от пользователя
    input_message = request.command.lower().strip("?!.")
    # первый запуск/перезапуск диалога
    if request.is_new_session or not database.get_entry("users_info",  ['Named'], {'request_id': request.user_id})[0][0]:
        print(database.get_entry("users_info", ['Name'], {'request_id': request.user_id}) == 'null')
        if request.is_new_session and (database.get_entry("users_info", ['Name'],
                                                          {'request_id': request.user_id}) == 'null'
                                       or not database.get_entry("users_info", ['Name'], {'request_id': request.user_id})):
            output_message = "Приветствую, немеханический. Не получается стать программистом? " \
                      "Есть вопросы о нашей нелёгкой жизни? Запускай симулятор! " \
                      "#для продолжения необходимо пройти авторизацию, введите имя пользователя..."
            response.set_text(aliceSpeakMap(output_message))
            response.set_tts(aliceSpeakMap(output_message))
            database.add_entries("users_info", {"request_id": request.user_id})
            print(database.get_entry("users_info",  ['Named']))
            handler = "asking name"
            update_handler(handler, database, request)
            return response, user_storage
        handler = database.get_entry("users_info", ['handler'], {'request_id': request.user_id})[0][0]
        print(handler)
        if handler == "asking name":
            print(request.user_id)
            database.update_entries('users_info', request.user_id, {'Named': True}, update_type='rewrite')
            user_storage["name"] = request.command
            database.update_entries('users_info', request.user_id, {'Name': input_message}, update_type='rewrite')

        user_storage['suggests'] = [
            "Основная информация",
            "Источник дохода",
            "Образование и курсы",
            "Конфигурация рабочей системы",
            "Помощь"
        ]

        Named = database.get_entry("users_info", ['Named'], {'request_id': request.user_id})[0][0]

        if not Named:
            output_message = random.choice(aliceAnswers["helloTextVariations"]).capitalize()+" Доступные разделы: " \
                     + ", ".join(user_storage['suggests'])
        else:
            output_message = random.choice(aliceAnswers["continueTextVariations"]).capitalize()+" Доступные разделы: " \
                     + ", ".join(user_storage['suggests'])
        handler = "other_next"
        buttons, user_storage = get_suggests(user_storage)
        return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler, True)

    handler = database.get_entry("users_info", ['handler'], {'request_id': request.user_id})[0][0]
    # Возвращает хендлер к основному разделу
    # !! Необходимо вынести подобную проверку в отдельную функцию для вызова в других разделах
    if handler.endswith("other_next"):
        if input_message == "источник дохода" or input_message == "доход":
            handler = "profit_page"
        elif input_message == "образование и курсы" or input_message == "образование" or input_message == "курсы":
            handler = "education_page"
        elif input_message == "конфигурация рабочей системы" or input_message == "конфигурация":
            handler = "system_page"
        elif input_message == "общая информация" or input_message == "информация":
            handler = "start_page"

    # Основная стартовая страница с основными данными игрока(основной раздел data)
    if handler.startswith("start_page"):
        # start_page
        if input_message == "назад" and not handler.endswith("job"):
            splitted = handler.split("->")
            if handler.endswith("next"):
                handler = "->".join(splitted[:-3])
            else:
                if len(splitted) > 1:
                    handler = "->".join(splitted[:-2])
                else:
                    handler = "null"
            handler = "null" if not handler else handler

        # !! Необходимо вынести в отдельную фунцию.
        if handler.endswith("other") or handler == "null":
            user_storage['suggests'] = [
                "Основная информация",
                "Источник дохода",
                "Образование и курсы",
                "Конфигурация рабочей системы",
                "Помощь"
            ]

            handler = "other->other_next"

            output_message = "Похоже мы вернулись в начало. \n Доступные опции: {}".format(
                ", ".join(user_storage['suggests']))

            buttons, user_storage = get_suggests(user_storage)
            return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

        if handler == "start_page":
            money = database.get_entry("users_info", ['Money'], {'request_id': request.user_id})[0][0]
            exp = database.get_entry("users_info", ['Exp'], {'request_id': request.user_id})[0][0]
            food = database.get_entry("users_info", ['Food'], {'request_id': request.user_id})[0][0]
            mood = database.get_entry("users_info", ['Mood'], {'request_id': request.user_id})[0][0]
            health = database.get_entry("users_info", ['Health'], {'request_id': request.user_id})[0][0]
            date = database.get_entry("users_info", ['Day'], {'request_id': request.user_id})[0][0]

            user_storage['suggests'] = [
                "Восполнение голода",
                "Восполнение здоровья",
                "Восполнение настроения",
                "Назад"
            ]

            handler += "->start_next"

            output_message = "Ваши деньги: {} \n Ваш накопленный опыт: {} \n Ваш голод: {} \n Ваше настроение: {}" \
                             " \n Ваше здоровье: {} \n Дней с начала игры прошло: {} \n Доступные опции: {}"\
                .format(money, exp, food, mood, health, date, ", ".join(user_storage['suggests']))

            buttons, user_storage = get_suggests(user_storage)
            return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

        # start_page -> start_next
        if handler.endswith("start_next"):
            if input_message == "восполнение голода" or input_message == "голод":
                handler += "->food_recharge"
            elif input_message == "восполнение здоровья" or input_message == "здоровье":
                handler += "->health_recharge"
            elif input_message == "восполнение настроения" or input_message == "настроение":
                handler += "->mood_recharge"

        if handler.count("food"):
            # start_page -> start_next -> food_recharge
            if handler.endswith("food_recharge"):
                food = database.get_entry("users_info", ['Food'], {'request_id': request.user_id})[0][0]
                index = database.get_entry("users_info", ['Lvl'], {'request_id': request.user_id})[0][0]
                food_list = read_answers_data("data/start_page_list")["food"][index]
                user_storage['suggests'] = [i + " цена {} восполнение {}".format(food_list[i][0], food_list[i][1]) for i in
                                            food_list.keys()]+["Назад"]
                handler += "->next"

                output_message = "Ваш голод: {} \n Список продуктов: \n {}"\
                    .format(food, ",\n".join(user_storage['suggests'][:-1])
                            + "\n Доступные опции: Назад")

                buttons, user_storage = get_suggests(user_storage)
                return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

            # start_page -> start_next -> food_recharge -> food_next
            if handler.endswith("next"):
                # !! Необходимо добавить в БД уровень игрока, который я потом буду подсчитывать, стартовый - первый.
                # !! Этот уровень и есть индекс, агааа.
                food = database.get_entry("users_info", ['Food'], {'request_id': request.user_id})[0][0]
                if food != 100:
                    index = database.get_entry("users_info", ['Lvl'], {'request_id': request.user_id})[0][0]
                    money = database.get_entry("users_info", ['Money'], {'request_id': request.user_id})[0][0]
                    product = ""
                    product_price = 0
                    product_weight = 0
                    food_list = read_answers_data("data/start_page_list")["food"][index]
                    for i in food_list.keys():
                        if i.lower().startswith(input_message):
                            product = i
                            product_price = food_list[i][0]
                            product_weight = food_list[i][1]

                    if product:
                        # !! Дальше мы проверяем, можем ли мы купить этот продукт,
                        # поэтому пока что тут просто будет очередной флажок
                        if money - product_price >= 0:
                            food = food + product_weight if (food + product_weight) % 100 and (food + product_weight)\
                                                            < 100  else 100
                            database.update_entries('users_info', request.user_id, {'Food': food},
                                                    update_type='rewrite')
                            database.update_entries('users_info', request.user_id, {'Money': money - product_price},
                                                    update_type='rewrite')
                            output_message = "Продукт {} успешно преобретен.\nВаш голод: {} \n Ваши финансы: {} \n Список продуктов: \n {}"\
                                .format(product, food, money - product_price, ",\n".join(user_storage['suggests'][:-1]) + "\n Доступные команды: Назад")
                        else:
                            output_message = "Продукт {} нельзя преобрести, нехватает денег: {} \nВаш голод: {} \n Ваши финансы: {} \n Список продуктов: \n{} "\
                                .format(product, product_price - money, food, money, ",\n".join(user_storage['suggests'][:-1]) + "\n Доступные команды: Назад")
                    else:
                        output_message = "Продукт {} не найден, повторите запрос \n Ваш голод: {} \n Ваши финансы: {}".format(input_message, food, money)
                else:
                    output_message = "Вы не голодный. \n  Список продуктов: \n {} Доступные команды: Назад".format(
                        ",\n".join(user_storage['suggests'][:-1])
                    )

                buttons, user_storage = get_suggests(user_storage)
                return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

        if handler.count("health"):
            # start_page -> start_next -> food_recharge -> health_recharge
            if handler.endswith("health_recharge"):
                health = database.get_entry("users_info", ['Health'], {'request_id': request.user_id})[0][0]
                index = database.get_entry("users_info", ['Lvl'], {'request_id': request.user_id})[0][0]
                health_list = read_answers_data("data/start_page_list")["health"][index]
                user_storage['suggests'] = \
                    [i + " цена {} восполнение {}".format(health_list[i][0], health_list[i][1]) for i in
                     health_list.keys()] + ["Назад"]

                handler += "->next"

                output_message = "Ваше здоровье {} \n Список доступных методов восстановления здоровья: \n {}"\
                    .format(health, ",\n".join(user_storage['suggests'][:-1])+ "\n Доступные команды: Назад")

                buttons, user_storage = get_suggests(user_storage)
                return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

            # start_page -> start_next -> food_recharge -> health_next
            if handler.endswith("next"):
                # !! Необходимо добавить в БД уровень игрока, который я потом буду подсчитывать, стартовый - первый.
                # !! Этот уровень и есть индекс, агааа.
                product = ""
                product_price = 0
                product_weight = 0
                health = database.get_entry("users_info", ['Health'], {'request_id': request.user_id})[0][0]
                if health != 100:
                    index = database.get_entry("users_info", ['Lvl'], {'request_id': request.user_id})[0][0]
                    health_list = read_answers_data("data/start_page_list")["health"][index]
                    for i in health_list.keys():
                        if i.lower().startswith(input_message):
                            product = i
                            product_price = health_list[i][0]
                            product_weight = health_list[i][1]

                    if product:
                        money = database.get_entry("users_info", ['Money'], {'request_id': request.user_id})[0][0]
                        if money - product_price:
                            health = health + product_weight if (health + product_weight) % 100 and (
                                    health + product_weight) < 100 else 100
                            database.update_entries('users_info', request.user_id, {'Health': health},
                                                    update_type='rewrite')
                            database.update_entries('users_info', request.user_id, {'Money': money - product_price},
                                                    update_type='rewrite')
                            output_message = "Метод {} успешно оплачен. \n Ваше здоровье: {} \n Ваши финансы: {}" \
                                             " \n Список доступных методов восстановления здоровья: {}"\
                                .format(product, health,money - product_price, ",\n".join(user_storage['suggests'][:-1])+ "\n Доступные команды: Назад")
                        else:
                            output_message = "Метод {} нельзя оплатить, нехватает денег: {} \n Ваше здоровье: {} \n" \
                                             "Ваши финансы: {} \nСписок доступных методов восстановления здоровья:\n{}"\
                                .format(product, product_price - money, health, money,
                                        ",\n".join(user_storage['suggests'][:-1]) + "\n Доступные команды: Назад")
                    else:
                        output_message = "Метод {} не найден, повторите запрос. \n Ваше здоровье: {} \n Список доступных методов восстановления здоровья:" \
                                         " \n {}".format(input_message, health, ",\n".join(user_storage['suggests'][:-1])
                                                      + "\n Доступные команды: Назад")
                else:
                    output_message = "Вы полностью здоровы. \n Список доступных методов восстановления здоровья:" \
                                         " {} Доступные команды: Назад".format(",\n".join(user_storage['suggests'][:-1]))

                buttons, user_storage = get_suggests(user_storage)
                return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

        if handler.count("mood"):
            # start_page -> start_next -> food_recharge -> mood_recharge
            if handler.endswith("mood_recharge"):
                mood = database.get_entry("users_info", ['Mood'], {'request_id': request.user_id})[0][0]
                index = database.get_entry("users_info", ['Lvl'], {'request_id': request.user_id})[0][0]
                mood_list = read_answers_data("data/start_page_list")["mood"][index]
                user_storage['suggests'] = [i+" цена {} восполнение {}".format(mood_list[i][0], mood_list[i][1]) for i in mood_list.keys()]

                handler += "->next"

                output_message = "Ваше настроение {} \n Список доступных методов восстановления настроения: \n {}"\
                    .format(mood, ",\n".join(user_storage['suggests'][:-1])+ "\n Доступные команды: Назад")

                buttons, user_storage = get_suggests(user_storage)
                return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

            # start_page -> start_next -> food_recharge -> food_next
            if handler.endswith("next"):
                # !! Необходимо добавить в БД уровень игрока, который я потом буду подсчитывать, стартовый - первый.
                # !! Этот уровень и есть индекс, агааа.
                mood = database.get_entry("users_info", ['Mood'], {'request_id': request.user_id})[0][0]
                if mood != 100:
                    index = database.get_entry("users_info", ['Lvl'], {'request_id': request.user_id})[0][0]
                    product = ""
                    product_price = 0
                    product_weight = 0
                    mood_list = read_answers_data("data/start_page_list")["mood"][index]
                    for i in mood_list.keys():
                        if i.lower().startswith(input_message):
                            product = i
                            product_price = mood_list[i][0]
                            product_weight = mood_list[i][1]

                    if product:
                        # !! Дальше мы проверяем, можем ли мы купить этот продукт,
                        # поэтому пока что тут просто будет очередной флажок
                        money = database.get_entry("users_info", ['Money'], {'request_id': request.user_id})[0][0]
                        if money - product_price >= 0:
                            mood = mood + product_weight if (mood + product_weight) % 100 and (
                                    mood + product_weight) < 100 else 100
                            database.update_entries('users_info', request.user_id, {'Mood': mood},
                                                    update_type='rewrite')
                            database.update_entries('users_info', request.user_id, {'Money': money - product_price},
                                                    update_type='rewrite')
                            output_message = "Метод {} успешно оплачен. \n Ваш настроение: {} \n Ваши финансы: {} \n Список доступных методов восстановления настроения: \n {}"\
                                .format(product, mood, money - product_price, ",\n".join(user_storage['suggests'][:-1])+ "\n Доступные команды: Назад")
                        else:
                            output_message = "Метод {} нельзя оплатить, нехватает денег: {}\n Ваш настроение: {} \n Ваши финансы: {} \n Список доступных методов восстановления" \
                                             " \n настроения: {}".format(product, product_price - money, mood, money, ",\n".join(user_storage['suggests'][:-1])
                                                                      + "\n Доступные команды: Назад")
                    else:
                        output_message = "Метод {} не найден, повторите запрос. \nВаш настроение: {} \n  Список доступных методов восстановления здоровья:" \
                                         " \n {}".format(input_message, mood, ",\n".join(user_storage['suggests'][:-1])
                                                      + "\n Доступные команды: Назад")
                else:
                    output_message = "У вас прекрасное настроение. \n Список доступных методов восстановления здоровья:" \
                                     " \n {} Доступные команды: Назад".format(",\n".join(user_storage['suggests'][:-1]))

                buttons, user_storage = get_suggests(user_storage)
                return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

        buttons, user_storage = get_suggests(user_storage)
        return ЯНичегоНеПонял(response, user_storage)

    if handler.startswith("profit_page"):
        if input_message == "назад" and not handler.endswith("job"):
            splitted = handler.split("->")
            if handler.endswith("next"):
                handler = "->".join(splitted[:-3])
            else:
                if len(splitted) > 1:
                    handler = "->".join(splitted[:-2])
                else:
                    handler = "null"
            handler = "null" if not handler else handler

        # !! Необходимо вынести в отдельную фунцию.
        if handler.endswith("other") or handler == "null":
            user_storage['suggests'] = [
                "Основная информация",
                "Источник дохода",
                "Образование и курсы",
                "Конфигурация рабочей системы",
                "Помощь"
            ]

            handler = "other->other_next"

            output_message = "Похоже мы вернулись в начало. \n Доступные опции: {}".format(
                ", ".join(user_storage['suggests']))

            buttons, user_storage = get_suggests(user_storage)
            return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

        if handler == "profit_page":
            job = database.get_entry("users_info", ['Job'], {'request_id': request.user_id})[0][0].split("#$")
            freelance = database.get_entry("users_info", ['Freelance'], {'request_id': request.user_id})[0][0].split("#$")
            bank = (database.get_entry("users_info", ['Credit'], {'request_id': request.user_id})[0][0].split("#$"),
                    database.get_entry("users_info", ['Deposit'], {'request_id': request.user_id})[0][0].split("#$"))
            print(job, 1, freelance, 2, bank)
            # business = database.get_entry("users_info", ['Business'], {'request_id': request.user_id})[0][0]

            user_storage['suggests'] = [
                "Работа",
                "Фриланс",
                "Банк",
                "Назад"
            ]

            handler += "->profit_next"

            output_message = "Ваши работа: {} Заработок: {}р \n Ваша фрилансерская деятельность: {} Время выполнения: {}" \
                             " Получаемая прибыль: {} \n Информация о деньгах в банке" \
                             " : \n Задолжность по кредиту: {} Процентная ставка: {} Срок выплаты: {}\n Сумма вклада: {} Процент по" \
                             " вкладу: {}\n Доступные команды: {}"\
                .format(job[0], job[1], freelance[0], freelance[2], freelance[1], bank[0][1], bank[0][2], bank[0][3],
                        bank[1][1], bank[1][2], ", ".join(user_storage['suggests']))

            buttons, user_storage = get_suggests(user_storage)
            return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

        if handler.endswith("profit_next"):
            if input_message == "работа":
                handler += "->job"
            elif input_message == "фриланс":
                handler += "->freelance"
            elif input_message == "банк":
                handler += "->bank"
            elif input_message == "бизнес":
                handler += "->business"

        if handler.count("job"):
            if handler.endswith("job"):
                job = database.get_entry("users_info", ['Job'], {'request_id': request.user_id})[0][0].split("#$")
                job_list = read_answers_data("data/profit_page_list")["job"]
                keys = sorted(job_list.keys())
                job_index = 0
                for i in keys:
                    if job[0] in job_list[i]:
                        job_index = i
                        break
                user_storage['suggests'] = ["Назад"]
                # Если у нас не максимально возможная ЗП, выдаем список вакансий длиной максимум до 10
                if int(job_index) != len(keys):
                    border = len(keys[int(job_index):]) % 10 if len(keys[int(job_index):]) % 10 != 0 else 10
                    handler += "->next"
                    lst = ["Текущая: {} Зарплата: {}".format(job_list[job_index][0], job_list[job_index][1])]
                    print(lst)
                    lst += keys[int(job_index) + 1:border + 1]
                    print(lst[1:], lst)
                    output_message = "Список вакансий: \n{} \n{} \nВыберите желаемую.  \nДоступные команды: Назад"\
                        .format(lst[0],
                                "\n".join(["{} Зарплата: {}".format(job_list[i][0], job_list[i][1]) for i in lst[1:]]))
                else:
                    output_message = "Текущая: {} Зарплата: {} \n Вы слишком умны, для вас работы больше пока не" \
                                     " придумали\n Доступные команды: Назад"\
                        .format(job_list[job_index][0], job_list[job_index][1])

                buttons, user_storage = get_suggests(user_storage)
                return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

            if handler.endswith("next"):
                job = database.get_entry("users_info", ['Job'], {'request_id': request.user_id})[0][0].split("#$")
                user_storage['suggests'] = ["Назад"]
                handler = "->".join(handler.split("->")[:-1])
                output_message = ""
                # !! Вот сюда засунуть нужно образование игрока
                user_requirements = database.get_entry("users_info",
                                            ['user_requirements'], {'request_id': request.user_id})[0][0].split("#$")
                job_list = read_answers_data("data/profit_page_list")["job"]
                keys = sorted(job_list.keys())
                job_index = 0
                for i in keys:
                    if job[0] in job_list[i]:
                        job_index = i
                        break
                if int(job_index) != len(keys):
                    if not input_message in job_list[job_index][0].lower():
                        border = len(keys[int(job_index):]) % 10 if len(keys[int(job_index):]) % 10 != 0 else 10
                        for i in keys[int(job_index):border + 1]:
                            if input_message in job_list[i][0].lower():
                                difference = [j for j in job_list[i][2] if j not in user_requirements]
                                if not difference:
                                    # !! Тут мы меняем работу на новую, если у нас совпадают все требования
                                    job_index = i
                                    job = "{}#${}".format(job_list[job_index][0], job_list[job_index][1])
                                    database.update_entries('users_info', request.user_id, {'Job': job},
                                                            update_type='rewrite')
                                    output_message = "Вы успешно повысились до {}. Доступные команды: Назад"\
                                        .format(job_list[job_index][0])
                                else:
                                    output_message = "Повышение невозможно, нехватает следующего: {}. Доступные команды: Назад"\
                                        .format(", ".join(difference))
                                break
                    else:
                        output_message = "В данный момент вы здесь уже работаете. Доступные команды: Назад"
                else:
                    output_message = "Текущая: {} Зарплата: {} \n Вы слишком умны, для вас работы больше пока не" \
                                     " придумали\n Доступные команды: Назад"
                if output_message:
                    buttons, user_storage = get_suggests(user_storage)
                    return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

        if handler.count("freelance"):
            if handler.endswith("freelance"):
                # !! Вот тут нужно сделать получение нынешней подработки из БД в переменную ниже
                current_freelance = database.get_entry("users_info", ['Freelance'],
                                                       {'request_id': request.user_id})[0][0].split("#$")
                user_storage['suggests'] = ["Назад"]
                if current_freelance[0] == "Безделие":
                    output_message = "В данный момент ваш род занятий: {} Получаемый доход: {} Время выполнения: {}\n"\
                        .format(current_freelance[0], current_freelance[1], current_freelance[2])
                    # !! Это снова тот индекс(уровень игрока, да).
                    index = database.get_entry("users_info", ['Lvl'],
                                                       {'request_id': request.user_id})[0][0]
                    freelance_list = read_answers_data("data/profit_page_list")["freelance"][index]
                    user_storage['suggests'] += [i for i in freelance_list.keys()]
                    handler += "->next"
                    lst = ["{}. Получаемый доход: {}. Время выполнения: {}."
                               .format(i, freelance_list[i][0], freelance_list[i][2])
                           for i in freelance_list.keys()]
                    output_message += "Список доступных подработок: \n {}\n " \
                                     "Выберите желаемую.  \n Доступные команды: Назад".format("\n".join(lst))
                else:
                    output_message = "В данный момент вы заняты {}, подождите {}, тогда вы сможете взять новое задание."\
                        .format(current_freelance[0], current_freelance[2])

                buttons, user_storage = get_suggests(user_storage)
                return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

            if handler.endswith("next"):
                # !! Это снова тот индекс(уровень игрока, да).
                index = database.get_entry("users_info", ['Lvl'],
                                           {'request_id': request.user_id})[0][0]
                current_freelance = database.get_entry("users_info", ['Freelance'],
                                                       {'request_id': request.user_id})[0][0].split("#$")
                user_storage['suggests'] = ["Назад"]
                if current_freelance[0] == "Безделие":
                    freelance_list = read_answers_data("data/profit_page_list")["freelance"][index]
                    lst = ["{} Оплата: {} Время выполнения {}"
                               .format(i, freelance_list[i][0], freelance_list[i][1]) for i in freelance_list.keys()]
                    for i in freelance_list.keys():
                        print(input_message, i)
                        if input_message in i.lower():
                            # !! Вот тут нужно сделать внесение новой подработки в БД из переменной ниже
                            user_requirements = database.get_entry("users_info",
                                                                   ['user_requirements'],
                                                                   {'request_id': request.user_id})[0][0].split("#$")
                            difference = [j for j in freelance_list[i][3] if j not in user_requirements]
                            if not difference:
                                current_freelance = [i, freelance_list[i][0], freelance_list[i][1]]
                                print(current_freelance)
                                output_message = "Подработка {} успешно взята на исполение. Оплата: {} Время выполнения" \
                                                 " {} Доступные команды: Назад".format(i, current_freelance[1], current_freelance[2])
                                database.update_entries('users_info', request.user_id, {'Freelance': "#$".join(current_freelance)},
                                                        update_type='rewrite')
                            else:
                                output_message = "Взятие данной подработки на исполнение невозможно," \
                                                 " нехватает следующего: {}. Доступные команды: Назад" \
                                    .format(", ".join(difference))
                            break
                    else:
                        user_storage['suggests'] = [i for i in freelance_list.keys()] + ["Назад"]
                        output_message = "Подработка {} не найдена. Выберите одну из доступных: \n {} \n Доступные команды: Назад"\
                            .format(input_message, "\n".join(lst))
                else:
                    output_message = "В данный момент вы заняты {}, подождите {}, тогда вы сможете взять новое задание." \
                        .format(current_freelance[0], current_freelance[1])
                buttons, user_storage = get_suggests(user_storage)
                return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

            return ЯНичегоНеПонял(response, user_storage)

        if handler.count("bank"):
            if handler.endswith("bank"):
                handler += "->next"
                money = database.get_entry("users_info", ['Money'], {'request_id': request.user_id})[0][0]
                credit, deposit = database.get_entry("users_info", ['Credit'],
                                                     {'request_id': request.user_id})[0][0].split("#$"),\
                                  database.get_entry("users_info", ['Deposit'],
                                                     {'request_id': request.user_id})[0][0].split("#$")
                credit[1] = int(credit[1])
                deposit[1] = int(deposit[1])
                index = database.get_entry("users_info", ['Lvl'],
                                           {'request_id': request.user_id})[0][0]
                available_credit = read_answers_data("data/profit_page_list")["credit"][index]\
                    if credit[1] == "0" \
                    else "Выдача нового кредита в данный момент недоступна, так как имеется задолжность"
                if available_credit.__class__ == list:
                    available_credit = "Выдаваемая сумма: {} Процентная ставка: {} Срок выдачи: {}".format(
                        available_credit[0], available_credit[1], available_credit[2])
                user_storage['suggests'] = [i for i in [
                    "Внести деньги на счет",
                    "Погасить задолжность по кредиту" if credit[1] != 0  else "",
                    "Взять деньги со счета" if deposit[1] != 0 else "",
                    "Взять кредит" if credit[1] == 0 else "",
                    "Назад"
                ] if i]
                output_message = "Наличные: {}р \n Информация о деньгах в банке" \
                             " : \n Задолжность по кредиту: {} Процентная ставка: {} Срок выплаты: {}\n Сумма вклада: {}" \
                                 " Процент по вкладу: {} \n Доступный кредит: {}\n Доступные команды: {}".format(
                    money, credit[1], credit[2], credit[3],
                        deposit[1], deposit[2], available_credit, "\n".join(user_storage["suggests"]))

                buttons, user_storage = get_suggests(user_storage)
                return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

            if handler.endswith("next"):
                if (input_message == "внести деньги на счет" or "внести" in input_message or "на счет" in input_message) and "не " not in input_message:
                    handler += "->money_deposit"
                elif (input_message == "погасить задолжность по кредиту" or "задолжность" in input_message or "по кредиту" in input_message or "погасить" in input_message) and "не " not in input_message:
                    handler += "->repayment"
                elif (input_message == "взять деньги со счета" or "деньги с" in input_message or  "со счета" in input_message or "взять деньги" in input_message) and "не " not in input_message :
                    handler += "->money_take"
                elif  "взять кредит" in input_message or "получить кредит" in input_message:
                    handler += "->credit"

            if handler.count("money_deposit"):
                if handler.endswith("money_deposit"):
                    money = database.get_entry("users_info", ['Money'], {'request_id': request.user_id})[0][0]
                    handler += "->next"
                    user_storage['suggests'] = ["Назад"]
                    deposit = database.get_entry("users_info", ['Deposit'],
                                                     {'request_id': request.user_id})[0][0].split("#$")
                    deposit[1] = int(deposit[1])
                    output_message = "Имеющаяся сумма у вас на руках: {}р \n Сумма во вкладе: {}р Процент по вкладу: {}% \n" \
                                     " Введите сумму, которую вы хотели бы внести на счет. \n Доступные команды: Назад".format(
                        money, deposit[1], deposit[2]
                    )
                    buttons, user_storage = get_suggests(user_storage)
                    return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

                if handler.endswith("next"):
                    user_storage['suggests'] = ["Назад"]
                    try:
                        money = database.get_entry("users_info", ['Money'], {'request_id': request.user_id})[0][0]
                        if int(input_message) <= money:
                            deposit = database.get_entry("users_info", ['Deposit'],
                                                         {'request_id': request.user_id})[0][0].split("#$")
                            deposit[1] = str(int(deposit[1])+int(input_message))
                            database.update_entries('users_info', request.user_id, {'Money': money-int(input_message)},
                                                    update_type='rewrite')
                            database.update_entries('users_info', request.user_id, {'Deposit': "#$".join(deposit)},
                                                    update_type='rewrite')
                            output_message = "Ваш вклад увеличился и теперь составляет {}р. \n Оставшиеся деньги у вас на руках: {}р Доступные команды: Назад".format(
                                deposit[1], money-int(input_message)
                            )
                        else:
                            output_message = "У вас недостаточно денег для внесения, нехватает {}р. Доступные команды: Назад".format(int(input_message)-money)
                    except TypeError:
                        output_message = "{} не является численным значением, введите сумму повторно. Доступные команды: Назад".format(input_message)

                    buttons, user_storage = get_suggests(user_storage)
                    return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

            if handler.count("repayment"):
                if handler.endswith("repayment"):
                    handler += "->next"
                    user_storage['suggests'] = ["Назад"]
                    money = database.get_entry("users_info", ['Money'], {'request_id': request.user_id})[0][0]
                    credit = database.get_entry("users_info", ['Credit'],
                                                 {'request_id': request.user_id})[0][0].split("#$")
                    if credit[1] != "0":
                        output_message = "Имеющаяся сумма у вас на руках: {}р \n Задолжность по кредиту: {} Процентная ставка: {} Срок выплаты: {} \n" \
                                         " Введите сумму, которую вы хотели бы внести на кредитный счет. \n Доступные команды: Назад".format(
                            money, credit[1], credit[2], credit[3]
                        )
                    else:
                        output_message = credit+" Доступные команды: Назад"

                    buttons, user_storage = get_suggests(user_storage)
                    return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

                if handler.endswith("next"):
                    user_storage['suggests'] = ["Назад"]
                    try:
                        money = database.get_entry("users_info", ['Money'], {'request_id': request.user_id})[0][0]
                        credit = database.get_entry("users_info", ['Credit'],
                                                    {'request_id': request.user_id})[0][0].split("#$")
                        if credit != "В данный момент задолжности нет.":
                            credit_sum = credit[0]

                            if int(input_message) <= money or money >= credit_sum:
                                if int(input_message) < credit_sum:
                                    # !! Здесь сделать апдейт кредита и налички игрока
                                    output_message = "Ваша сумма по кредиту уменьшилась и теперь составляет {}р. \n Оставшиеся деньги у вас на руках: {}р Доступные команды: Назад".format(
                                        credit_sum - int(input_message), money - int(input_message)
                                    )
                                else:
                                    output_message = "Ваш кредит успешно погашен, даже если вы ввели сумму больше" \
                                                     " задолжности, лишняя часть останется при вас. \n Оставшиеся деньги" \
                                                     " у вас на руках: {}".format(money-credit_sum)
                            else:
                                output_message = "У вас недостаточно денег для погашения, не хватает {}р. Доступные команды: Назад".format(
                                    int(input_message) - money)
                        else:
                            output_message = credit+" Доступные команды: Назад"

                    except TypeError:
                        output_message = "{} не является численным значением, введите сумму повторно. Доступные команды: Назад".format(
                            input_message)

                    buttons, user_storage = get_suggests(user_storage)
                    return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

            if handler.count("money_take"):
                if handler.endswith("money_take"):
                    money = "сюда вставить получение денег пользователя"
                    deposit = [1488, 228]
                    handler += "->next"
                    user_storage['suggests'] = ["Назад"]
                    if deposit[0] != 0:
                        output_message = "Имеющаяся сумма у вас на руках: {}р \n Сумма на вкладе: {}р Процент по вкладу: {}% \n" \
                                         " Введите сумму, которую вы хотели бы забрать с банковского счета. \n Доступные команды: Назад".format(
                            money, deposit[0], deposit[1]
                        )
                    else:
                        output_message = "В данным момент на вашем счете денег нет. Доступные команды: Назад"

                    buttons, user_storage = get_suggests(user_storage)
                    return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

                if handler.endswith("next"):
                    user_storage['suggests'] = ["Назад"]
                    try:
                        # !!сюда вставить получение денег пользователя
                        money = 1888
                        deposit = [1488, 228]
                        if deposit[0] != 0:
                            if int(input_message) <= deposit[0]:
                                output_message = "Ваша сумма денег на руках увеличилась и теперь составляет {}р." \
                                    " \n Оставшаяся сумма на банковском счете: {}".format(money+int(input_message), deposit[0] - int(input_message))
                            else:
                                output_message = "На вашем банковском счете недостаточно средств, не хватает {}р. Доступные команды: Назад".format(
                                    int(input_message) - deposit[0])
                        else:
                            output_message = "В данным момент на вашем счете денег нет. Доступные команды: Назад"

                    except Exception:
                        output_message = "{} не является численным значением, введите сумму повторно. Доступные команды: Назад".format(
                            input_message)

                    buttons, user_storage = get_suggests(user_storage)
                    return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

            if handler.count("credit"):
                if handler.endswith("credit"):
                    user_storage['suggests'] = ["Назад"]
                    #Нынешний кредит пользователя
                    credit = [0, 0]
                    handler+="->next"
                    if credit[0] == 0:
                        user_storage['suggests'].append("Продолжить")
                        index = "1"
                        #["выдаваемая сумма", "процентная ставка", "срок выплаты"]
                        available_credit = read_answers_data("data/profit_page_list")["credit"][index]
                        output_message = "Вам доступен кредит на сделующих условиях: \n Выдаваемая сумма: {}" \
                                         " \n Процентная ставка: {} \n Срок выплаты: {}" \
                                         " \n Напишите далее, если вас всё устраивает, назад, если нет. \n  Доступные команды: Продолжить, Назад".format(
                            available_credit[0], available_credit[1], available_credit[2]
                        )
                    else:
                        output_message = "Выдача нового кредита в данный момент недоступна, так как имеется задолжность. Доступные команды: Назад"
                    buttons, user_storage = get_suggests(user_storage)
                    return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

                if handler.endswith("next"):
                    #!! Сделать изменение кредита пользователя
                    user_storage['suggests'] = ["Назад"]
                    # Нынешний кредит пользователя
                    credit = [0, 0]
                    if input_message == "продолжить" or input_message == "давай" or input_message == "согласен":
                        if credit[0] == 0:
                            index = "1"
                            # ["выдаваемая сумма", "процентная ставка", "срок выплаты"]
                            available_credit = read_answers_data("data/profit_page_list")["credit"][index]
                            output_message = "Вам выдан кредит на сделующих условиях: \n Выдаваемая сумма: {}" \
                                             " \n Процентная ставка: {} \n Срок выплаты: {}" \
                                             " \n Доступные команды: Назад".format(
                                available_credit[0], available_credit[1], available_credit[2]
                            )
                        else:
                            output_message = "Выдача нового кредита в данный момент недоступна, так как имеется задолжность. Доступные команды: Назад"
                        buttons, user_storage = get_suggests(user_storage)
                        return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

                    buttons, user_storage = get_suggests(user_storage)
                    return ЯНичегоНеПонял(response, user_storage)

    if handler.startswith("education_page"):
        if handler == "education_page":
            expirience = "сюда вставить опыт игрока"
            lvl = "сюда вставить уровень игрока"


    update_handler(handler, database, request)

    if input_message in ['нет', 'не хочется', 'в следующий раз', 'выход', "не хочу", 'выйти']:
        answered = True
        choice = random.choice(aliceAnswers["quitTextVariations"])
        response.set_text(aliceSpeakMap(choice))
        response.set_tts(aliceSpeakMap(choice,True))
        response.end_session = True
        return response, user_storage
    print(handler)

    buttons, user_storage = get_suggests(user_storage)
    return ЯНичегоНеПонял(response, user_storage)


def get_suggests(user_storage):
    if "suggests" in user_storage.keys():
        suggests = [
            {'title': suggest, 'hide': True}
            for suggest in user_storage['suggests']
        ]
    else:
        suggests = []

    return suggests, user_storage
