from telebot.types import CallbackQuery
from loguru import logger

from loader import bot
from .common import price
from .history import history, full_history
from keyboards.inline_keyboards import all_commands
from handlers.default_heandlers.help import bot_help


@bot.callback_query_handler(func=lambda call: call.data.startswith('/'))
def callback_city(call: CallbackQuery) -> None:
    """ Функция, которая собирает все сообщения пользователя из inline кнопки меню

    Распределяет по полученную команду по тому, что нужно сделать
    и редактирует свое сообщение

    """
    if call.data == '/lowprice' or call.data == '/highprice' or call.data == '/bestdeal':
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f'Начинаем искать отель'
        )
        call.message.text = call.data
        price(call.message)

    elif call.data == '/history':
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f'История, это хорошо'
        )
        history(call.message)

    elif call.data == '/help':
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f'Сейчас расскажу, что можно сделать'
        )
        bot_help(call.message)


@bot.callback_query_handler(func=lambda call: call.data.startswith('answer#'))
def callback_photo(call: CallbackQuery) -> None:
    """    Функция, обрабатывает ответ пользователя полной истории.

    Принимает строку, которая начинается на "answer#"
    Бот редактирует свое сообщение на ответ пользователя.
    """
    try:
        callback, answer = call.data.split('#')

        if answer.lower() == 'да':
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f'Сейчас выведу остальную историю'
            )
            full_history(call.message)

        elif answer.lower() == 'нет':
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text='Давай поищем еще что-нибудь',
                reply_markup=all_commands()
            )

    except Exception as ex:
        logger.error(f'callback.py | Ошибка при обработке ответа пользователю - {ex}')
        bot.send_message(
            chat_id=call.message.chat.id,
            text='Что-то пошло не так при обработке ответа'
        )

