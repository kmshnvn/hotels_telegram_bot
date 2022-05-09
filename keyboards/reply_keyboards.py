from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from config_data.config import DEFAULT_COMMANDS


def main_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for element in DEFAULT_COMMANDS:
        keyboard.add(KeyboardButton(element[0]))
    return keyboard


def request_photo() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(one_time_keyboard=True)
    keyboard.add(KeyboardButton('Вывести фото'))
    keyboard.add(KeyboardButton('Фото не нужны'))

    return keyboard
