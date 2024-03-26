from config import *
from Logging import *
from database import *
import telebot
import requests

API_TOKEN = TOKEN
bot = telebot.TeleBot(API_TOKEN)

users_history = {}
create_table()



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
    bot.send_message(message.chat.id, f"Приветствую, {name}, рад знакомству! Я бот - помощник, основанный на нейросети. Моя нейросеть может ответить на любые ваши вопросы по математике и рисованию! (разумные конечно)\n"
                                      "Ознакомтесь со списком моих команд по команде /help", reply_markup=markup)