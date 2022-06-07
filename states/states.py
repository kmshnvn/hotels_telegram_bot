from telebot.handler_backends import State, StatesGroup


# class UserInfoState(StatesGroup):
#     user_id = State()
#     username = State()
#     city_id = State()
#     command_name = State()
#     sort_order = State()
#     distance_from_center = State()
#     check_in = State()
#     check_out = State()
#     hotels_count = State()
#     photo_count = State()



class SortPrice(StatesGroup):
    """Класс состояний пользователя"""

    start = State()
    find_city = State()
    city = State()
    hotel_numbers = State()
    photos = State()
    photo_numbers = State()


