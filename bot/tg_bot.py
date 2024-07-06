import telebot
from telebot import types
from values import TELEGRAM_BOT_TOKEN
from db.db import cursor, conn
from pars import fetch_vacancies


bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

user_states = {}

vacancy_name = None
salary_from = None
salary_to = None
currency = None
city = None

def start_markup():
    markup = types.InlineKeyboardMarkup(row_width=True)
    link_keyboard = types.InlineKeyboardButton(text="Начать поиск!", callback_data="job")
    markup.add(link_keyboard)
    return markup

def start_markup2():
    markup = types.InlineKeyboardMarkup(row_width=True)
    start_button = types.InlineKeyboardButton(text="Старт", callback_data="start")
    markup.add(start_button)
    return markup

def next_markup1():
    markup = types.InlineKeyboardMarkup(row_width=True)
    next1 = types.InlineKeyboardButton(text="Пропустить вопрос", callback_data="next1")
    markup.add(next1)
    return markup

def next_markup2():
    markup = types.InlineKeyboardMarkup(row_width=True)
    next2 = types.InlineKeyboardButton(text="Пропустить вопрос", callback_data="next2")
    back2 = types.InlineKeyboardButton(text="Вернуться назад", callback_data="back2")
    markup.add(next2, back2)
    return markup

def next_markup3():
    markup = types.InlineKeyboardMarkup(row_width=True)
    next3 = types.InlineKeyboardButton(text="Пропустить вопрос", callback_data="next3")
    back3 = types.InlineKeyboardButton(text="Вернуться назад", callback_data="back3")
    markup.add(next3, back3)
    return markup

def next_markup4():
    markup = types.InlineKeyboardMarkup(row_width=True)
    next4 = types.InlineKeyboardButton(text="Пропустить вопрос", callback_data="next4")
    back4 = types.InlineKeyboardButton(text="Вернуться назад", callback_data="back4")
    markup.add(next4, back4)
    return markup

def next_markup5():
    markup = types.InlineKeyboardMarkup(row_width=True)
    next5 = types.InlineKeyboardButton(text="Пропустить вопрос", callback_data="next5")
    markup.add(next5)
    return markup

def next_markup6():
    markup = types.InlineKeyboardMarkup(row_width=True)
    next6 = types.InlineKeyboardButton(text="Пропустить вопрос", callback_data="next6")
    markup.add(next6)
    return markup

def next_markup7():
    markup = types.InlineKeyboardMarkup(row_width=True)
    next7 = types.InlineKeyboardButton(text="Пропустить вопрос", callback_data="next7")
    markup.add(next7)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    cursor.execute("""CREATE TABLE IF NOT EXISTS user_answers(user_id INTEGER, vacancy_name TEXT, salary_from TEXT, salary_to TEXT, currency TEXT, city TEXT)""")
    cursor.execute("""
            INSERT INTO user_answers (user_id, vacancy_name, salary_from, salary_to, currency, city)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, 0, 0, 0, 0, 0))
    conn.commit()
    bot.send_message(message.chat.id, f'Здравствуй, {message.from_user.first_name}!\n'
                     f'Бот создан для поиска вакансий', reply_markup=start_markup())
    cursor.execute("""CREATE TABLE IF NOT EXISTS login_id(
        id SERIAL PRIMARY KEY, user_id BIGINT
    )""")
    conn.commit()
    people_id = message.chat.id
    cursor.execute(f"SELECT id FROM login_id WHERE user_id = {people_id}")
    data = cursor.fetchone()
    if data is None:
        user_id = message.chat.id
        cursor.execute("INSERT INTO login_id (user_id) VALUES(%s);", (user_id,))
        conn.commit()

def ask_question(chat_id, question, next_step_handler, markup=None):
    msg = bot.send_message(chat_id, question, reply_markup=markup)
    user_states[chat_id] = next_step_handler
    bot.register_next_step_handler(msg, handle_response)

def handle_response(message):
    chat_id = message.chat.id
    if chat_id in user_states:
        next_step_handler = user_states.pop(chat_id)
        next_step_handler(message)

def salary_from_def(message):
    if message.text:
        bot.send_message(message.chat.id, "Подождите, идет загрузка вакансий")
        fetch_vacancies(message.text, message.chat.id)
        cursor.execute("SELECT * FROM information_schema.tables WHERE table_name = %s", ('vacancies',))
        if cursor.fetchone():
            user_id = message.chat.id
            cursor.execute("UPDATE user_answers SET vacancy_name = %s WHERE user_id = %s;", (message.text, user_id))
            conn.commit()
            ask_question(message.chat.id, "От какой зарплаты мне искать вакансию?", salary_to_def, next_markup1())
        else:
            message = bot.send_message(message.chat.id, f"Такой вакансии не существует\n"
                            "Попробуйте снова")
            bot.register_next_step_handler(message, salary_from_def)
        
def salary_to_def(message):
    if message.text:
        user_id = message.chat.id
        cursor.execute("UPDATE user_answers SET salary_from = %s WHERE user_id = %s;", (message.text, user_id))
        conn.commit()
        ask_question(message.chat.id, "До какой зарплаты мне искать вакансию?", currency_def, next_markup2())

def salary_to2_def(message):
    if message.text:
        user_id = message.chat.id
        cursor.execute("UPDATE user_answers SET salary_from = %s WHERE user_id = %s;", (message.text, user_id))
        conn.commit()
        ask_question(message.chat.id, "До какой зарплаты мне искать вакансию?", currency_def, next_markup2())

def currency_def(message):
    if message.text:
        user_id = message.chat.id
        cursor.execute("UPDATE user_answers SET salary_to = %s WHERE user_id = %s;", (message.text, user_id))
        conn.commit()
        ask_question(message.chat.id, f"В какой валюте мне искать?(currency_def)\n"
                    "Ответить можно только RUR, KZT, EUR или USD", city_def, next_markup3())
        
def currency2_def(message):
    if message.text:
        user_id = message.chat.id
        cursor.execute("UPDATE user_answers SET salary_to = %s WHERE user_id = %s;", (message.text, user_id))
        conn.commit()
        ask_question(message.chat.id, f"В какой валюте мне искать?(currency2_def)\n"
                    "Ответить можно только RUR, KZT, EUR или USD", city_def, next_markup3())
        
def currency3_def(message):
    if message.text:
        user_id = message.chat.id
        cursor.execute("SELECT salary_to FROM user_answers WHERE user_id = %s;", (user_id,))
        result = cursor.fetchone()
        if result[0] == 0:
            cursor.execute("UPDATE user_answers SET salary_to = %s WHERE user_id = %s;", (0, user_id))
            conn.commit()
        else:
            ask_question(message.chat.id, f"В какой валюте мне искать?(currency3_def)\n"
                        "Ответить можно только RUR, KZT, EUR или USD", city_def, next_markup3())

def city_def(message):
    if message.text == "RUR" or message.text == "KZT" or message.text == "EUR" or message.text == "USD":
        user_id = message.chat.id
        cursor.execute("UPDATE user_answers SET currency = %s WHERE user_id = %s;", (message.text, user_id))
        conn.commit()
        ask_question(message.chat.id, "В каком городе искать вакансию?", finish_def, next_markup4())
    else:
        ask_question(message.chat.id, f"В какой валюте мне искать?(city_def)\n"
                    "Ответить можно только RUR, KZT, EUR или USD", city_def, next_markup3())
        
def city2_def(message):
    if message.text == "RUR" or message.text == "KZT" or message.text == "EUR" or message.text == "USD":
        user_id = message.chat.id
        cursor.execute("UPDATE user_answers SET currency = %s WHERE user_id = %s;", (message.text, user_id))
        conn.commit()
        ask_question(message.chat.id, "В каком городе искать вакансию?", finish_def, next_markup4())
    else:
        ask_question(message.chat.id, f"В какой валюте мне искать?(city2_def)\n"
                    "Ответить можно только RUR, KZT, EUR или USD", city2_def, next_markup3())
        
def city3_def(message):
    if message.text:
        user_id = message.chat.id
        cursor.execute("SELECT currency FROM user_answers WHERE user_id = %s;", (user_id,))
        result = cursor.fetchone()
        if result[0] == "0":
            cursor.execute("UPDATE user_answers SET currency = %s WHERE user_id = %s;", (0, user_id))
            conn.commit()
        else:
            ask_question(message.chat.id, "В каком городе искать вакансию?", finish_def, next_markup3())

def finish_def(message):
    if message.text:
        user_id = message.chat.id
        cursor.execute("UPDATE user_answers SET city = %s WHERE user_id = %s;", (message.text, user_id))
        conn.commit()
        finish_def2(message)
        
def finish_def2(message):
        # Retrieve values from user_answers table
        user_id = message.chat.id
        cursor.execute("SELECT user_id, vacancy_name, salary_from, salary_to, currency, city FROM user_answers WHERE user_id = %s;", (user_id,))
        row = cursor.fetchone()

        if row:
            user_id = row[0]
            vacancy_name = row[1]
            salary_from = row[2]
            salary_to = row[3]
            currency = row[4]
            city = row[5]

            # Construct SQL query to fetch vacancies
            sql_query = """
                SELECT v.vacancy_name, v.salary_from, v.salary_to, v.currency, v.city, v.metro, v.id
                FROM vacancies v 
                INNER JOIN user_answers u ON v.user_id_vac = u.user_id
                WHERE 1=1
                """

            conditions = []
            params = []

            # Conditions for salary_from, salary_to, currency, and city
            if int(salary_from) > 0:
                conditions.append("v.salary_from >= %s")
                params.append(salary_from)
            elif int(salary_from) == 0:
                conditions.append("1=1")  # При salary_from = 0 выбираем все записи
            if int(salary_to) > 0:
                conditions.append("v.salary_to <= %s")
                params.append(salary_to)
            elif int(salary_to) == 0:
                conditions.append("1=1")  # При salary_to = 0 выбираем все записи
            if currency != "0":
                conditions.append("v.currency = %s")
                params.append(currency)
            else:
                conditions.append("1=1")  # При currency = 0 выбираем все записи
            if city != "0":
                conditions.append("v.city = %s")
                params.append(city)
            else:
                conditions.append("1=1")  # При city = 0 выбираем все записи

            # Append conditions to SQL query
            if conditions:
                sql_query += " AND " + " AND ".join(conditions)

            sql_query += " ORDER BY v.id;"  # Order by vacancy ID for consistent pagination

            # Execute query and fetch results
            cursor.execute(sql_query, params)
            rows = cursor.fetchall()

            if rows:
                # Store the vacancies in user's session data for pagination
                user_states[user_id] = {
                    'vacancies': rows,
                    'index': 0  # Start index for pagination
                }

                # Send the first batch of vacancies (up to 10)
                send_vacancies(user_id)
            else:
                bot.send_message(user_id, "Подходящих вакансий не найдено.")
        else:
            bot.send_message(user_id, "Данные в таблице user_answers не найдены.")
            
def send_vacancies(user_id):
    # Retrieve stored vacancies and current index from session data
    session_data = user_states.get(user_id)
    if session_data:
        vacancies = session_data['vacancies']
        current_index = session_data['index']

        num_vacancies = len(vacancies)
        batch_size = 10

        # Correct the current_index if it goes below zero
        if current_index < 0:
            current_index = 0

        # Get the correct batch of vacancies to display
        batch = vacancies[current_index:current_index + batch_size]

        if not batch:
            bot.send_message(user_id, "Нет вакансий для отображения.")
            return

        for index, vacancy in enumerate(batch, start=current_index + 1):
            vacancy_message = f"<b>Вакансия {index}:</b>\n" \
                              f"<b>Вакансия:</b> {vacancy[0]}\n" \
                              f"<b>Зарплата от:</b> {vacancy[1]} <b>до:</b> {vacancy[2]} <b>валюта:</b> {vacancy[3]}\n" \
                              f"<b>Город:</b> {vacancy[4]}\n" \
                              f"<b>Metro:</b> {vacancy[5]}"

            # Inline keyboard for each vacancy
            inline_markup = types.InlineKeyboardMarkup()
            inline_markup.row(
                types.InlineKeyboardButton(text="Получить ссылку", callback_data=f"get_link_{index}")
            )

            bot.send_message(user_id, vacancy_message, parse_mode='HTML', reply_markup=inline_markup)

        # Update session data with new index
        session_data['index'] = current_index + batch_size
        user_states[user_id] = session_data

        # Prepare inline keyboard for navigation
        inline_markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = []

        if current_index + batch_size < num_vacancies:
            buttons.append(types.InlineKeyboardButton(text="Далее", callback_data="next_vacancies"))
        
        if current_index > 0:
            buttons.append(types.InlineKeyboardButton(text="Назад", callback_data="prev_vacancies"))

        buttons.append(types.InlineKeyboardButton(text="Завершить поиск", callback_data="finish_search"))
        inline_markup.add(*buttons)

        bot.send_message(user_id, "Выберите действие:", reply_markup=inline_markup)

   
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    currency_val = 0
    if call.data == 'start':
        start(call.message)
    elif call.data == 'job':
        ask_question(call.message.chat.id, "Отлично, напишите вакансию для поиска", salary_from_def)
    elif call.data == 'next1':
        cursor.execute("UPDATE user_answers SET salary_from = %s WHERE user_id = %s;", (currency_val, call.message.chat.id))
        conn.commit()
        ask_question(call.message.chat.id, "При пропуске ответа, будут выдаваться все возможные варианты поиска\n"
                                           "До какой зарплаты мне искать вакансию?", currency_def, next_markup2())
    elif call.data == 'next2':
        cursor.execute("UPDATE user_answers SET salary_to = %s WHERE user_id = %s;", (currency_val, call.message.chat.id))
        conn.commit()
        ask_question(call.message.chat.id,  "При пропуске ответа, будут выдаваться все возможные варианты поиска\n"
                                            "\n"
                                            "В какой валюте мне искать вакансию?(некст2)\n"
                                            "Ответить можно только RUR, KZT, EUR или USD", city_def, next_markup3())
    elif call.data == 'back2':
        ask_question(call.message.chat.id, "От какой зарплаты мне искать вакансию?(бэк)", salary_to2_def, next_markup5())
        
    elif call.data == 'next3':
        cursor.execute("UPDATE user_answers SET currency = %s WHERE user_id = %s;", (currency_val, call.message.chat.id))
        conn.commit()
        ask_question(call.message.chat.id, "При пропуске ответа, будут выдаваться все возможные варианты поиска\n"
                                           "В каком городе мне искать вакансию?", finish_def, next_markup4())
    elif call.data == 'back3':
        ask_question(call.message.chat.id, "До какой зарплаты мне искать вакансию?(бэк)", currency2_def, next_markup6())
        
    elif call.data == 'next4':
        cursor.execute("UPDATE user_answers SET city = %s WHERE user_id = %s;", (currency_val, call.message.chat.id))
        conn.commit()
        finish_def2(call.message)
        
    elif call.data == 'back4':
        ask_question(call.message.chat.id, f"В какой валюте мне искать вакансию?(бэк4)\n"
                    "Ответить можно только RUR, KZT, EUR или USD", city2_def, next_markup7())
        
    elif call.data == 'next5':
        ask_question(call.message.chat.id, "До какой зарплаты мне искать вакансию?(бэк)", currency_def, next_markup2())
        
    elif call.data == 'next6':
            ask_question(call.message.chat.id, f"В какой валюте мне искать вакансию?(next6)\n"
                        "Ответить можно только RUR, KZT, EUR или USD", city_def, next_markup3())
        
    elif call.data == 'next7':
        ask_question(call.message.chat.id, "В каком городе искать вакансию?", finish_def, next_markup4())
        
    elif call.data == 'next_vacancies':
        user_id = call.message.chat.id
        send_vacancies(user_id)
    elif call.data == 'prev_vacancies':
        user_id = call.message.chat.id
        session_data = user_states.get(user_id)
        if session_data:
            current_index = session_data.get('index', 0)
            current_index -= 20  # Move back two batches (to the previous batch of 10)
            if current_index < 0:
                current_index = 0  # Ensure the index does not go below 0
            session_data['index'] = current_index
            user_states[user_id] = session_data
            send_vacancies(user_id)
    elif call.data == 'finish_search':
        user_id = call.message.chat.id
        column_name1 = "user_id_vac"
        column_name2 = "user_id"
        value_to_delete = user_id
        delete_query = f"DELETE FROM vacancies WHERE {column_name1} = %s;"
        cursor.execute(delete_query, (value_to_delete,))
        delete_query2 = f"DELETE FROM user_answers WHERE {column_name2} = %s;"
        cursor.execute(delete_query2, (value_to_delete,))
        conn.commit()
        ask_question(call.message.chat.id, f"Поиск завершен\n"
                    "Чтобы начать новый поиск, просто нажми кнопку старт", start, start_markup2())
    elif call.data.startswith('get_link_'):
        try:
            parts = call.data.split('_')
            if len(parts) == 3:
                vacancy_index = int(parts[2]) - 1
                user_id = call.message.chat.id

                session_data = user_states.get(user_id)
                if session_data:
                    vacancies = session_data.get('vacancies', [])
                    if 0 <= vacancy_index < len(vacancies):
                        # Проверка, что ссылка существует в ожидаемом столбце (шестой столбец)
                        vacancy_link = vacancies[vacancy_index][6]
                        if vacancy_link:
                            bot.send_message(user_id, f"Ссылка на вакансию: {vacancy_link}")
                        else:
                            bot.send_message(user_id, "Ссылка на вакансию не найдена.")
                    else:
                        bot.send_message(user_id, "Неверный номер вакансии.")
        except Exception as e:
            print(f"Ошибка обработки колбэка get_link: {e}")

bot.polling(none_stop=True)