from typing import List, Dict

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config_data.config import DEFAULT_COMMANDS


def city_markup(cities: List[Dict], command) -> InlineKeyboardMarkup:
    """
    Функция, создает клавиатуру со списком городов
    и командой пользователя для повторного поиска
    """
    name: str = 'city#'

    keyboard = InlineKeyboardMarkup()
    for city in cities[:5]:
        keyboard.add(InlineKeyboardButton(
            text=city['city_name'],
            callback_data=name+city["destination_id"]))
    keyboard.add(InlineKeyboardButton(
            text='Другое',
            callback_data=command))

    return keyboard


def request_photo() -> InlineKeyboardMarkup:
    """    Функция, создает клавиатуру с ответами Да или Нет    """

    name: str = 'photo#'
    answer_list: List[str] = ['Да', 'Нет']
    keyboard = InlineKeyboardMarkup()
    for element in answer_list:
        keyboard.add(InlineKeyboardButton(
                text=element,
                callback_data=name+element))

    return keyboard


def hotel_link(url: str) -> InlineKeyboardMarkup:
    """    Функция, создает кнопку со ссылкой перехода на сайт    """

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(
        text='Перейти на сайт',
        url=url))
    return keyboard


def all_commands() -> InlineKeyboardMarkup:
    """    Функция, создает кнопку со ссылкой перехода на сайт    """

    keyboard = InlineKeyboardMarkup()

    for command in DEFAULT_COMMANDS:
        print(command[1], '/'+command[0])
        keyboard.add(InlineKeyboardButton(
            text=command[1],
            callback_data='/'+command[0]))

    return keyboard


def yes_no_keyboard() -> InlineKeyboardMarkup:
    """    Функция, создает клавиатуру с ответами Да или Нет    """

    name: str = 'answer#'
    answer_list: List[str] = ['Да', 'Нет']
    keyboard = InlineKeyboardMarkup()
    for element in answer_list:
        keyboard.add(InlineKeyboardButton(
                text=element,
                callback_data=name+element))

    return keyboard
