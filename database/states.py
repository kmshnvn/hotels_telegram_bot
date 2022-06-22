from telebot.handler_backends import State, StatesGroup


class SortPrice(StatesGroup):
    """ Класс состояний пользователя """

    start = State()
    city = State()
    find_city = State()
    bestdeal_city = State()
    distance = State()
    hotel_numbers = State()
    photos = State()
    photo_numbers = State()
