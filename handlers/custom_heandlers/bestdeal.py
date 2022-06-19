from loguru import logger

from loader import bot
from telebot.types import Message
from states.states import SortPrice
from database.model import User as user


@bot.message_handler(state=SortPrice.bestdeal_city)
def survey(message: Message) -> None:
    """ Функция, проверяет цену, которую ввел пользователь

    Если значение прошло проверку, то минимальное и максимальное значение
    записываются в БД, после этого запрашивается расстояние до центра

    """
    min_price: str = '0'
    max_price: str = '0'
    check_variables = False
    try:
        min_price, max_price = message.text.split(' ')
        if min_price.isdigit() and max_price.isdigit():
            if min_price == max_price:
                bot.send_message(message.chat.id, 'Минимальное и максимальное значение должно отличаться')
            else:
                check_variables = True
        else:
            bot.send_message(message.chat.id, 'Нужно ввести диапазон цифрами')

    except ValueError:
        if message.text.isdigit():
            max_price = message.text
            check_variables = True
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text='Неправильный ввод. Нужно ввести цифру или '
                     'диапазон расстояния от центра через пробел.'
                     '\nПример: 10 20 или 123'
            )
    try:
        if check_variables:
            if min_price > max_price:
                min_price, max_price = max_price, min_price

            try:
                new = user.get(telegram_id=message.chat.id)
                new.min_price = min_price
                new.max_price = max_price
                new.save()
            except Exception as error:
                logger.error(f'Ошибка записи в БД - {error}')
            bot.set_state(message.from_user.id, SortPrice.distance, message.chat.id)
            bot.send_message(message.chat.id, 'Уточните расстояние до центра в км')

    except Exception as ex:
        logger.error(f'bestdeal.py | {ex}')


@bot.message_handler(state=SortPrice.distance)
def distance(message: Message) -> None:
    """ Функция, проверяет расстояние, которое ввел пользователь

    Если значение прошло проверку, то минимальное и максимальное значение
    записываются в БД, после этого запрашивается сколько отелей вывести

    """
    min_distance: str = '0'
    max_distance: str = '0'
    check_variables = False
    try:
        min_distance, max_distance = message.text.split(' ')
        if min_distance.isdigit() and max_distance.isdigit():
            if min_distance == max_distance:
                bot.send_message(message.chat.id, 'Минимальное и максимальное значение должно отличаться')
            else:
                check_variables = True
        else:
            bot.send_message(message.chat.id, 'Нужно ввести диапазон цифрами')

    except ValueError:
        if message.text.isdigit():
            min_distance = '0'
            max_distance = message.text
            check_variables = True
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text='Неправильный ввод. Нужно ввести цифру или '
                     'диапазон расстояния от центра через пробел.'
                     '\nПример: 10 20 или 123'
            )
    try:
        if check_variables:
            if min_distance > max_distance:
                min_distance, max_distance = max_distance, min_distance

            try:
                new = user.get(telegram_id=message.chat.id)
                new.min_distance = min_distance
                new.max_distance = max_distance
                new.save()
            except Exception as error:
                logger.error(f'Ошибка записи в БД - {error}')
            bot.set_state(message.from_user.id, SortPrice.find_city, message.chat.id)
            bot.send_message(message.chat.id, 'Сколько отелей вывести?')

    except Exception as ex:
        logger.error(f'bestdeal.py | {ex}')
