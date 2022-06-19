import os
from typing import Any, Dict

from loguru import logger

from .model import User, History, db


def db_get_user(user_id: int) -> Dict:
    """
    Функция, выбирает пользователя из БД и возвращает словарь с данными

    """
    query = User.select().where(User.telegram_id == user_id)
    for string in query.dicts().execute():
        return string


def db_get_value(user_id: int, value: str) -> Any:
    """
    Функция, ищет пользователя в БД и возвращает запрошенное значение

    """
    query = User.select().where(User.telegram_id == user_id)
    for string in query.dicts().execute():
        return string[value]


def db_save_data(user_info: Dict, hotels: Dict) -> None:
    """
    Функция, записывает все данные в историю использования.

    Получает все данные, которые ввел пользователь и те отели,
    которые он искал и записывает их в БД
    """
    History.create(
        user_id=user_info['telegram_id'],
        command_name=user_info['command_name'],
        search_city=user_info['search_city'],
        check_in=user_info['check_in'],
        check_out=user_info['check_out'],
        hotels=hotels
    )


def db_get_history(user_id: int) -> Dict:
    """
    Функция, выбирает пользователя из БД и возвращает словарь с данными

    """
    query = History.select().where(History.user_id == user_id)
    return query.dicts().execute()


if not os.path.exists('database/bot_database.db'):
    try:
        with db:
            db.create_tables([User, History])
    except Exception as ex:
        logger.error(f'database.py | Ошибка при создании БД User - {ex}')
