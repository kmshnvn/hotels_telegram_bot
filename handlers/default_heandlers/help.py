from telebot.types import Message

from loader import bot
from config_data.config import DEFAULT_COMMANDS


@bot.message_handler(commands=['help'])
def bot_help(message: Message) -> None:
    """
    Функция, дает справочную информацию по работе бота

    Активируется в момент написания пользователем /help.

    """
    text = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS]
    bot.send_message(message.chat.id,
                     'Используй мои команды, чтобы найти подходящий отель:\n\n'
                     + '\n'.join(text))
