from telebot.types import Message

from loguru import logger

from loader import bot
from config_data.config import DEFAULT_COMMANDS


@bot.message_handler(commands=['help'])
def bot_help(message: Message) -> None:
    """
    Функция, дает справочную информацию по работе бота

    Активируется в момент написания пользователем /help.

    """
    logger.info(f'{message.chat.id} - команда help')
    text = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS]
    bot.send_message(message.chat.id,
                     'Я бот, который поможет тебе найти отель для твоего отдыха.\n'
                     '\nК сожалению, из-за некоторых ограничений поиск по России не доступен\n'
                     '\nИспользуй мои команды, чтобы найти подходящий отель:\n\n'
                     + '\n'.join(text))
