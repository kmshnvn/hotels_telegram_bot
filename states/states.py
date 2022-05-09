from telebot.handler_backends import State, StatesGroup


class UserInfoState(StatesGroup):
    name = State()
    age = State()
    country = State()
    city = State()
    phone_number = State()

class SortPrice(StatesGroup):
    start = State()
    city = State()
    hotel_numbers = State()
    photos = State()
    photo_numbers = State()


