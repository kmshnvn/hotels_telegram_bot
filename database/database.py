import os
from typing import Any, Dict

import sqlite3

from .users import User as user


def db_get_user(user_id: int) -> Dict:
    """
    Функция, выбирает пользователя из БД и возвращает словарь с данными

    :param user_id:
    :return:
    """
    query = user.select().where(user.telegram_id == user_id)
    for string in query.dicts().execute():
        return string


def db_get_value(user_id: int, value: str) -> Any:
    """
    Функция, ищет пользователя в БД и возвращает запрошенное значение

    :param user_id:
    :param value:
    :return:
    """
    query = user.select().where(user.telegram_id == user_id)
    for string in query.dicts().execute():
        return string[value]


# def write_data(id, user_field, data):
#     new = User.get(telegram_id=id)
#     new.user_field = data
#     new.save()


# def db_save_value(user_id: int, value: Any, command) -> None:
#     new = user.get(telegram_id=user_id)
#
#     for key, val in user.__dict__.items():
#         if key == command:
#             new.val = 'low'
#             new.save()
#             break
#
#
#     print(new.command_name)

    # if value == :
    #     return self._usermname
    # elif value == '':
    #     return self._telegram_id
    # elif value == '':
    #     return self.command_name
    # elif value == 'search_city':
    #     return self.search_city
    # elif value == 'city_id':
    #     return self.city_id
    # elif value == 'sort_order':
    #     return self.sort_order
    # elif value == 'distance_from_center':
    #     return self.distance_from_center
    # elif value == 'check_in':
    #     return self.check_in
    # elif value == 'check_out':
    #     return self.check_out
    # elif value == 'hotels_count':
    #     return self.hotels_count
    # elif value == 'photo_count':
    #     return self.photo_count


# def output_database(user_id: int) -> str:
#     """
#     Функция, выбирает пользователя и возвращает строку с данными пользователя
#
#     :param user_id:
#     :return:
#     """
#     text: str = ''
#     query = user.select().where(user.telegram_id == user_id)
#     for string in query.dicts().execute():
#         for key, value in string.items():
#             if not key == 'id' and value is not None:
#                 text += f'{key} - {value}\n'
#     return text


if __name__ == '__main__':
    if not os.path.exists('database/bot_database.db'):
        try:
            conn = sqlite3.connect('database/bot_database.db')
            user.create_table()
            conn.close()
        except Exception as ex:
            print(ex)