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
    # !! handler = "ну вот тут ты забираешь хэндлер из бд, ага"
    input_message = request.command.lower().strip("?!.")
    # первый запуск/перезапуск диалога
    if request.is_new_session or not database.get_entry("users_info",  ['Named'], {'request_id': request.user_id})[0][0]:
        if request.is_new_session and (database.get_entry("users_info",  ['Name'],
                                                          {'request_id': request.user_id}) == 'null'
                                       or not database.get_entry("users_info",  ['Name'])):
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

        user_storage['suggests']= [
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
                "Назад"
            ]

            handler += "->start_next"

            output_message = "Ваши деньги: {} \n Ваш накопленный опыт: {} \n Ваш голод: {} \n Ваше настроение: {}" \
                             " \n Ваше здоровье: {} Текущая дата: {} \n Доступные опции: {}"\
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
                food = "сюда вставить получение голода пользователя"

                index = "1"
                food_list = read_answers_data("data/start_page_list")["food"][index]
                user_storage['suggests'] = [i + " цена {} восполнение {}".format(food_list[i][0], food_list[i][1]) for i in
                                            food_list.keys()]
                handler += "->next"

                output_message = "Ваш голод: {} Список продуктов: \n {}"\
                    .format(food, ",\n".join(user_storage['suggests'][:-1])
                            + "\n Доступные опции: Назад")

                buttons, user_storage = get_suggests(user_storage)
                return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

            # start_page -> start_next -> food_recharge -> food_next
            if handler.endswith("next"):
                # !! Необходимо добавить в БД уровень игрока, который я потом буду подсчитывать, стартовый - первый.
                # !! Этот уровень и есть индекс, агааа.
                index = "1"
                product = ""
                food_list = read_answers_data("data/start_page_list")["food"][index]
                for i in food_list.keys():
                    if i.lower().startswith(input_message):
                        product = i
                        product_price = food_list[i][0]
                        product_weight = food_list[i][1]

                if product:
                    # !! Дальше мы проверяем, можем ли мы купить этот продукт,
                    # поэтому пока что тут просто будет очередной флажок
                    flag = True
                    if flag == True:
                        output_message = "Продукт {} успешно преобретен. \n Список продуктов: {}"\
                            .format(product, ",\n".join(user_storage['suggests'][:-1]) + "\n Доступные команды: Назад")
                    else:
                        output_message = "Продукт {} нельзя преобрести, нехватает денег. \n Список продуктов:{} "\
                            .format(product, ",\n".join(user_storage['suggests'][:-1]) + "\n Доступные команды: Назад")
                else:
                    output_message = "Продукт {} не найден, повторите запрос".format(input_message)

                buttons, user_storage = get_suggests(user_storage)
                return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

        if handler.count("health"):
            # start_page -> start_next -> food_recharge -> health_recharge
            if handler.endswith("health_recharge"):
                health = "сюда вставить получение здоровья пользователя"

                index = "1"
                food_list = read_answers_data("data/start_page_list")["health"][index]
                user_storage['suggests'] = \
                    [i + " цена {} восполнение {}".format(food_list[i][0], food_list[i][1]) for i in food_list.keys()]

                handler += "->next"

                output_message = "Ваше здоровье {} \n Список доступных методов восстановления здоровья: \n {}"\
                    .format(health, ",\n".join(user_storage['suggests'][:-1])+ "\n Доступные команды: Назад")

                buttons, user_storage = get_suggests(user_storage)
                return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

            # start_page -> start_next -> food_recharge -> health_next
            if handler.endswith("next"):
                # !! Необходимо добавить в БД уровень игрока, который я потом буду подсчитывать, стартовый - первый.
                # !! Этот уровень и есть индекс, агааа.
                index = "1"
                product = ""
                food_list = read_answers_data("data/start_page_list")["health"][index]
                for i in food_list.keys():
                    if i.lower().startswith(input_message):
                        product = i
                        product_price = food_list[i][0]
                        product_weight = food_list[i][1]

                if product:
                    money = 1488
                    if money - product_price:
                        output_message = "Метод {} успешно оплачен. \n Список доступных методов восстановления здоровья: {}"\
                            .format(product, ",\n".join(user_storage['suggests'][:-1])+ "\n Доступные команды: Назад")
                    else:
                        output_message = "Метод {} нельзя оплатить, нехватает денег. \n Список доступных методов восстановления" \
                                         " здоровья: {}".format(product, ",\n".join(user_storage['suggests'][:-1])
                                                                + "\n Доступные команды: Назад")
                else:
                    output_message = "Метод {} не найден, повторите запрос. \n Список доступных методов восстановления здоровья:" \
                                     " {}".format(input_message, ",\n".join(user_storage['suggests'][:-1])
                                                  + "\n Доступные команды: Назад")

                buttons, user_storage = get_suggests(user_storage)
                return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

        if handler.count("mood"):
            # start_page -> start_next -> food_recharge -> mood_recharge
            if handler.endswith("mood_recharge"):
                mood = "сюда вставить получение здоровья пользователя"

                index = "1"
                food_list = read_answers_data("data/start_page_list")["mood"][index]
                user_storage['suggests'] = [i+" цена {} восполнение {}".format(food_list[i][0], food_list[i][1]) for i in food_list.keys()]

                handler += "->next"

                output_message = "Ваше настроение {} \n Список доступных методов восстановления настроения: \n {}"\
                    .format(mood, ",\n".join(user_storage['suggests'][:-1])+ "\n Доступные команды: Назад")

                buttons, user_storage = get_suggests(user_storage)
                return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

            # start_page -> start_next -> food_recharge -> food_next
            if handler.endswith("next"):
                # !! Необходимо добавить в БД уровень игрока, который я потом буду подсчитывать, стартовый - первый.
                # !! Этот уровень и есть индекс, агааа.
                index = "1"
                product = ""
                food_list = read_answers_data("data/start_page_list")["mood"][index]
                for i in food_list.keys():
                    if i.lower().startswith(input_message):
                        product = i
                        product_price = food_list[i][0]
                        product_weight = food_list[i][1]

                if product:
                    # !! Дальше мы проверяем, можем ли мы купить этот продукт,
                    # поэтому пока что тут просто будет очередной флажок
                    flag = True
                    if flag == True:
                        output_message = "Метод {} успешно оплачен. \n Список доступных методов восстановления настроения: {}"\
                            .format(product, ",\n".join(user_storage['suggests'][:-1])+ "\n Доступные команды: Назад")
                    else:
                        output_message = "Метод {} нельзя оплатить, нехватает денег. \n Список доступных методов восстановления" \
                                         " настроения: {}".format(product, ",\n".join(user_storage['suggests'][:-1])
                                                                  + "\n Доступные команды: Назад")
                else:
                    output_message = "Метод {} не найден, повторите запрос. \n Список доступных методов восстановления здоровья:" \
                                     " {}".format(input_message, ",\n".join(user_storage['suggests'][:-1])
                                                  + "\n Доступные команды: Назад")

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
            job = "сюда вставить получение работы пользователя"
            freelance = "сюда вставить получение фриланса пользователя"
            bank = "сюда вставить получение банка пользователя"
            business = "сюда вставить получение бизнесса пользователя"

            user_storage['suggests'] = [
                "Работа",
                "Фриланс",
                "Банк",
                "Бизнес",
                "Назад"
            ]

            handler += "->profit_next"

            output_message = "Ваши работа: {} \n Ваша фрилансерская деятельность: {} \n Информация о деньгах в банке" \
                             " : {} \n Ваш бизнес: {} Доступные опции: {}"\
                .format(job, freelance, bank, business, ", ".join(user_storage['suggests']))

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
                # !! Вот тут нужно сделать получение работы из БД
                job = "1"
                job_list = read_answers_data("data/profit_page_list")["job"]
                keys = sorted(job_list.keys())
                user_storage['suggests'] = ["Назад"]
                # Если у нас не максимально возможная ЗП, выдаем список вакансий длиной максимум до 10
                if int(job) != len(keys):
                    border = len(keys[int(job):]) % 10 if len(keys[int(job):]) % 10 != 0 else 10
                    handler += "->next"
                    lst = ["Текущая: {} Зарплата: {}".format(job_list[job][0], job_list[job][1])]
                    lst += keys[int(job):border + 1]
                    output_message = "Список вакансий: \n {} \n {} \n Выберите желаемую.  \n Доступные команды: Назад"\
                        .format(lst[0],
                                "\n".join(["{} Зарплата: {}".format(job_list[i][0], job_list[i][1]) for i in lst[1:]]))
                else:
                    output_message = "Список вакансий: \n {} \n Выбирать больше не из чего. \n Доступные команды: Назад"\
                        .format(job_list[job])

                buttons, user_storage = get_suggests(user_storage)
                return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

            if handler.endswith("next"):
                job = "1"
                user_storage['suggests'] = ["Назад"]
                handler = "->".join(handler.split("->")[:-1])
                output_message = ""
                # !! Вот сюда засунуть нужно образование игрока
                user_requirements = ["..."]
                job_list = read_answers_data("data/profit_page_list")["job"]
                if not input_message in job_list[job][0].lower():
                    keys = sorted(job_list.keys())
                    border = len(keys[int(job):]) % 10 if len(keys[int(job):]) % 10 != 0 else 10
                    for i in keys[int(job):border + 1]:
                        if input_message in job_list[i][0].lower():
                            difference = [j for j in job_list[i][2] if j not in user_requirements]
                            if not difference:
                                # !! Тут мы меняем работу на новую, если у нас совпадают все требования
                                job = i
                                output_message = "Вы успешно повысились до {}. Доступные команды: Назад"\
                                    .format(job_list[job][0])
                            else:
                                output_message = "Повышение невозможно, нехватает следующего: {}. Доступные команды: Назад"\
                                    .format(", ".join(difference))
                            break
                else:
                    output_message = "В данный момент вы здесь работаете. Доступные команды: Назад"
                if output_message:
                    buttons, user_storage = get_suggests(user_storage)
                    return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

        if handler.count("freelance"):
            if handler.endswith("freelance"):
                # !! Вот тут нужно сделать получение нынешней подработки из БД в переменную ниже
                current_freelance = ["нет", "вреня, которое осталось"]
                user_storage['suggests'] = ["Назад"]
                if current_freelance[0] == "нет":
                    # !! Это снова тот индекс(уровень игрока, да).
                    index = "1"
                    freelance_list = read_answers_data("data/profit_page_list")["freelance"][index]
                    handler += "->next"
                    lst = ["{} Оплата: {} Время выполнения {}"
                               .format(i, freelance_list[i][0], freelance_list[i][1]) for i in freelance_list.keys()]
                    output_message = "Список доступных подработок: \n {}\n " \
                                     "Выберите желаемую.  \n Доступные команды: Назад".format("\n".join(lst))
                else:
                    output_message = "В данный момент вы заняты {}, подождите {}, тогда вы сможете взять новое задание."\
                        .format(current_freelance[0], current_freelance[1])

                buttons, user_storage = get_suggests(user_storage)
                return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

            if handler.endswith("next"):
                # !! Это снова тот индекс(уровень игрока, да).
                index = "1"
                current_freelance = ["нет", "вреня, которое осталось"]
                user_storage['suggests'] = ["Назад"]
                if current_freelance[0] == "нет":
                    freelance_list = read_answers_data("data/profit_page_list")["freelance"][index]
                    lst = ["{} Оплата: {} Время выполнения {}"
                               .format(i, freelance_list[i][0], freelance_list[i][1]) for i in freelance_list.keys()]
                    for i in freelance_list.keys():
                        if input_message in i:
                            # !! Вот тут нужно сделать внесение новой подработки в БД из переменной ниже
                            current_freelance = [i, freelance_list[i][0], freelance_list[i][1]]
                            output_message = "Подработка {} успешно взята на исполение. Оплата: {} Время выполнения" \
                                             " {} Доступные команды: Назад".format(i, current_freelance[1], current_freelance[2])
                            buttons, user_storage = get_suggests(user_storage)
                            return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

                    output_message = "Подработка {} не найдена. Выберите одну из доступных: \n {} \n Доступные команды: Назад"\
                        .format(input_message, "\n".join(lst))
                    buttons, user_storage = get_suggests(user_storage)
                    return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

                output_message = "В данный момент вы заняты {}, подождите {}, тогда вы сможете взять новое задание." \
                    .format(current_freelance[0], current_freelance[1])
                buttons, user_storage = get_suggests(user_storage)
                return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

            return ЯНичегоНеПонял(response, user_storage)

        if handler.count("bank"):
            if handler.endswith("bank"):
                money = "сюда вставить получение денег пользователя"
                handler += "->next"
                deposit = "Сюда вставить информацию о текущем вкладе игрока"
                credit = [0, 0]
                # !! Это снова тот индекс(уровень игрока, да).
                index = "1"
                available_credit = read_answers_data("data/profit_page_list")["credit"][index]\
                    if credit[0] == 0 \
                    else "Выдача нового кредита в данный момент недоступна, так как имеется задолжность"
                user_storage['suggests'] = [i for i in [
                    "Внести деньги на счет",
                    "Погасить задолжность по кредиту" if credit[0] != 0  else "",
                    "Взять деньги со счета" if deposit != 0 else "",
                    "Взять кредит" if credit[0] == 0 else "",
                    "Назад"
                ] if i]
                output_message = "Наличные: {}р \n Информация о вашем банковском счете: \n Нынешняя сумма вклада: {} \n" \
                                 " Нынешняя задолжность по кредиту: {} \n Доступна сумма выдачи денег по кредиту {} \n" \
                                 " Доступные команды: {}".format(money, deposit, credit, available_credit, "\n".join(user_storage["suggests"]))

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
                    money = "сюда вставить получение денег пользователя"
                    # !! Это снова тот индекс(уровень игрока, да).
                    index = 1
                    handler += "->next"
                    user_storage['suggests'] = ["Назад"]
                    percent = read_answers_data("data/profit_page_list")["deposit"][index]
                    deposit = "сюда вставить информацию о текущем вкладе игрока"
                    output_message = "Имеющаяся сумма у вас на руках: {}р \n Сумма во вкладе: {}р Процент по вкладу: {}% \n" \
                                     " Введите сумму, которую вы хотели бы внести на счет. \n Доступные команды: Назад".format(
                        money, deposit, percent
                    )
                    buttons, user_storage = get_suggests(user_storage)
                    return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

                if handler.endswith("next"):
                    user_storage['suggests'] = ["Назад"]
                    try:
                        # !!сюда вставить получение денег пользователя
                        money = 1488
                        if int(input_message) <= money:
                            #!!сюда вставить информацию о текущем вкладе игрока
                            deposit = 228
                            #!! Здесь сделать апдейт депозита и налички игрока
                            output_message = "Ваш вклад увеличился и теперь составляет {}р. \n Оставшиеся деньги у вас на руках: {}р Доступные команды: Назад".format(
                                deposit+int(input_message), money-int(input_message)
                            )
                        else:
                            output_message = "У вас недостаточно денег для внесения, нехватает {}р. Доступные команды: Назад".format(int(input_message)-money)

                    except TypeError:
                        output_message = "{} не является численным значением, введите сумму повторно. Доступные команды: Назад".format(input_message)

                    buttons, user_storage = get_suggests(user_storage)
                    return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

            if handler.count("repayment"):
                if handler.endswith("repayment"):
                    money = "сюда вставить получение денег пользователя"
                    # !! Это снова тот индекс(уровень игрока, да).
                    index = "1"
                    handler += "->next"
                    user_storage['suggests'] = ["Назад"]
                    #!! сюда вставить информацию о текущем кредите игрока
                    credit = "В данный момент задолжности нет."
                    #credit = [1488, 13,37, 21]
                    if credit != "В данный момент задолжности нет.":
                        output_message = "Имеющаяся сумма у вас на руках: {}р \n Задолжность по кредиту: {}р Процент по кредиту: {}% Срок выплаты: Осталось {} \n" \
                                         " Введите сумму, которую вы хотели бы внести на кредитный счет. \n Доступные команды: Назад".format(
                            money, credit[0], credit[1], credit[2]
                        )
                    else:
                        output_message = credit+" Доступные команды: Назад"

                    buttons, user_storage = get_suggests(user_storage)
                    return НуПридумаемНазваниеПотом(response, user_storage, output_message, buttons, database, request, handler)

                if handler.endswith("next"):
                    user_storage['suggests'] = ["Назад"]
                    try:
                        # !!сюда вставить получение денег пользователя
                        money = 14088
                        # !!сюда вставить информацию о текущем вкладе игрока
                        credit = "В данный момент задолжности нет."
                        #credit = [1488, 13,37, 21]
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
