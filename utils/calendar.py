from datetime import date, timedelta

from loguru import logger
from telegram_bot_calendar import DetailedTelegramCalendar, RUSTEP
from telebot.types import Message, CallbackQuery

from loader import bot
from database.model import User
from states.states import SortPrice
from database.database import db_get_value


def check_in(message: Message) -> None:
    """    Функция, Создает календарь для выбора дат заезда    """

    calendar, step = DetailedTelegramCalendar(
        calendar_id=1, locale='ru', min_date=date.today()
    ).build()

    bot.send_message(message.chat.id,
                     f"Укажите дату заезда:\n"
                     f"\nВыберите {RUSTEP[step]}",
                     reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def callback_check_in(call: CallbackQuery) -> None:
    """    Функция, выводит календарь для выбора дат заезда    """

    result, key, step = DetailedTelegramCalendar(
        calendar_id=1, locale='ru', min_date=date.today()
    ).process(call.data)

    try:
        if not result and key:
            bot.edit_message_text(f"Выберите {RUSTEP[step]}",
                                  call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=key)

        elif result:
            result_date = result.strftime('%d.%m.%Y')
            bot.edit_message_text(f"Дата заезда: {result_date}",
                                  call.message.chat.id,
                                  call.message.message_id)

            try:
                new = User.get(telegram_id=call.message.chat.id)
                new.check_in = result
                new.save()
            except Exception as error:
                logger.error(f'Ошибка записи в БД - {error}')

            check_out(call.message)

    except KeyError as error:
        logger.error(error)
        bot.send_message(call.message.chat.id,
                         '🤬Возникла ошибка при выборе даты заезда. Попробуйте снова')

        check_in(call.message)


def check_out(message: Message) -> None:
    """    Функция, Создает календарь для выбора дат выезда    """

    calendar, step = DetailedTelegramCalendar(
        calendar_id=2, locale='ru',
        min_date=db_get_value(message.chat.id, 'check_in')
    ).build()

    bot.send_message(message.chat.id,
                     f"Укажите дату выезда:\n"
                     f"\nВыберите {RUSTEP[step]}",
                     reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def callback_check_in(call: CallbackQuery) -> None:
    """    Функция, выводит календарь для выбора дат выезда

    В конце запрашивает у пользователя кол-во отелей для вывода
    """
    check_out_date = db_get_value(call.message.chat.id, 'check_in') + timedelta(days=1)

    result, key, step = DetailedTelegramCalendar(
        calendar_id=2, locale='ru',
        min_date=check_out_date
    ).process(call.data)

    try:
        if not result and key:
            bot.edit_message_text(f"Выберите {RUSTEP[step]}",
                                  call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=key)
        elif result:
            result_date = result.strftime('%d.%m.%Y')

            bot.edit_message_text(f"Дата выезда: {result_date}",
                                  call.message.chat.id,
                                  call.message.message_id)

            try:
                new = User.get(telegram_id=call.message.chat.id)
                new.check_out = result
                new.save()
            except Exception as error:
                logger.error(f'Ошибка записи в БД - {error}')

            user_state = db_get_value(call.message.chat.id, 'command_name')

            if user_state == '/bestdeal':
                bot.set_state(call.message.chat.id, SortPrice.bestdeal_city)

                bot.send_message(
                    chat_id=call.message.chat.id,
                    text='Введите минимальную и максимальную цену в $ через пробел')
            else:
                bot.set_state(call.message.chat.id, SortPrice.find_city)
                bot.send_message(call.message.chat.id, 'Сколько отелей вывести?')

    except KeyError as error:
        logger.error(f'Ошибка при выборе даты заезда - {error}')
        bot.send_message(call.message.chat.id,
                         'Возникла ошибка при выборе даты выезда. Попробуйте снова')
        check_out(call.message)
