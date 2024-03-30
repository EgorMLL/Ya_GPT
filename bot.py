from config import *
from Logging import *
from database import *
import telebot
import requests

API_TOKEN = TOKEN
bot = telebot.TeleBot(API_TOKEN)

users_history = {}
create_table()
create_table2()

CONTINUE_STORY = 'Продолжи сюжет в 1-3 предложения и оставь интригу. Не пиши никакой пояснительный текст от себя'
END_STORY = 'Напиши завершение истории c неожиданной развязкой. Не пиши никакой пояснительный текст от себя'

SYSTEM_PROMPT = (
    "Ты пишешь историю вместе с человеком. "
    "Историю вы пишете по очереди. Начинает человек, а ты продолжаешь. "
    "Если это уместно, ты можешь добавлять в историю диалог между персонажами. "
    "Диалоги пиши с новой строки и отделяй тире. "
    "Не пиши никакого пояснительного текста в начале, а просто логично продолжай историю."
)



@bot.message_handler(commands=['debug'])
def send_logs(message):
    with open("log_file.txt", "rb") as f:
        bot.send_document(message.chat.id, f)


@bot.message_handler(commands=["start"])
def start(message):
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    name = message.from_user.first_name
    markup.add("/help")
    logging.info("Функция start сработала")
    bot.send_message(message.chat.id, f"Приветствую, {name}, рад знакомству! Я бот - сценарист, основанный на нейросети. Моя нейросеть может генерировать истории на ваш вкус!"
                                      "Ознакомтесь со списком моих команд по команде /help", reply_markup=markup)


@bot.message_handler(commands=["help"])
def help(message):
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("/new_story")
    markup.add("/debug")
    logging.info("Функция help сработала")
    bot.send_message(message.chat.id, "Конечно! Вот список моих комманд:\n"
                                      "/debug - откладка об ошибках.\n"
                                      "/new_story - генерация новой истории и подбирание промтов для неё.\n"
                                      , reply_markup=markup)



def end_task_all(message):
    level = message.text
    return level in message.text.lower()


def filter_hello(message):
    word = "прив"
    return word in message.text.lower()

def filter_bye(message):
    word = "пок"
    return word in message.text.lower()


def record2(message):
    level = message.text
    return level in message.text.lower()


def func(message):
    user_promt = message.text
    return user_promt in message.text.lower()




def ask_gpt2(collection, mode='continue'):
    """Запрос к YandexGPT"""


    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    data = {
        "modelUri": f"gpt://{folder_id}/yandexgpt/latest",
        "completionOptions": {"stream": False, "temperature": 0.6, "maxTokens": 200},
        "messages": []
    }

    for row in collection:
        content = row['content']
        if mode == 'continue' and row['role'] == 'user':
            content += '\n' + CONTINUE_STORY
        elif mode == 'end' and row['role'] == 'user':
            content += '\n' + END_STORY
        data["messages"].append({"role": row["role"], "text": content})

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            return f"Status code {response.status_code}."
        return response.json()['result']['alternatives'][0]['message']['text']
    except Exception as e:
        return "Произошла непредвиденная ошибка."


user_data = {

    '': {
        'genre': "",
        'character': "",
        'setting': "",
        'additional_info': ""}}


def create_prompt(user_data, user_id):

    results = select_data_all(user_id)
    value = results.fetchall()[0]
    genre = value[2]
    main_character = value[3]
    place = value[4]
    info = value[5]

    user_data = {

        user_id: {
            'genre': genre,
            'character': main_character,
            'setting': place,
            'additional_info': info}}




    prompt = SYSTEM_PROMPT


    prompt += (f"\nНапиши начало истории в стиле {user_data[user_id]['genre']} "
               f"с главным героем {user_data[user_id]['character']}. "
               f"Вот начальный сеттинг: \n{user_data[user_id]['setting']}. \n"
               "Начало должно быть коротким, 1-3 предложения.\n")


    if user_data[user_id]['additional_info']:
        prompt += (f"Также пользователь попросил учесть "
                   f"следующую дополнительную информацию: {user_data[user_id]['additional_info']} ")


    prompt += 'Не пиши никакие подсказки пользователю, что делать дальше. Он сам знает'

    return prompt



@bot.message_handler(commands=['new_story'])
def record(message):
    user_id = message.from_user.id
    genre = ""
    the_main_character = ""
    place = ""
    info = ""
    update_all(user_id, genre, the_main_character, place, info)
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

    markup.add("Фентези")
    markup.add("Страшилка")
    markup.add("Комедия")

    logging.info("Функция new_story сработала")
    bot.send_message(message.chat.id, 'Выбери жанр своей истории:',
                     reply_markup=markup)
    bot.register_next_step_handler(message, record_story)









@bot.message_handler(commands=['get_promt'])
def prompt_gpt(message):

    user_id = message.from_user.id
    prompt = create_prompt(user_data, user_id)
    bot.send_message(message.chat.id, "Введи начало истории")
    collection = [{'role': 'user', 'content': prompt}]
    bot.register_next_step_handler(message, prompt_gpt2)

@bot.message_handler(func=prompt_gpt)
def prompt_gpt2(message):

    text = message.text

    user_id = message.from_user.id

    prompt = create_prompt(user_data, user_id)

    prompt += text

    collection = [{'role': 'user', 'content': prompt}]

    response = ask_gpt2(collection, mode='continue')

    bot.send_message(message.chat.id, f"Первое продолжение истории:\n{response}\n")

    collection.append({'role': 'assistant', 'content': response})  # Добавляем ответ в collection.

    bot.send_message(message.chat.id, "Введи продолжение истории")

    bot.register_next_step_handler(message, prompt_gpt3)

@bot.message_handler(func=prompt_gpt2)
def prompt_gpt3(message):
    text = message.text

    user_id = message.from_user.id

    prompt = create_prompt(user_data, user_id)

    prompt += text

    collection = [{'role': 'user', 'content': prompt}]

    response = ask_gpt2(collection, mode='continue')

    bot.send_message(message.chat.id, f"Второе продолжение истории:\n{response}\n")

    collection.append({'role': 'assistant', 'content': response})

    bot.register_next_step_handler(message, prompt_gpt4)

@bot.message_handler(func=prompt_gpt3)
def prompt_gpt4(message):
    text = message.text

    user_id = message.from_user.id

    prompt = create_prompt(user_data, user_id)

    prompt += text

    collection = [{'role': 'user', 'content': prompt}]

    response = ask_gpt2(collection, mode='end')
    bot.send_message(message.chat.id, f"Завершение истории:\n{response}\n")
    collection.append({'role': 'assistant', 'content': response})
    bot.register_next_step_handler(message, end_story)



@bot.message_handler(func=prompt_gpt4)
def end_story(message):
    bot.send_message(message.chat.id, f"История была завершена!\n"
                                      "Если вы хотите заново сгенерировать историю, пропишите команду /new_story")



@bot.message_handler(func=record)
def record_story(message):
    user_id = message.from_user.id
    genre = message.text
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)



    update_genre(genre, user_id)
    select_data_genre(user_id)

    markup.add("Илон Маск")
    markup.add("Томас Шелби")
    markup.add("Сталин")
    markup.add("Леонардо Да Винчи")
    bot.send_message(message.chat.id, 'Теперь выбери главного героя своей истории (можешь написать своего):',
                     reply_markup=markup)
    bot.register_next_step_handler(message, record_the_main_character)
    logging.info("Функция record_story сработала")


@bot.message_handler(func=record_story)
def record_the_main_character(message):
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    the_main_character = message.text
    user_id = message.from_user.id

    update_data_the_main_character(user_id, the_main_character)

    markup.add("Город")
    markup.add("Магический мир")
    markup.add("Луна")

    bot.send_message(message.chat.id, 'Данные успешно сохранены!')
    bot.send_message(message.chat.id, 'Выберите место, в котором будет проимходить история (можешь написать своё):',
                     reply_markup=markup)
    logging.info("Функция record_the_main_character сработала")
    bot.register_next_step_handler(message, record_place)


@bot.message_handler(func=record_the_main_character)
def record_place(message):
    place = message.text
    user_id = message.from_user.id

    update_place(user_id, place)

    bot.send_message(message.chat.id, 'Данные успешно сохранены!')
    bot.send_message(message.chat.id,
                     'Если хочешь чтобы в истории была ещё какая то дополнительная информация то можешь написать её сейчас\n'
                     'Или можешь сразу перейти к генерации истории, написав команду /begin')
    bot.register_next_step_handler(message, record_info)
    logging.info("Функция record_place сработала")



@bot.message_handler(func=record_place)
def record_info(message):
    user_id = message.from_user.id
    info = message.text
    if info == "/begin":
        logging.info("Перенос на комманду /begin прошёл успешно.")
        bot.register_next_step_handler(message, complete)
        return
    else:
        update_info(user_id, info)
        bot.send_message(message.chat.id, 'Данные успешно сохранены!')
        bot.send_message(message.chat.id,
                         'Если хочешь чтобы в истории была ещё какая то дополнительная информация то можешь написать её сейчас'
                         'Или можешь сразу перейти к генерации истории, написав команду /begin')
        bot.register_next_step_handler(message, record_info)
        logging.info("Функция record_info сработала")



@bot.message_handler(func=record_info)
def complete(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, 'Введите команду /get_promt, чтобы получить сгенерированный текст\n'
                                      'Внимание! Всего кусочков генерации истории от нейросети 3 штуки. (для экономии токенов)')




@bot.message_handler(content_types=['text'], func=filter_hello)
def say_hello(message):
    name = message.from_user.first_name
    markup.add("/start")
    bot.send_message(message.from_user.id, text=f"Приветствую, {name}! Если вы ещё не ознакомленны со мной, то введите команду /start", reply_markup=markup)

@bot.message_handler(content_types=['text'], func=filter_bye)
def say_hello(message):
    user_name = message.from_user.first_name
    bot.send_message(message.from_user.id, f"Досвидания, {user_name}!")


@bot.message_handler(content_types=['text'])
def repeat_message(message):
        bot.send_message(message.from_user.id, f"Извините, я не понял ваш запрос. \n"
                                               "Пожалуйста, введите комманду /start для ознакомления с моими способностями.")

if __name__ == "__main__":
    logging.info("Бот запущен")
    bot.polling(non_stop=True)
