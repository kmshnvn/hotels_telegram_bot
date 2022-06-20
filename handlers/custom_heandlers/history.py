from datetime import datetime
from typing import List, Dict

from telebot.types import Message
from loguru import logger

from loader import bot
from database.database import db_get_history
from keyboards.inline_keyboards import all_commands, yes_no_keyboard
from time import sleep


def text_history(query: Dict, date, message: Message) -> str:
    """    Функция, составляет текст истории пользователя

    Получает словарь с данными пользователя, составляет текст.
    Если текст превышает максимальную длину, то отправляет текст,
    очищает его и продолжает собирать историю.

    После этого возвращает окончательный текст.

    """
    logger.info(f'{message.chat.id} - history.py | составляю сообщение истории использования')

    text_length: int = 2000
    text: str = ''

    for element in query:
        hotel_text = ''

        if date == element['create_date'].date():
            dates = element['create_date']
            result_date = dates.strftime('%H:%M')
            command = str(element['command_name'])
            city = str(element['search_city'])
            check_in = element['check_in'].strftime('%d.%m.%Y')
            check_out = element['check_out'].strftime('%d.%m.%Y')
            for key, value in element['hotels'].items():
                hotel_text += f'\n🔸[{key}]({value})'

            history_text = f'\n🕐{result_date}\n' \
                           f'{command}\n' \
                           f'*{city}*\n' \
                           f'📆{check_in} - {check_out}\n' \
                           f'{hotel_text}\n'

            if len(text) + len(history_text) > text_length:
                bot.send_message(message.chat.id, text,
                                 parse_mode='Markdown',
                                 disable_web_page_preview=True)
                text = ''

            text += history_text

    return text


def history_list(query: Dict, today):
    """
    Функция, собирает список со всеми датами,
    в которые пользователь использовал бота

    """
    full_dates: List = []
    today_history = False

    for element in query:
        dates = element['create_date'].date()
        if today == dates:
            today_history = True

        if dates not in full_dates:
            full_dates.append(dates)

    return full_dates, today_history


def full_history_message(message: Message, query: Dict,
                         full_dates: List, end: int, start: int = 0) -> None:
    """    Функция, выводит историю пользования ботом по дням.

    Принимает сообщение пользователя, словарь с данными клиента из БД,
    список со всеми датами, длину списка дат и с какого начинать выводить
    """
    logger.info(f'{message.chat.id} - history.py | Вывожу историю пользования ботом по дням')

    for date in full_dates[start:end]:
        sleep(1)
        bot.send_message(
            chat_id=message.chat.id,
            text=f'*История за {date.strftime("%d.%m.%Y")}*',
            parse_mode='Markdown',
            disable_web_page_preview=True)
        text = text_history(query, date, message)
        bot.send_message(message.chat.id, text, parse_mode='Markdown', disable_web_page_preview=True)
        full_dates.pop(0)


@bot.message_handler(commands=['history'])
def history(message: Message) -> None:
    """    Функция, отлавливает команду /history

    Смотрит текущую дату, и получает данные из БД, ищет все даты пользователя;
    Если дат нет, то выводит информацию об этом, если в списке дат найдено сегодняшнее число -
    показывает историю за сегодняшний день, иначе выводит историю за последние 3 дня,
    в который пользователь использовал бота
    """
    logger.info(f'{message.chat.id} - history.py | выбор команды /history')

    today_date = datetime.now().date()
    query = db_get_history(message.chat.id)

    full_dates, today_history = history_list(query, today_date)
    if full_dates is None:
        bot.send_message(
            chat_id=message.chat.id,
            text=f'История пользования еще нет, выберите одну из команд',
            reply_markup=all_commands())
    elif today_history:
        text = text_history(query, today_date, message)

        bot.send_message(
            chat_id=message.chat.id,
            text=f'История за сегодня\n{text}',
            parse_mode='Markdown',
            disable_web_page_preview=True)
        sleep(1)
        bot.send_message(message.chat.id, 'Вывести всю историю?', reply_markup=yes_no_keyboard())

    else:
        full_dates.sort(reverse=True)
        last_date = full_dates[0]
        bot.send_message(
            chat_id=message.chat.id,
            text=f'Последнее использование бота {last_date.strftime("%d.%m.%Y")}')
        bot.send_message(message.chat.id, f'Сейчас выведу историю последнего использования')
        end = 3
        full_history_message(message, query, full_dates, end)
        if not full_dates:
            sleep(1)
            bot.send_message(message.chat.id, 'Это вся история использования🤫')
            sleep(1)
            bot.send_message(message.chat.id, 'Давай поищем еще что-нибудь', reply_markup=all_commands())
        else:
            bot.send_message(message.chat.id, 'Вывести всю историю?', reply_markup=yes_no_keyboard())


def full_history(message: Message):
    """
    Функция, выводит всю историю пользователя, за исключением того,
    что пользователь уже увидел

    """
    logger.info(f'{message.chat.id} - history.py | вывод всей истории пользования')

    today_date = datetime.now().date()
    query = db_get_history(message.chat.id)

    full_dates, today_history = history_list(query, today_date)
    full_dates.sort(reverse=True)

    if today_history:
        start = 1
    else:
        start = 3

    end = len(full_dates)
    full_history_message(message, query, full_dates, end, start)
    bot.send_message(message.chat.id, 'Давай поищем еще что-нибудь', reply_markup=all_commands())
