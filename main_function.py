# coding: utf-8
from __future__ import unicode_literals
import random
import json

Named = False


def find_difference(lst1, lst2):  # i = item
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
    

def IDontUnderstand(response, user_storage, buttons = ""):
    message = random.choice(aliceAnswers["cantTranslate"])
    response.set_text(aliceSpeakMap(message))
    response.set_tts(aliceSpeakMap(message, True))
    buttons, user_storage = get_suggests(user_storage)
    response.set_buttons(buttons)
    return response, user_storage

# Ну вот эта функция всем функциям функция, ага. Замена постоянному формированию ответа, ага, экономит 4 строчки!!
def message_return(response, user_storage, message, button, database, request, handler, warning, congrats, flag=False):
    # ща будет магия
    update_handler(handler, database, request)
    if warning:
        message = warning+ message
    text_message = message.split("Доступные")[0]
    if flag:
        response.set_text(aliceSpeakMap(text_message))
        response.set_tts(aliceSpeakMap(message, True))
    else:
        response.set_text(text_message)
        response.set_tts(message)
    buttons, user_storage = get_suggests(user_storage)
    response.set_buttons(button)
    return response, user_storage


def handle_dialog(request, response, user_storage, database):
    # request.command - сообщение от пользователя
    warning_message = ""
    congrats = ""
    user_storage = user_storage
    if not user_storage:
        user_storage = {"suggests" : []}
    input_message = request.command.lower().strip("?!.")
    if database.get_entry("users_info",  ['handler'], {'request_id': request.user_id}) != [] and \
            database.get_entry("users_info", ['handler'], {'request_id': request.user_id})[0][0].startswith('is_dead'):
        handler = database.get_entry("users_info",  ['handler'], {'request_id': request.user_id})[0][0]
        if handler == "is_dead" or request.is_new_session:
            output_message = "Ваше здоровье опустилось до нуля, вы мертвы. Нажмите любую кнопку" \
                             " для перезапуска симуляции."
            handler += '->next'
            user_storage['suggests'] = ["Любая кнопка"]
            buttons, user_storage = get_suggests(user_storage)
            return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message,
                                            True)
        if handler.endswith("next"):
            Name = database.get_entry("users_info", ['Name'], {'request_id': request.user_id})[0][0]
            database.delete_entry("users_info", {"request_id": request.user_id})
            database.add_entries("users_info", {"request_id": request.user_id})
            database.update_entries('users_info', request.user_id, {'Name': Name}, update_type='rewrite')
            database.update_entries('users_info', request.user_id, {'Named': True}, update_type='rewrite')
            user_storage['suggests'] = [
                "Основная информация",
                "Источник дохода",
                "Образование и курсы",
                "Помощь",
                "Следующий день"
            ]
            output_message = random.choice(aliceAnswers["continueTextVariations"]).capitalize() + " Доступные разделы: " \
                             + ", ".join(user_storage['suggests'])
            handler = "other_next"
            buttons, user_storage = get_suggests(user_storage)
            return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats,
                                            True)

    # первый запуск/перезапуск диалога
    if request.is_new_session or not database.get_entry("users_info",  ['Named'], {'request_id': request.user_id})[0][0]:
        if request.is_new_session and (database.get_entry("users_info", ['Name'],
                                                          {'request_id': request.user_id}) == 'null'
                                       or not database.get_entry("users_info", ['Name'], {'request_id': request.user_id})):
            output_message = "Приветствую, немеханический. Не получается стать программистом? " \
                      "Есть вопросы о нашей нелёгкой жизни? Запускай симулятор!\n" \
                      "#для продолжения необходимо пройти авторизацию, введите имя пользователя..."
            response.set_text(aliceSpeakMap(output_message))
            response.set_tts(aliceSpeakMap(output_message))
            database.add_entries("users_info", {"request_id": request.user_id})
            handler = "asking name"
            update_handler(handler, database, request)
            return response, user_storage
        handler = database.get_entry("users_info", ['handler'], {'request_id': request.user_id})[0][0]
        if handler == "asking name":
            database.update_entries('users_info', request.user_id, {'Named': True}, update_type='rewrite')
            user_storage["name"] = request.command
            database.update_entries('users_info', request.user_id, {'Name': input_message}, update_type='rewrite')

        user_storage['suggests'] = [
            "Основная информация",
            "Источник дохода",
            "Образование и курсы",
            "Помощь",
            "Следующий день"
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
        return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats, True)

    handler = database.get_entry("users_info", ['handler'], {'request_id': request.user_id})[0][0]
    # Возвращает хендлер к основному разделу
    if input_message == "следующий день" or "следующий" in input_message:
        handler = "->".join(handler.split("->")[:-1])
        day = database.get_entry("users_info", ['Day'], {'request_id': request.user_id})[0][0]
        database.update_entries('users_info', request.user_id, {'Day': day + 1}, update_type='rewrite')
        database.update_entries('users_info', request.user_id, {'Day_changed': True}, update_type='rewrite')

    if database.get_entry("users_info", ['Day_changed'], {'request_id': request.user_id})[0][0]:
        money = database.get_entry("users_info", ['Money'], {'request_id': request.user_id})[0][0]
        exp = database.get_entry("users_info", ['Exp'], {'request_id': request.user_id})[0][0]
        job = database.get_entry("users_info", ['Job'], {'request_id': request.user_id})[0][0].split("#$")
        food = database.get_entry("users_info", ['Food'], {'request_id': request.user_id})[0][0]
        waste = database.get_entry("users_info", ['Waste'], {'request_id': request.user_id})[0][0].split("#$")
        food_less = waste[0]
        mood_less = waste[1]
        if food-int(food_less) > 0:
            if waste[3]:
                database.update_entries('users_info', request.user_id, {'Waste': "#$".join([food_less, mood_less,
                                                                                            waste[2], "0"])},
                                        update_type='rewrite')
            database.update_entries('users_info', request.user_id, {'Food': food-int(food_less)}, update_type='rewrite')
        else:
            warning_message += "Внимание, вы сильно голодны: ваше здоровье будет уменьшаться на 10 каждый день," \
                               " пока вы не избавитесь от голода.\n"
            database.update_entries('users_info', request.user_id, {'Food': 0},
                                    update_type='rewrite')
            if waste[3] == "0":
                database.update_entries('users_info', request.user_id, {'Waste': "#$".join([food_less, mood_less,
                                                                            waste[2], "10"])}, update_type='rewrite')
        waste = database.get_entry("users_info", ['Waste'], {'request_id': request.user_id})[0][0].split("#$")
        mood = database.get_entry("users_info", ['Mood'], {'request_id': request.user_id})[0][0]
        if mood-int(mood_less) > 0:
            database.update_entries('users_info', request.user_id, {'Mood': mood-int(mood_less)}, update_type='rewrite')
            if waste[2]:
                database.update_entries('users_info', request.user_id, {'Waste': "#$".join([food_less, mood_less,
                                                                                            "0", waste[3]])},
                                        update_type='rewrite')
        else:
            database.update_entries('users_info', request.user_id, {'Mood': 0},
                                    update_type='rewrite')
            warning_message += "Внимание, вы очень печальны: ваше здоровье будет уменьшаться на 5 единиц каждый день," \
                               " пока вы не повысите настроение. \n"
            if waste[2] == "0":
                database.update_entries('users_info', request.user_id, {'Waste': "#$".join([food_less, mood_less,
                                                                                    "5", waste[3]])}, update_type='rewrite')
        health_less = str(int(waste[2])+int(waste[3]))
        health = database.get_entry("users_info", ['Health'], {'request_id': request.user_id})[0][0]
        if int(health-int(health_less)*float(job[3])) > 0:
            database.update_entries('users_info', request.user_id, {'Health':
                                                                        int(health - int(health_less) * float(job[3]))}, update_type='rewrite')
        else:
            output_message = "Ваше здоровье опустилось до нуля, вы мертвы.\nНажмите любую кнопку" \
                             " для перезапуска симуляции."
            handler = 'is_dead->next'
            user_storage['suggests'] = ["Любая кнопка"]
            buttons, user_storage = get_suggests(user_storage)
            return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

        if job[0] != "Безработный":
            database.update_entries('users_info', request.user_id, {'Money':
                                                                        money+int(job[1])},
                                    update_type='rewrite')
            if job[3] != "0":
                database.update_entries('users_info', request.user_id, {'Exp':
                                                                            exp + int(job[2])},
                                        update_type='rewrite')
                exp = database.get_entry("users_info", ['Exp'], {'request_id': request.user_id})[0][0]
        freelance = database.get_entry("users_info", ['Freelance'], {'request_id': request.user_id})[0][0].split("#$")
        if freelance[0] != "Безделие":
            freelance[2] = str(int(freelance[2]) - 1)
            if freelance[2] == "0":
                print(freelance)
                money -= int(freelance[1])
                exp += int(freelance[2])
                database.update_entries('users_info', request.user_id,
                                        {'Exp': exp}, update_type='rewrite')
                database.update_entries('users_info', request.user_id,
                                        {'Money': money}, update_type='rewrite')
                freelance = 'Безделие#$бесценный опыт о потери времени#$бесконечность'
                database.update_entries('users_info', request.user_id,
                                        {'Freelance': freelance}, update_type='rewrite')
            else:
                database.update_entries('users_info', request.user_id,
                                        {'Freelance': "#$".join(freelance)}, update_type='rewrite')
        credit = database.get_entry("users_info", ['Credit'], {'request_id': request.user_id})[0][0].split("#$")
        if credit[0] != "0":
            if int(credit[2]) - 1 > 0:
                if int(credit[2]) - 1 < 6:
                    warning_message += "Внимание! Близится крайний срок оплаты кредита! Если не произвести оплату " \
                                       "вовремя, то судебные приставы лишат вас всего имущества и накопленных денег! \n"
                credit = "#$".join([str(int(int(credit[0])+(int(credit[0])*float(credit[1])/100)//30)), credit[1], str(int(credit[2]) - 1)])
                database.update_entries('users_info', request.user_id,
                                        {'Credit': credit}, update_type='rewrite')
        deposit = database.get_entry("users_info", ['Deposit'], {'request_id': request.user_id})[0][0].split("#$")
        if deposit[0] != "0":
            deposit = "#$".join([str(int(int(deposit[0]) + int(deposit[0])*int(deposit[1])/3000)), deposit[1]])
            database.update_entries('users_info', request.user_id,
                                    {'Deposit': deposit}, update_type='rewrite')
        current_course = database.get_entry("users_info", ['current_course'], {'request_id': request.user_id})[0][0].split("#$")
        if current_course[0] != "null":
            if int(current_course[2]) - 1 > 0:
                current_course = "#$".join([current_course[0], current_course[1], str(int(current_course[2]) - 1)])
                database.update_entries('users_info', request.user_id,
                                        {'current_course': current_course}, update_type='rewrite')
            else:
                exp = database.get_entry("users_info", ['Exp'], {'request_id': request.user_id})[0][0]
                course = database.get_entry("users_info", ['course'], {'request_id': request.user_id})[0][0].split("#$")
                course.append(current_course[0])
                database.update_entries('users_info', request.user_id,
                                        {'course': "#$".join(course)}, update_type='rewrite')
                exp += int(current_course[1])
                database.update_entries('users_info', request.user_id,
                                        {'Exp': exp}, update_type='rewrite')
                database.update_entries('users_info', request.user_id,
                                        {'current_course': 'null'}, update_type='rewrite')

        current_education = database.get_entry("users_info", ['current_education'], {'request_id': request.user_id})[0][
            0].split("#$")
        if current_education[0] != "null":
            print(current_education)
            if int(current_education[1]) - 1 > 0:
                current_education = "#$".join([current_education[0], str(int(current_education[1]) - 1), current_education[2]])
                database.update_entries('users_info', request.user_id,
                                        {'current_education': current_education}, update_type='rewrite')
            else:
                exp = database.get_entry("users_info", ['Exp'], {'request_id': request.user_id})[0][0]
                education = database.get_entry("users_info", ['education'], {'request_id': request.user_id})[0][0].split("#$")
                education.append(current_education[0])
                database.update_entries('users_info', request.user_id,
                                        {'education': "#$".join(education)}, update_type='rewrite')
                exp += int(current_education[2])
                database.update_entries('users_info', request.user_id,
                                        {'Exp': exp}, update_type='rewrite')
                database.update_entries('users_info', request.user_id,
                                        {'current_education': 'null'}, update_type='rewrite')

        exp = database.get_entry("users_info", ['Exp'], {'request_id': request.user_id})[0][0]
        lvl = database.get_entry("users_info", ['Lvl'], {'request_id': request.user_id})[0][0]
        credit = database.get_entry("users_info", ['Credit'], {'request_id': request.user_id})[0][0].split("#$")
        if 5000 <= exp < 10000 and lvl != "1":
            if credit[0] != "0":
                database.update_entries('users_info', request.user_id,
                                        {'Сredit': credit[0] + "#$15.9#$" + credit[1]}, update_type='rewrite')
            deposit = database.get_entry("users_info", ['Deposit'], {'request_id': request.user_id})[0][0].split("#$")
            database.update_entries('users_info', request.user_id,
                                    {'Deposit': deposit[0]+"#$10"}, update_type='rewrite')
            congrats += "Поздравляем! Ваш уровень поднялся, ваша кредитная ставка снижена, а процент по вкладу" \
                        " увеличен! Однако в то же время увеличились цены на продукты, развлечения и медицину."
            database.update_entries('users_info', request.user_id,
                                        {'Lvl': '1'}, update_type='rewrite')
        elif 10000 <= exp < 20000 and lvl != "2":
            if credit[0] != "0":
                database.update_entries('users_info', request.user_id,
                                        {'Сredit': credit[0] + "#$12.7#$" + credit[1]}, update_type='rewrite')
            deposit = database.get_entry("users_info", ['Deposit'], {'request_id': request.user_id})[0][0].split("#$")
            database.update_entries('users_info', request.user_id,
                                    {'Deposit': deposit[0] + "#$13"}, update_type='rewrite')
            congrats += "Поздравляем! Ваш уровень поднялся, ваша кредитная ставка снижена, а процент по вкладу" \
                        " увеличен! Однако в то же время увеличились и цены на продукты, развлечения и медицину."
            database.update_entries('users_info', request.user_id,
                                        {'Lvl': '2'}, update_type='rewrite')
        elif 20000 <= exp < 40000 and lvl != "3":
            if credit[0] != "0":
                database.update_entries('users_info', request.user_id,
                                        {'Сredit': credit[0] + "#$11.1#$" + credit[1]}, update_type='rewrite')
            deposit = database.get_entry("users_info", ['Deposit'], {'request_id': request.user_id})[0][0].split("#$")
            database.update_entries('users_info', request.user_id,
                                    {'Deposit': deposit[0] + "#$16"}, update_type='rewrite')
            congrats += "Поздравляем! Ваш уровень поднялся до максимально доступного в данный момент, ваша кредитная ставка снижена, а процент по вкладу" \
                        " увеличен! Однако в то же время увеличились и цены на продукты, развлечения и медицину."
            database.update_entries('users_info', request.user_id,
                                    {'Lvl': '3'}, update_type='rewrite')
        if len(user_storage["suggests"]) > 3:
            if user_storage['suggests'][:4] == ["Основная информация", "Источник дохода", "Образование и курсы", "Помощь"]:
                output_message = "Выберите один из доступных разделов. Доступные разделы: " \
                                 + ", ".join(user_storage['suggests'])
                handler = "other_next"
                buttons, user_storage = get_suggests(user_storage)
                database.update_entries('users_info', request.user_id, {'Day_changed': False}, update_type='rewrite')
                return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message,
                                                True)

        database.update_entries('users_info', request.user_id, {'Day_changed': False}, update_type='rewrite')

    if "помощь" in input_message or input_message in "а что ты умеешь":
        output_message = "В данной игре ты пройдешь путь карьерного роста от безработного до" \
                         " главы собственной компании, в то же время на нем тебе придется следить и бороться с самыми" \
                         " злейшими врагами программистов: голодом и плохим настроением! Проживая день за днем, " \
                         "тебе придется питаться и развлекать себя, дабы не умереть от стресса. Перемещайся по разделам," \
                         "выполняй желаемые действия и переходи на следующий день, всё просто! Удачи! Доступные разделы: {}".format(
            "\n".join(user_storage["suggests"])
        )
        buttons, user_storage = get_suggests(user_storage)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              handler, warning_message, congrats)

    if handler.endswith("other_next"):
        print(input_message in "помощь")
        if input_message == "источник дохода" or input_message == "доход":
            handler = "profit_page"
        elif input_message == "образование и курсы" or input_message == "образование" or input_message == "курсы":
            handler = "education_page"
        elif input_message == "основная информация" or input_message == "информация":
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

        if handler.endswith("other") or handler == "null":
            user_storage['suggests'] = [
                "Основная информация",
                "Источник дохода",
                "Образование и курсы",
                "Помощь",
                "Следующий день"
            ]

            handler = "other->other_next"

            output_message = "Похоже, мы вернулись в начало.\nДоступные опции: {}".format(
                ", ".join(user_storage['suggests']))

            buttons, user_storage = get_suggests(user_storage)
            return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

        if handler == "start_page":
            money = database.get_entry("users_info", ['Money'], {'request_id': request.user_id})[0][0]
            exp = database.get_entry("users_info", ['Exp'], {'request_id': request.user_id})[0][0]
            food = database.get_entry("users_info", ['Food'], {'request_id': request.user_id})[0][0]
            mood = database.get_entry("users_info", ['Mood'], {'request_id': request.user_id})[0][0]
            health = database.get_entry("users_info", ['Health'], {'request_id': request.user_id})[0][0]
            date = database.get_entry("users_info", ['Day'], {'request_id': request.user_id})[0][0]

            user_storage['suggests'] = [
                "Восполнение сытости",
                "Восполнение здоровья",
                "Восполнение настроения",
                "Назад",
                "Следующий день"
            ]

            handler += "->start_next"

            output_message = "Ваши деньги: {} \nВаш накопленный опыт: {} \nВаша сытость: {} \nВаше настроение: {}" \
                             " \nВаше здоровье: {} \nДней с начала игры прошло: {} \nДоступные опции: {}"\
                .format(money, exp, food, mood, health, date, ", ".join(user_storage['suggests']))

            buttons, user_storage = get_suggests(user_storage)
            return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

        # start_page -> start_next
        if handler.endswith("start_next"):
            if input_message == "восполнение сытости" or input_message == "голод" or input_message == "сытость":
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
                lst = [i + " - цена {}, восполнение {}".format(food_list[i][0], food_list[i][1]) for i in
                                            food_list.keys()]
                user_storage['suggests'] = [i for i in
                                            food_list.keys()]+["Назад", "Следующий день"]
                handler += "->next"

                output_message = "Ваш голод: {} \nСписок продуктов:\n {}"\
                    .format(food, ",\n".join(lst)
                            + "\n Доступные опции: Назад")

                buttons, user_storage = get_suggests(user_storage)
                return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

            # start_page -> start_next -> food_recharge -> food_next
            if handler.endswith("next"):
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
                        if money - int(int(product_price)) >= 0:
                            food = food + int(product_weight) if (food + int(product_weight)) % 100 and (food + int(product_weight))\
                                                            < 100  else 100
                            database.update_entries('users_info', request.user_id, {'Food': food},
                                                    update_type='rewrite')
                            database.update_entries('users_info', request.user_id, {'Money': money - int(int(product_price))},
                                                    update_type='rewrite')
                            output_message = "Продукт {} успешно преобретен.\nВаша сытость: {} \n Ваши финансы: {} \n Список продуктов: \n{}"\
                                .format(product, food, money - int(product_price), ",\n".join(user_storage['suggests'][:-1]) + "\n Доступные команды: Назад, Следующий день")
                        else:
                            output_message = "Продукт {} нельзя преобрести, не хватает денег: {} \nВаша сытость: {} \n Ваши финансы: {} \n Список продуктов: \n{} "\
                                .format(product, int(product_price) - money, food, money, ",\n".join(user_storage['suggests'][:-1]) + "\n Доступные команды: Назад, Следующий день")
                    else:
                        output_message = "Продукт {} не найден, повторите запрос \n Ваша сытость: {} \n Ваши финансы: {}".format(input_message, food, money)
                else:
                    output_message = "Вы не голодны. \n  Список продуктов: \n {} \nДоступные команды: Назад, Следующий день".format(
                        ",\n".join(user_storage['suggests'][:-1])
                    )

                buttons, user_storage = get_suggests(user_storage)
                return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

        if handler.count("health"):
            # start_page -> start_next -> food_recharge -> health_recharge
            if handler.endswith("health_recharge"):
                health = database.get_entry("users_info", ['Health'], {'request_id': request.user_id})[0][0]
                index = database.get_entry("users_info", ['Lvl'], {'request_id': request.user_id})[0][0]
                health_list = read_answers_data("data/start_page_list")["health"][index]
                user_storage['suggests'] = [i for i in health_list.keys()] + ["Назад", "Следующий день"]

                lst = [i + " - цена {}, восполнение {}".format(health_list[i][0], health_list[i][1]) for i in
                     health_list.keys()]

                handler += "->next"

                output_message = "Ваше здоровье: {} \n Список доступных методов восстановления здоровья: \n {}"\
                    .format(health, ",\n".join(lst) + "\n Доступные команды: Назад, Следующий день")

                buttons, user_storage = get_suggests(user_storage)
                return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

            # start_page -> start_next -> food_recharge -> health_next
            if handler.endswith("next"):
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
                        if money - int(int(product_price)) >= 0:
                            health = health + int(product_weight) if (health + int(product_weight)) % 100 and (
                                    health + int(product_weight)) < 100 else 100
                            database.update_entries('users_info', request.user_id, {'Health': health},
                                                    update_type='rewrite')
                            database.update_entries('users_info', request.user_id, {'Money': money - int(int(product_price))},
                                                    update_type='rewrite')
                            output_message = "Метод {} успешно оплачен. \n Ваше здоровье: {} \n Ваши финансы: {}" \
                                             " \n Список доступных методов восстановления здоровья: {}"\
                                .format(product, health,money - int(product_price), ",\n".join(user_storage['suggests'][:-1])+ "\n Доступные команды: Назад, Следующий день")
                        else:
                            output_message = "Метод {} нельзя оплатить, не хватает денег: {} \n Ваше здоровье: {} \n" \
                                             "Ваши финансы: {} \nСписок доступных методов восстановления здоровья:\n{}"\
                                .format(product, int(int(product_price)) - money, health, money,
                                        ",\n".join(user_storage['suggests'][:-1]) + "\n Доступные команды: Назад, Следующий день")
                    else:
                        output_message = "Метод {} не найден, повторите запрос. \n Ваше здоровье: {} \n Список доступных методов восстановления здоровья:" \
                                         " \n {}".format(input_message, health, ",\n".join(user_storage['suggests'][:-1])
                                                      + "\n Доступные команды: Назад, Следующий день")
                else:
                    output_message = "Вы полностью здоровы. \n Список доступных методов восстановления здоровья:" \
                                         " {} Доступные команды: Назад, Следующий день".format(",\n".join(user_storage['suggests'][:-1]))

                buttons, user_storage = get_suggests(user_storage)
                return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

        if handler.count("mood"):
            if handler.endswith("mood_recharge"):
                mood = database.get_entry("users_info", ['Mood'], {'request_id': request.user_id})[0][0]
                index = database.get_entry("users_info", ['Lvl'], {'request_id': request.user_id})[0][0]
                mood_list = read_answers_data("data/start_page_list")["mood"][index]
                user_storage['suggests'] = [i for i in mood_list.keys()] + ["Назад", "Следующий день"]

                lst = [i+" - цена {}, восполнение {}".format(mood_list[i][0], mood_list[i][1]) for i in mood_list.keys()]
                handler += "->next"

                output_message = "Ваше настроение: {} \n Список доступных методов восстановления настроения: \n {}"\
                    .format(mood, ",\n".join(lst) + "\n Доступные команды: Назад, Следующий день")

                buttons, user_storage = get_suggests(user_storage)
                return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

            if handler.endswith("next"):
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
                        money = database.get_entry("users_info", ['Money'], {'request_id': request.user_id})[0][0]
                        if money - int(product_price) >= 0:
                            mood = mood + int(product_weight) if (mood + int(product_weight)) % 100 and (
                                    mood + int(product_weight)) < 100 else 100
                            database.update_entries('users_info', request.user_id, {'Mood': mood},
                                                    update_type='rewrite')
                            database.update_entries('users_info', request.user_id, {'Money': money - int(int(product_price))},
                                                    update_type='rewrite')
                            output_message = "Метод {} успешно оплачен. \n Ваш настроение: {} \n Ваши финансы: {} \n Список доступных методов восстановления настроения: \n {}"\
                                .format(product, mood, money - int(int(product_price)), ",\n".join(user_storage['suggests'][:-1])+ "\n Доступные команды: Назад, Следующий день")
                        else:
                            output_message = "Метод {} нельзя оплатить, не хватает денег: {}\n Ваш настроение: {} \n Ваши финансы: {} \n Список доступных методов восстановления" \
                                             " \n настроения: {}".format(product, int(int(product_price)) - money, mood, money, ",\n".join(user_storage['suggests'][:-1])
                                                                      + "\n Доступные команды: Назад, Следующий день")
                    else:
                        output_message = "Метод {} не найден, повторите запрос. \nВаш настроение: {} \n  Список доступных методов восстановления здоровья:" \
                                         " \n {}".format(input_message, mood, ",\n".join(user_storage['suggests'][:-1])
                                                      + "\n Доступные команды: Назад, Следующий день")
                else:
                    output_message = "У вас прекрасное настроение. \n Список доступных методов восстановления здоровья:" \
                                     " \n {} Доступные команды: Назад, Следующий день".format(",\n".join(user_storage['suggests'][:-1]))

                buttons, user_storage = get_suggests(user_storage)
                return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

        buttons, user_storage = get_suggests(user_storage)
        return IDontUnderstand(response, user_storage)

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
                "Помощь",
                "Следующий день"
            ]

            handler = "other->other_next"

            output_message = "Похоже, мы вернулись в начало. \n Доступные опции: {}".format(
                ", ".join(user_storage['suggests']))

            buttons, user_storage = get_suggests(user_storage)
            return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

        if handler == "profit_page":
            job = database.get_entry("users_info", ['Job'], {'request_id': request.user_id})[0][0].split("#$")
            freelance = database.get_entry("users_info", ['Freelance'], {'request_id': request.user_id})[0][0].split("#$")
            bank = (database.get_entry("users_info", ['Credit'], {'request_id': request.user_id})[0][0].split("#$"),
                    database.get_entry("users_info", ['Deposit'], {'request_id': request.user_id})[0][0].split("#$"))
            # business = database.get_entry("users_info", ['Business'], {'request_id': request.user_id})[0][0]

            user_storage['suggests'] = [
                "Работа",
                "Фриланс",
                "Банк",
                "Назад"
            ]

            handler += "->profit_next"

            output_message = "Ваши работа: {} \nЗаработок: {}р \n Ваша фрилансерская деятельность: {} \nВремя выполнения: {}" \
                             " Получаемая прибыль: {} \n Информация о деньгах в банке" \
                             " : \n Задолжность по кредиту: {} \nПроцентная ставка: {} \nСрок выплаты: {}\n Сумма вклада: {} \nПроцент по" \
                             " вкладу: {}\n Доступные команды: {}"\
                .format(job[0], job[1], freelance[0], freelance[2], freelance[1], bank[0][0], bank[0][1], bank[0][2],
                        bank[1][0], bank[1][1], ", ".join(user_storage['suggests']))

            buttons, user_storage = get_suggests(user_storage)
            return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

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
                keys = [str(j) for j in sorted([int(i) for i in job_list.keys()])]
                job_index = 0
                for i in keys:
                    if job[0] in job_list[i]:
                        job_index = i
                        break
                user_storage['suggests'] = ["Назад", "Следующий день"]
                # Если у нас не максимально возможная ЗП, выдаем список вакансий длиной максимум до 10
                if int(job_index) != len(keys):
                    lower_border = int(job_index) - 5 if int(job_index) > 5 else 0
                    upper_border = int(job_index) + 5 if int(job_index) + 5 < len(keys) else len(keys)
                    handler += "->next"
                    lst = ["Текущая: {} \nЗарплата: {} \nПолучаемый опыт: {} \nКоэффициент стресса: {}".format(
                        job_list[job_index][0], job_list[job_index][1], job_list[job_index][3], job_list[job_index][4])]
                    lst += keys[lower_border:int(job_index)] + keys[int(job_index)+1:upper_border]
                    user_storage['suggests'] = [job_list[i][0] for i in lst[1:]]
                    output_message = "Список вакансий: \n{} \n{} \nВыберите желаемую.  \nДоступные команды: Назад, Следующий день"\
                        .format(lst[0],
                                "\n".join(["{} Зарплата: {}. Получаемый опыт: {}. Коэффициент стресса: {}.".format(
                                    job_list[i][0], job_list[i][1], job_list[i][3], job_list[i][4]) for i in lst[1:]]))
                else:
                    output_message = "Текущая: {} \nЗарплата: {} \nПолучаемый опыт: {} \nКоэффициент стресса: {}\n" \
                                     " Вы слишком умны, для вас работы больше пока не придумали\n Доступные команды:" \
                                     " Назад".format(
                        job_list[job_index][0], job_list[job_index][1], job_list[job_index][3], job_list[job_index][4])

                buttons, user_storage = get_suggests(user_storage)
                return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

            if handler.endswith("next"):
                job = database.get_entry("users_info", ['Job'], {'request_id': request.user_id})[0][0].split("#$")
                user_storage['suggests'] = ["Назад", "Следующий день"]
                handler = "->".join(handler.split("->")[:-1])
                output_message = ""
                # !! Вот сюда засунуть нужно образование игрока
                user_requirements = database.get_entry("users_info",
                                            ['education'], {'request_id': request.user_id})[0][0].split("#$")+ \
                                    database.get_entry("users_info",
                                                       ['books'], {'request_id': request.user_id})[0][0].split("#$")+ \
                                    database.get_entry("users_info",
                                                       ['course'], {'request_id': request.user_id})[0][0].split("#$")
                user_requirements = [i for i in user_requirements if i != 'null']
                job_list = read_answers_data("data/profit_page_list")["job"]
                keys = [str(j) for j in sorted([int(i) for i in job_list.keys()])]
                job_index = 0
                for i in keys:
                    if job[0] in job_list[i]:
                        job_index = i
                        break
                if int(job_index) != len(keys):
                    if not input_message in job_list[job_index][0].lower():
                        lower_border = int(job_index) - 5 if int(job_index) > 5 else 0
                        upper_border = int(job_index) + 5 if int(job_index) + 5 < len(keys) else len(keys)
                        for i in keys[lower_border:int(job_index)] + keys[int(job_index)+1:upper_border]:
                            if input_message in job_list[i][0].lower():
                                difference = []
                                lst = "#$".join(user_requirements)
                                for j in job_list[i][2]:
                                    if " или " in j:
                                        if (j.split(" или ")[0] not in lst and j.split(" или ")[1] not in lst):
                                            difference.append(j)
                                    elif j not in lst:
                                        difference.append(j)
                                print(difference)
                                if not difference:
                                    # !! Тут мы меняем работу на новую, если у нас совпадают все требования
                                    job_i = job_list[i]
                                    job = "{}#${}#${}#${}".format(job_i[0], job_i[1], job_i[3], job_i[4])
                                    database.update_entries('users_info', request.user_id, {'Job': job},
                                                            update_type='rewrite')
                                    output_message = "Вы успешно повысились до {}. \nДоступные команды: Назад, Следующий день"\
                                        .format(job_list[i][0])
                                else:
                                    output_message = "Повышение невозможно, не хватает следующего: {}. \nДоступные команды: Назад, Следующий день"\
                                        .format(", ".join(difference))
                                break
                    else:
                        output_message = "В данный момент вы здесь уже работаете. \nДоступные команды: Назад, Следующий день"
                else:
                    output_message = "Текущая: {} \nЗарплата: {} \n Вы слишком умны, для вас работы больше пока не" \
                                     " придумали\n Доступные команды: Назад, Следующий день"
                if output_message:
                    buttons, user_storage = get_suggests(user_storage)
                    return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

        if handler.count("freelance"):
            if handler.endswith("freelance"):
                # !! Вот тут нужно сделать получение нынешней подработки из БД в переменную ниже
                current_freelance = database.get_entry("users_info", ['Freelance'],
                                                       {'request_id': request.user_id})[0][0].split("#$")
                user_storage["suggests"] = []
                if current_freelance[0] == "Безделие":
                    output_message = "В данный момент ваш род занятий: {} \nПолучаемый доход: {} \nВремя выполнения: {}\n"\
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
                                     "Выберите желаемую.  \n Доступные команды: Назад, Следующий день".format("\n".join(lst))
                else:
                    output_message = "В данный момент вы заняты {}, подождите {}, тогда вы сможете взять новое задание."\
                        .format(current_freelance[0], current_freelance[2])
                user_storage['suggests'] += ["Назад", "Следующий день"]
                buttons, user_storage = get_suggests(user_storage)
                return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

            if handler.endswith("next"):
                user_storage["suggests"] = []
                # !! Это снова тот индекс(уровень игрока, да).
                index = database.get_entry("users_info", ['Lvl'],
                                           {'request_id': request.user_id})[0][0]
                current_freelance = database.get_entry("users_info", ['Freelance'],
                                                       {'request_id': request.user_id})[0][0].split("#$")
                if current_freelance[0] == "Безделие":
                    freelance_list = read_answers_data("data/profit_page_list")["freelance"][index]
                    lst = ["{} Оплата: {} Время выполнения {}"
                               .format(i, freelance_list[i][0], freelance_list[i][1]) for i in freelance_list.keys()]
                    for i in freelance_list.keys():
                        if input_message in i.lower():
                            # !! Вот тут нужно сделать внесение новой подработки в БД из переменной ниже
                            user_requirements = database.get_entry("users_info",
                                                                   ['education'], {'request_id': request.user_id})[0][
                                                    0].split("#$") + \
                                                database.get_entry("users_info",
                                                                   ['books'], {'request_id': request.user_id})[0][
                                                    0].split("#$") + \
                                                database.get_entry("users_info",
                                                                   ['course'], {'request_id': request.user_id})[0][
                                                    0].split("#$")
                            user_requirements = [i for i in user_requirements if i != 'null']

                            print(user_requirements)
                            difference = [j for j in freelance_list[i][3] if j not in user_requirements]
                            if not difference:
                                current_freelance = [i, freelance_list[i][0], freelance_list[i][1]]
                                print(current_freelance)
                                output_message = "Подработка {} успешно взята на исполение. \nОплата: {} \nВремя выполнения" \
                                                 " {} \nДоступные команды: Назад, Следующий день".format(i, current_freelance[1], current_freelance[2])
                                database.update_entries('users_info', request.user_id, {'Freelance': "#$".join(current_freelance)},
                                                        update_type='rewrite')
                            else:
                                output_message = "Взятие данной подработки на исполнение невозможно," \
                                                 " не хватает следующего: {}. \nДоступные команды: Назад, Следующий день" \
                                    .format(", ".join(difference))
                            break
                    else:
                        user_storage['suggests'] = [i for i in freelance_list.keys()] + ["Назад", "Следующий день"]
                        output_message = "Подработка {} не найдена. \nВыберите одну из доступных: \n {} \n Доступные команды: Назад, Следующий день"\
                            .format(input_message, "\n".join(lst))
                else:
                    output_message = "В данный момент вы заняты {}, подождите {}, тогда вы сможете взять новое задание." \
                        .format(current_freelance[0], current_freelance[1])
                user_storage['suggests'] += ["Назад", "Следующий день"]
                buttons, user_storage = get_suggests(user_storage)
                return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

            return IDontUnderstand(response, user_storage)

        if handler.count("bank"):
            if handler.endswith("bank"):
                handler += "->next"
                money = database.get_entry("users_info", ['Money'], {'request_id': request.user_id})[0][0]
                credit, deposit = database.get_entry("users_info", ['Credit'],
                                                     {'request_id': request.user_id})[0][0].split("#$"),\
                                  database.get_entry("users_info", ['Deposit'],
                                                     {'request_id': request.user_id})[0][0].split("#$")
                index = database.get_entry("users_info", ['Lvl'],
                                           {'request_id': request.user_id})[0][0]
                available_credit = read_answers_data("data/profit_page_list")["credit"][index]\
                    if credit[0] == "0" \
                    else "Выдача нового кредита в данный момент недоступна, так как имеется задолжность"
                if available_credit.__class__ == list:
                    available_credit = "Выдаваемая сумма: {} \nПроцентная ставка: {} \nСрок выдачи: {}".format(
                        available_credit[0], available_credit[1], available_credit[2])
                user_storage['suggests'] = [i for i in [
                    "Внести деньги на счет",
                    "Погасить задолжность по кредиту" if credit[0] != "0"  else "",
                    "Взять деньги со счета" if deposit[0] != "0" else "",
                    "Взять кредит" if credit[0] == "0" else "",
                    "Назад",
                    "Следующий день"
                ] if i]
                print(credit, deposit)
                output_message = "Наличные: {}р \n Информация о деньгах в банке" \
                             " : \n Задолжность по кредиту: {} \nПроцентная ставка: {} \nСрок выплаты: {}\n Сумма вклада: {}" \
                                 " Процент по вкладу: {} \n Доступный кредит: {}\n Доступные команды: {}".format(
                    money, credit[0], credit[1], credit[2],
                        deposit[0], deposit[1], available_credit, "\n".join(user_storage["suggests"]))

                buttons, user_storage = get_suggests(user_storage)
                return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

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
                    user_storage['suggests'] = ["Назад", "Следующий день"]
                    deposit = database.get_entry("users_info", ['Deposit'],
                                                     {'request_id': request.user_id})[0][0].split("#$")
                    output_message = "Имеющаяся сумма у вас на руках: {}р \n Сумма во вкладе: {}р \nПроцент по вкладу: {}% \n" \
                                     " Введите сумму, которую вы хотели бы внести на счет. \n Доступные команды: Назад, Следующий день".format(
                        money, deposit[0], deposit[1]
                    )
                    buttons, user_storage = get_suggests(user_storage)
                    return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

                if handler.endswith("next"):
                    user_storage['suggests'] = ["Назад", "Следующий день"]
                    try:
                        money = database.get_entry("users_info", ['Money'], {'request_id': request.user_id})[0][0]
                        if int(input_message) <= money:
                            deposit = database.get_entry("users_info", ['Deposit'],
                                                         {'request_id': request.user_id})[0][0].split("#$")
                            deposit[0] = str(int(deposit[0])+int(input_message))
                            database.update_entries('users_info', request.user_id, {'Money': money-int(input_message)},
                                                    update_type='rewrite')
                            database.update_entries('users_info', request.user_id, {'Deposit': "#$".join(deposit)},
                                                    update_type='rewrite')
                            output_message = "Ваш вклад увеличился и теперь составляет {}р. \n Оставшиеся деньги у вас на руках: {}р \nДоступные команды: Назад, Следующий день".format(
                                deposit[0], money-int(input_message)
                            )
                        else:
                            output_message = "У вас недостаточно денег для внесения, не хватает {}р. \nДоступные команды: Назад, Следующий день".format(int(input_message)-money)
                    except TypeError:
                        output_message = "{} не является численным значением, введите сумму повторно. \nДоступные команды: Назад, Следующий день".format(input_message)

                    buttons, user_storage = get_suggests(user_storage)
                    return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

            if handler.count("repayment"):
                if handler.endswith("repayment"):
                    handler += "->next"
                    user_storage['suggests'] = ["Назад", "Следующий день"]
                    money = database.get_entry("users_info", ['Money'], {'request_id': request.user_id})[0][0]
                    credit = database.get_entry("users_info", ['Credit'],
                                                 {'request_id': request.user_id})[0][0].split("#$")
                    if credit[0] != "0":
                        output_message = "Имеющаяся сумма у вас на руках: {}р \n Задолжность по кредиту: {} \nПроцентная ставка: {} \nСрок выплаты: {} \n" \
                                         " Введите сумму, которую вы хотели бы внести на кредитный счет. \n Доступные команды: Назад, Следующий день".format(
                            money, credit[0], credit[1], credit[2]
                        )
                    else:
                        output_message = "В данный момент задолжности по кредиту нет. \nДоступные команды: Назад, Следующий день"

                    buttons, user_storage = get_suggests(user_storage)
                    return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

                if handler.endswith("next"):
                    user_storage['suggests'] = ["Назад", "Следующий день"]
                    try:
                        money = database.get_entry("users_info", ['Money'], {'request_id': request.user_id})[0][0]
                        credit = database.get_entry("users_info", ['Credit'],
                                                    {'request_id': request.user_id})[0][0].split("#$")
                        if credit != "В данный момент задолжности нет.":
                            credit_sum = int(credit[0])

                            if int(input_message) <= money or money >= credit_sum:
                                if int(input_message) < credit_sum:
                                    credit[0] = str(int(credit[0]) - int(input_message))
                                    print(credit)
                                    database.update_entries('users_info', request.user_id,
                                                            {'Money': money - int(input_message)},
                                                            update_type='rewrite')
                                    database.update_entries('users_info', request.user_id,
                                                            {'Credit': "#$".join(credit)},
                                                            update_type='rewrite')
                                    output_message = "Ваша сумма по кредиту уменьшилась и теперь составляет {}р. " \
                                                     "\n Оставшиеся деньги у вас на руках: {}р " \
                                                     "\nДоступные команды: Назад, Следующий день".format(
                                        credit_sum - int(input_message), money - int(input_message)
                                    )
                                else:
                                    credit[0] = "0"
                                    database.update_entries('users_info', request.user_id,
                                                            {'Money': money-credit_sum},
                                                            update_type='rewrite')
                                    database.update_entries('users_info', request.user_id,
                                                            {'Credit': "#$".join(credit)},
                                                            update_type='rewrite')
                                    output_message = "Ваш кредит успешно погашен, даже если вы ввели сумму больше" \
                                                     " задолжности, лишняя часть останется при вас. \n Оставшиеся деньги" \
                                                     " у вас на руках: {}".format(money-credit_sum)
                            else:
                                output_message = "У вас недостаточно денег для погашения, не хватает {}р. \nДоступные команды: Назад, Следующий день".format(
                                    int(input_message) - money)
                        else:
                            output_message = credit+" Доступные команды: Назад, Следующий день"
                    except TypeError:
                        output_message = "{} не является численным значением, введите сумму повторно. \nДоступные команды: Назад, Следующий день".format(
                            input_message)

                    buttons, user_storage = get_suggests(user_storage)
                    return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

            if handler.count("money_take"):
                if handler.endswith("money_take"):
                    money = database.get_entry("users_info", ['Money'], {'request_id': request.user_id})[0][0]
                    handler += "->next"
                    user_storage['suggests'] = ["Назад", "Следующий день"]
                    deposit = database.get_entry("users_info", ['Deposit'],
                                                 {'request_id': request.user_id})[0][0].split("#$")
                    if deposit[0] != "0":
                        output_message = "Имеющаяся сумма у вас на руках: {}р \n Сумма на вкладе: {}р \nПроцент по вкладу: {}% \n" \
                                         " Введите сумму, которую вы хотели бы забрать с банковского счета. \n Доступные команды: Назад, Следующий день".format(
                            money, deposit[0], deposit[1]
                        )
                    else:
                        output_message = "В данным момент на вашем счете денег нет. \nДоступные команды: Назад, Следующий день"

                    buttons, user_storage = get_suggests(user_storage)
                    return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

                if handler.endswith("next"):
                    user_storage['suggests'] = ["Назад", "Следующий день"]
                    try:
                        money = database.get_entry("users_info", ['Money'], {'request_id': request.user_id})[0][0]
                        user_storage['suggests'] = ["Назад", "Следующий день"]
                        deposit = database.get_entry("users_info", ['Deposit'],
                                                     {'request_id': request.user_id})[0][0].split("#$")
                        if deposit[0] != "0":
                            if int(input_message) <= int(deposit[0]):
                                output_message = "Ваша сумма денег на руках увеличилась и теперь составляет {}р." \
                                    " \n Оставшаяся сумма на банковском счете: {}".format(money+int(input_message),
                                                                                          int(deposit[0]) - int(input_message))
                                deposit[0] = str(int(deposit[0])-int(input_message))
                                database.update_entries('users_info', request.user_id,
                                                        {'Money': money + int(input_message)},
                                                        update_type='rewrite')
                                database.update_entries('users_info', request.user_id,
                                                        {'Deposit': "#$".join(deposit)},
                                                        update_type='rewrite')
                            else:
                                output_message = "На вашем банковском счете недостаточно средств, не хватает {}р. \nДоступные команды: Назад, Следующий день".format(
                                    int(input_message) - int(deposit[0]))
                        else:
                            output_message = "В данным момент на вашем счете денег нет. \nДоступные команды: Назад, Следующий день"

                    except Exception:
                        output_message = "{} не является численным значением, введите сумму повторно. \nДоступные команды: Назад, Следующий день".format(
                            input_message)

                    buttons, user_storage = get_suggests(user_storage)
                    return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

            if handler.count("credit"):
                if handler.endswith("credit"):
                    user_storage['suggests'] = ["Назад", "Следующий день"]
                    credit = database.get_entry("users_info", ['Credit'],
                                                {'request_id': request.user_id})[0][0].split("#$")
                    handler += "->next"
                    if credit[0] == "0":
                        user_storage['suggests'].append("Продолжить")
                        index = database.get_entry("users_info", ['Lvl'],
                                                   {'request_id': request.user_id})[0][0]
                        available_credit = read_answers_data("data/profit_page_list")["credit"][index]
                        output_message = "Вам доступен кредит на сделующих условиях: \n Выдаваемая сумма: {}" \
                                         " \n Процентная ставка: {} \n Срок выплаты: {}" \
                                         " \n Напишите далее, если вас всё устраивает;\n назад, если нет. \n  Доступные команды: Продолжить, Назад".format(
                            available_credit[0], available_credit[1], available_credit[2]
                        )
                    else:
                        output_message = "Выдача нового кредита в данный момент недоступна, так как имеется задолжность. \nДоступные команды: Назад, Следующий день"
                    buttons, user_storage = get_suggests(user_storage)
                    return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

                if handler.endswith("next"):
                    user_storage['suggests'] = ["Назад", "Следующий день"]
                    credit = database.get_entry("users_info", ['Credit'],
                                                {'request_id': request.user_id})[0][0].split("#$")
                    money = database.get_entry("users_info", ['Money'], {'request_id': request.user_id})[0][0]
                    if input_message == "продолжить" or input_message == "давай" or input_message == "согласен":
                        if credit[0] == "0":
                            index = database.get_entry("users_info", ['Lvl'],
                                                       {'request_id': request.user_id})[0][0]
                            credit = read_answers_data("data/profit_page_list")["credit"][index]
                            output_message = "Ваша сумма денег на руках увеличилась и теперь составляет {}р.\n" \
                                             "Вам выдан кредит на сделующих условиях: \n Выдаваемая сумма: {}" \
                                             " \n Процентная ставка: {} \n Срок выплаты: {} \n" \
                                             " \n Доступные команды: Назад, Следующий день".format(
                                money + int(credit[0]),credit[0], credit[1], credit[2]
                            )
                            database.update_entries('users_info', request.user_id,
                                                    {'Money': money + int(credit[0])},
                                                    update_type='rewrite')
                            database.update_entries('users_info', request.user_id,
                                                    {'Credit': "#$".join(credit)},
                                                    update_type='rewrite')
                        else:
                            output_message = "Выдача нового кредита в данный момент недоступна, так как имеется задолжность. \nДоступные команды: Назад, Следующий день"
                        buttons, user_storage = get_suggests(user_storage)
                        return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

                    buttons, user_storage = get_suggests(user_storage)
                    return IDontUnderstand(response, user_storage)

    if handler.startswith("education_page"):
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
        if handler == "null":
            user_storage['suggests'] = [
                "Основная информация",
                "Источник дохода",
                "Образование и курсы",
                "Помощь",
                "Следующий день"
            ]

            handler = "other->other_next"

            output_message = "Похоже, мы вернулись в начало. \n Доступные опции: {}".format(
                ", ".join(user_storage['suggests']))

            buttons, user_storage = get_suggests(user_storage)
            return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

        if handler == "education_page":
            exp = database.get_entry("users_info", ['Exp'],
                                                       {'request_id': request.user_id})[0][0]
            current_education = database.get_entry("users_info", ['current_education'],
                                                {'request_id': request.user_id})[0][0].split("#$")
            current_education = "В данный момент получаете: " + "{}. Оставшееся время: {}".format(current_education[0],
                                                                                                  current_education[1]) if \
                len(current_education) > 1 else current_education[0]
            current_education = current_education if not current_education.endswith('null') else \
                " Последнее полученное образование " + database.get_entry("users_info", ['education'],{'request_id': request.user_id})[0][0].split("#$")[-1]
            current_education = current_education if not current_education.endswith("null") else "Отсутствтвует"

            current_course =database.get_entry("users_info", ['current_course'],
                                                       {'request_id': request.user_id})[0][0].split("#$")
            current_course = "В данный момент проходите: " + "{}. Оставшееся время: {}".format(current_course[0],
                                                                                               current_course[2]) if \
                len(current_course) > 1 else current_course[0]
            current_course = current_course if not current_course.endswith('null') else \
                "Последний пройденный курс: " + database.get_entry("users_info", ['course'],
                                                       {'request_id': request.user_id})[0][0].split("#$")[-1]
            current_course = current_course if not current_course.endswith('null') else "Отсутствуют"

            books = database.get_entry("users_info", ['books'],
                                                       {'request_id': request.user_id})[0][0].split("#$")[-1]
            books = books if not books.endswith('null') else "Отсутствует"

            lvl = database.get_entry("users_info", ['Lvl'],
                                                       {'request_id': request.user_id})[0][0]
            handler += "->education_next"
            user_storage['suggests'] = ["Получить образование", "Пройти курс", "Прочесть книгу", "Назад", "Следующий день"]
            if "#$" not in current_course:
                output_message = "Ваш опыт: {}. \n Ваш уровень: {} \nИнформация об образовании: {}. \nИнформация о крусах: {}. \n Последняя " \
                                 "прочитанная книга: {}. \n Доступные команды: Назад, Следующий день".format(exp, lvl, current_education, current_course, books)
            else:

                output_message = "Ваш опыт: {}. \n Ваш уровень: {} \nИнформация об образовании: {}. \nИнформация о крусах: {}. \n Последняя " \
                                 "прочитанная книга: {}. \n Доступные команды: Назад, Следующий день".format(exp, lvl, current_education, current_course, books)
            buttons, user_storage = get_suggests(user_storage)
            return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

        if handler.endswith("->education_next"):
            if (input_message == "получить образование" or "образование" in input_message) and "не " not in input_message:
                handler += "->get_educated"
            elif (input_message == "пройти курс" or "курсы" in input_message or  "курс" in input_message) and "не " not in input_message:
                handler += "->get_course"
            elif (input_message == "прочесть книгу" or "книгу" in input_message or "книга" in input_message) and "не " not in input_message:
                handler += "->buy_book"
        if handler.count("educated"):
            if handler.endswith("educated"):
                current_education = database.get_entry("users_info", ['current_education'],
                                                       {'request_id': request.user_id})[0][0].split("#$")
                current_education = "В данный момент получаете: " + "{}. Оставшееся время: {}".format(
                    current_education[0],
                    current_education[1]) if \
                    len(current_education) > 1 else current_education[0]
                current_education = current_education if not current_education.endswith("null") else "Отсутствтвует"
                available_education = read_answers_data("data/education_page_list")["education"]
                handler += "->next"
                if not current_education.startswith("В данный"):
                    dct_k = [str(j) for j in sorted([int(i) for i in available_education.keys()])]
                    for i in dct_k:
                        if current_education in available_education[i]:
                            num = i
                            break
                    else:
                        num = "1"
                    if int(num)+1 < len(available_education):
                        available = dct_k[int(num):]
                        education = database.get_entry("users_info", ['education'],
                                                       {'request_id': request.user_id})[0][0].split("#$")
                        education = education if education[0] != "null" else ["Отсутствует"]
                        edc = ["{}. \nДлительность обучения: {}. \nЦена обучения: {}. \nПолучаемый опыт: {}".format(
                            available_education[i][0], available_education[i][1], available_education[i][2], available_education[i][3])
                            for i in available]
                        user_storage["suggests"] = [available_education[i][0] for i in available] + ["Назад", "Следующий день"]
                        output_message = "Полученное образование: {}. \n Доступное к получению: {}. \nДоступные команды: Назад, Следующий день"\
                            .format("\n".join(education) if education else "Отсутствует", "\n".join(edc))
                    else:
                        user_storage["suggests"] = ["Назад", "Следующий день"]
                        output_message = "Вы уже получили максимально возможное образование.".format(
                            current_education
                        )
                else:
                    output_message = current_education+" Дождитесь окончания обучения."

                buttons, user_storage = get_suggests(user_storage)
                return message_return(response, user_storage, output_message, buttons, database, request,
                                                handler, warning_message, congrats)

            if handler.endswith("next"):
                current_education = "В данный момент получаете: " + \
                                    database.get_entry("users_info", ['current_education'],
                                                       {'request_id': request.user_id})[0][0].split("#$")[0]
                current_education = current_education if not current_education.endswith('null') else \
                    database.get_entry("users_info", ['education'], {'request_id': request.user_id})[0][0].split("#$")[
                        -1]
                current_education = current_education if not current_education.endswith("null") else "Отсутствтвует"
                available_education = read_answers_data("data/education_page_list")["education"]
                if not current_education.startswith("В данный"):
                    dct_k = [str(j) for j in sorted([int(i) for i in available_education.keys()])]
                    for i in dct_k:
                        if current_education in available_education[i]:
                            num = i
                            break
                    else:
                        num = "1"
                    if int(num) + 1 < len(available_education):
                        available = dct_k[int(num):]
                        education = database.get_entry("users_info", ['education'],
                                                       {'request_id': request.user_id})[0][0].split("#$")
                        for i in education:
                            if request.command in i:
                                user_storage["suggests"] =[available_education[i][0] for i in available] + ["Назад", "Следующий день"]
                                edc = ["{}. \nДлительность обучения: {}. \nЦена обучения: {}. \nПолучаемый опыт: {}".format(
                                    available_education[i][0], available_education[i][1], available_education[i][2],
                                    available_education[i][3])
                                    for i in available]
                                output_message = "{} уже имеется, выберите другой вариант. \n Доступное к получению: {}".format(i, "\n".join(edc))
                                buttons, user_storage = get_suggests(user_storage)
                                return message_return(response, user_storage, output_message, buttons,
                                                                database, request,
                                                                handler, warning_message, congrats)
                        for i in available:
                            print(request.command, available_education[i][0])
                            if request.command.lower() in available_education[i][0].lower():
                                money = database.get_entry("users_info", ['Money'],
                                                       {'request_id': request.user_id})[0][0]
                                if money >= int(available_education[i][2]):
                                    chosen_edc = "{}#${}#${}".format(available_education[i][0], available_education[i][1], available_education[i][3])
                                    database.update_entries('users_info', request.user_id,
                                                            {'Money': money - int(available_education[i][2])},
                                                            update_type='rewrite')
                                    database.update_entries('users_info', request.user_id,
                                                            {'current_education': chosen_edc},
                                                            update_type='rewrite')
                                    output_message = "Вы начали получать образование {}. \nОставшиеся деньги: {}" \
                                                     " Доступные команды: Назад".format(
                                        available_education[i][0], money - int(available_education[i][2]))
                                else:
                                    output_message = "Вы не можете обучаться в связи с нехваткой денег, не хватает: {}" \
                                                     ". \nДоступные команды: Назад".format(
                                        int(available_education[i][2]) - money
                                    )
                                break
                        else:
                            print(input_message)
                            output_message = "{} не было найдено в списке доступных образований к получению".format(input_message)

                        user_storage["suggests"] = ["Назад"]
                    else:
                        user_storage["suggests"] = ["Назад"]
                        output_message = "Вы уже получили максимально возможное образование.".format(
                            current_education
                        )
                else:
                    output_message = current_education + " Дождитесь окончания обучения."

                buttons, user_storage = get_suggests(user_storage)
                return message_return(response, user_storage, output_message, buttons, database, request,
                                                handler, warning_message, congrats)

        if handler.count("course"):
            if handler.endswith("course"):
                current_course = database.get_entry("users_info", ['current_course'],
                                                    {'request_id': request.user_id})[0][0].split("#$")
                current_course = "В данный момент проходите: " + "{}. Оставшееся время: {}".format(current_course[0],
                                                                                                   current_course[2]) if \
                    len(current_course) > 1 else current_course[0]
                current_course = current_course if not current_course.endswith("null") else "Отсутствтвует"
                if not current_course.startswith("В данный"):
                    index = database.get_entry("users_info", ['Lvl'],
                                               {'request_id': request.user_id})[0][0]
                    education = database.get_entry("users_info", ['current_course'],
                                                   {'request_id': request.user_id})[0][0].split("#$")
                    education = education if education[0] != "null" else ["Отсутствует"]
                    available_course = read_answers_data("data/education_page_list")["courses"]
                    courses = []
                    if index == "0":
                        courses = [[i, available_course["0"][i][0], available_course["0"][i][1],
                                    available_course["0"][i][2]] for i in available_course["0"].keys()\
                                   if i not in education]
                    else:
                        for i in range(int(index) + 1):
                            for j in available_course[str(i)].keys():
                                courses.append([j, available_course[str(i)][j][0], available_course[str(i)][j][1],
                                                available_course[str(i)][j][2]])
                    handler += "->next"
                    if courses:
                        edc = ["{}. \nДлительность курса: {}. \nЦена курса: {}. \nПолучаемый опыт: {}.".format(i[0], i[3], i[1], i[2]) for i in courses][:5]
                        user_storage["suggests"] = [i[0] for i in courses][:5] + ["Назад", "Следующий день"]
                        output_message = "Пройденные курсы: {}. \n Список доступных курсов: {}. \nДоступные команды: Назад, Следующий день" \
                            .format("\n".join(education) if education else "Отсутствует", "\n".join(edc))
                    else:
                        user_storage["suggests"] = ["Назад", "Следующий день"]
                        output_message = "Вы прошли максимально доступное количество курсов, повысьте уровень," \
                                         " чтобы получить новые."
                else:
                    user_storage["suggests"] = ["Назад", "Следующий день"]
                    output_message = current_course + ". Доступные команды: Назад, Следующий день"

                buttons, user_storage = get_suggests(user_storage)
                return message_return(response, user_storage, output_message, buttons, database, request,
                                                handler, warning_message, congrats)

            if handler.endswith("next"):
                current_course = database.get_entry("users_info", ['current_course'],
                                                    {'request_id': request.user_id})[0][0].split("#$")
                current_course = "В данный момент проходите: " + "{}. Оставшееся время: {}".format(current_course[0],
                                                                                                   current_course[2]) if \
                    len(current_course) > 1 else current_course[0]
                current_course = current_course if not current_course.endswith("null") else "Отсутствтвует"
                if not current_course.startswith("В данный"):
                    index = database.get_entry("users_info", ['Lvl'],
                                               {'request_id': request.user_id})[0][0]
                    education = database.get_entry("users_info", ['current_course'],
                                                   {'request_id': request.user_id})[0][0].split("#$")
                    education = education if education[0] != "null" else ["Отсутствует"]
                    available_course = read_answers_data("data/education_page_list")["courses"]
                    courses = []
                    if index == "0":
                        courses = [[i, available_course["0"][i][0], available_course["0"][i][1],
                                    available_course["0"][i][2]] for i in available_course["0"].keys() \
                                   if i not in education]
                    else:
                        for i in range(int(index) + 1):
                            for j in available_course[str(i)].keys():
                                if j not in education:
                                    courses.append([j, available_course[str(i)][j][0], available_course[str(i)][j][1],
                                                    available_course[str(i)][j][2]])
                    if courses:
                        for i in courses:
                            print(i, request.command)
                            if request.command in i[0].lower():
                                money = database.get_entry("users_info", ['Money'],
                                                       {'request_id': request.user_id})[0][0]
                                if money >= int(i[1]):
                                    chosen_course = "{}#${}#${}".format(i[0], i[2], i[3])
                                    database.update_entries('users_info', request.user_id,
                                                            {'Money': money - int(i[1])},
                                                            update_type='rewrite')
                                    database.update_entries('users_info', request.user_id,
                                                            {'current_course': chosen_course},
                                                            update_type='rewrite')
                                    user_storage['suggests'] = ['Назад', 'Следующий день']
                                    output_message = "Вы начали прохождение курса {}. \nОставшиеся деньги: {} \nДоступные команды: Назад," \
                                                     " Следующий день".format(i[0], money - int(i[1]))
                                else:
                                    output_message = "Вы не можете обучаться в связи с нехваткой денег, не хватает: {}" \
                                                     ". \nДоступные команды: Назад, Следующий день".format(
                                        money - int(i[1])
                                    )
                                break
                        else:
                            edc = ["{}. Длительность курса: {}. Цена курса: {}".format(i[0], i[1], i[2]) for i in courses][:5]
                            user_storage["suggests"] = [i[0] for i in courses][:5] + ["Назад", "Следующий день"]
                            output_message = "Курс {} не был найден. Список доступных курсов: {}. \nДоступные команды: Назад, Следующий день" \
                                .format(input_message, "\n".join(edc))
                    else:
                        user_storage["suggests"] = ["Назад", "Следующий день"]
                        output_message = "Вы прошли максимально доступное количество курсов, повысьте уровень," \
                                         " чтобы получить новые."
                else:
                    user_storage["suggests"] = ["Назад", "Следующий день"]
                    output_message = current_course+". \nДоступные команды: Назад, Следующий день"

                buttons, user_storage = get_suggests(user_storage)
                return message_return(response, user_storage, output_message, buttons, database, request,
                                                handler, warning_message, congrats)

        if handler.count("book"):
            if handler.endswith("book"):
                handler += "->next"
                index = database.get_entry("users_info", ['Lvl'],
                                           {'request_id': request.user_id})[0][0]
                books = database.get_entry("users_info", ['current_course'],
                                               {'request_id': request.user_id})[0][0].split("#$")
                books = books if books[0] != "null" else ["Отсутствует"]
                available_books = []
                user_storage["suggests"] = ["Назад", "Следующий день"]
                av_bk = []
                if index == "0":
                    jsn = read_answers_data("data/education_page_list")["books"]["0"]
                    for i in jsn.keys():
                        if i not in books:
                            available_books.append(i)
                            av_bk.append("{} Цена: {}. \nПолучаемый опыт: {}".format(i, jsn[i][0], jsn[i][1]))
                else:
                    for i in range(int(index) + 1):
                        jsn = read_answers_data("data/education_page_list")["books"][str(i)]
                        for j in jsn.keys():
                            if j not in books:
                                available_books.append(j)
                                av_bk.append("{} Цена: {}. \nПолучаемый опыт: {}".format(j, jsn[j][0], jsn[j][1]))
                if available_books:
                    user_storage['suggests'] += available_books[:5]
                    output_message = "Последняя прочитанная книга: {} \nПопулярные книги: {} \n" \
                                     "Выберите желаемую; eсли вам для работы выдвинули требование прочитать какую-то" \
                                     " определённую, но её нет в списке - также дайте название, мы найдем её по общему" \
                                     " каталогу. \тДоступные команды: Назад, Следующий день".format(books[-1], "\n".join(av_bk[:5]))
                else:
                    output_message = "Последняя прочитанная книга: {}. \n Вы прочитали максимально возможное количество" \
                                     "книг для вашего уровня. \тДоступные команды: Назад, Следующий день"

                buttons, user_storage = get_suggests(user_storage)
                return message_return(response, user_storage, output_message, buttons, database, request,
                                            handler, warning_message, congrats)

        if handler.endswith("next"):
            index = database.get_entry("users_info", ['Lvl'],
                                       {'request_id': request.user_id})[0][0]
            books = database.get_entry("users_info", ['current_course'],
                                       {'request_id': request.user_id})[0][0].split("#$")
            books = books if books[0] != "null" else ["Отсутствует"]
            available_books = []
            av_bk = []
            if index == "0":
                jsn = read_answers_data("data/education_page_list")["books"]["0"]
                for i in jsn.keys():
                    if i not in books:
                        available_books.append(i)
                        av_bk.append("{} Цена: {}. \nПолучаемый опыт: {}".format(i, jsn[i][0], jsn[i][1]))
            else:
                for i in range(int(index) + 1):
                    jsn = read_answers_data("data/education_page_list")["books"][str(i)]
                    for j in jsn.keys():
                        if j not in books:
                            available_books.append(j)
                            av_bk.append("{} Цена: {}. \nПолучаемый опыт: {}".format(j, jsn[j][0], jsn[j][1]))
            if available_books:
                for i in available_books:
                    if input_message in i.lower():
                        money = database.get_entry("users_info", ['Money'],
                                       {'request_id': request.user_id})[0][0]
                        for p in range(int(index) + 1):
                            jsn = read_answers_data("data/education_page_list")["books"][str(p)]
                            for j in jsn.keys():
                                if i in j:
                                    product = jsn[j]
                                    break
                        if money - int(product[0]) > 0:
                            if books[0] == "Отсутствует":
                                books = [i]
                            else:
                                books.append(i)
                            database.update_entries('users_info', request.user_id,
                                                    {'Money': money - int(product[0])},
                                                    update_type='rewrite')
                            database.update_entries('users_info', request.user_id,
                                                    {'books': "#$".join(books)},
                                                    update_type='rewrite')
                            exp = database.get_entry("users_info", ['Exp'],
                                       {'request_id': request.user_id})[0][0] + int(product[1])
                            database.update_entries('users_info', request.user_id,
                                                    {'Exp': exp},
                                                    update_type='rewrite')
                            output_message = "Книга {} успешно приобретена. Ваш опыт повысился и составляет: {}. " \
                                             "\nОставшиеся деньги: {}".format(i, exp, money - int(product[0]))
                        else:
                            user_storage['suggests'] += available_books[:5]
                            output_message = "Недостаточно денег для покупки книги, не хватает: {}. \n Другие популярные" \
                                             " книги: {}. \nДоступные команды: Назад, Следующий день".format(int(product[0])-money, "\n".join(av_bk[:5]))
                        break
                else:
                    user_storage['suggests'] += available_books[:5]
                    output_message = "Книга {} не найдена. \nДругие популярные книги: {}. \nДоступные команды: Назад, Следующий день".format(input_message,
                                                                                                  "\n".join(av_bk[:5]))
            else:
                output_message = "Последняя прочитанная книга: {}. \n Вы прочитали максимально возможное количество" \
                                 "книг для вашего уровня. \nДоступные команды: Назад, Следующий день"

            buttons, user_storage = get_suggests(user_storage)
            return message_return(response, user_storage, output_message, buttons, database, request,
                                            handler, warning_message, congrats)


    update_handler(handler, database, request)

    if input_message in ['нет', 'не хочется', 'в следующий раз', 'выход', "не хочу", 'выйти']:
        choice = random.choice(aliceAnswers["quitTextVariations"])
        response.set_text(aliceSpeakMap(choice))
        response.set_tts(aliceSpeakMap(choice,True))
        response.end_session = True
        return response, user_storage

    buttons, user_storage = get_suggests(user_storage)
    return IDontUnderstand(response, user_storage)


def get_suggests(user_storage):
    if "suggests" in user_storage.keys():
        suggests = [
            {'title': suggest, 'hide': True}
            for suggest in user_storage['suggests']
        ]
    else:
        suggests = []

    return suggests, user_storage
