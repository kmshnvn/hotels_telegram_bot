from typing import List, Dict

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from api.request_api import get_city_api


def city_markup(cities: List[Dict]) -> InlineKeyboardMarkup:
    """
    Функция, создает клавиатуру со списком городов

    :param city:
    :return:
    """

    name: str = 'city#'

    keyboard = InlineKeyboardMarkup()
    for city in cities[:5]:
        keyboard.add(InlineKeyboardButton(
            text=city['city_name'],
            callback_data=name+city["destination_id"]))
    keyboard.add(InlineKeyboardButton(
            text='Другое',
            callback_data='/lowprice'))

    return keyboard


def request_photo() -> InlineKeyboardMarkup:
    """
    Функция, создает клавиатуру с ответами Да или Нет

    :return:
    """
    name: str = 'photo#'
    answer_list: List[str] = ['Да', 'Нет']
    keyboard = InlineKeyboardMarkup()
    for element in answer_list:
        keyboard.add(InlineKeyboardButton(
                text=element,
                callback_data=name+element))

    return keyboard


def test_keyboard(city: str) -> InlineKeyboardMarkup:
    """
    Тестовая клавиатура

    :param city:
    :return:
    """

    name: str = 'city#'
    destinations = InlineKeyboardMarkup()
    destinations.add(InlineKeyboardButton(
            text=city,
            callback_data=name+'0000'))
    destinations.add(InlineKeyboardButton(
            text=city+'_new',
            callback_data=name+'00001'))
    return destinations


def hotel_link(url: str) -> InlineKeyboardMarkup:
    """
    Функция, создает кнопку со ссылкой перехода на сайт

    :param url:
    :return:
    """

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(
        text='Перейти на сайт',
        url=url))
    return keyboard
