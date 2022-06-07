from telebot.types import BotCommand
from loguru import logger

from config_data.config import DEFAULT_COMMANDS


def set_default_commands(bot) -> None:
    """
    Функция, устанавливает команды для бота

    :param bot:
    :return:
    """
    bot.set_my_commands(
        [BotCommand(*i) for i in DEFAULT_COMMANDS]
    )
