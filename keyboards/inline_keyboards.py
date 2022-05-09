from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from api.request_api import city_founding


def city_markup(cities):
    destinations = InlineKeyboardMarkup()
    for city in cities:
        destinations.add(
            InlineKeyboardButton(text=city['city_name'],
            callback_data=f'{city["destination_id"]}')
        )
    return destinations
