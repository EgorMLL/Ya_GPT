from telebot.types import ReplyKeyboardMarkup
import logging




markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)



logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt="%Y-%m-%d %H:%M",
    filename="log_file.txt",
    filemode="w",
)