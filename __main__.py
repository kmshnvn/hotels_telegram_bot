from telebot.apihelper import ApiTelegramException
from telebot.custom_filters import StateFilter
from loguru import logger

from loader import bot
import handlers
from utils.set_bot_commands import set_default_commands
from database import database

logger.add('logger.log', format='{time} {level} {message}', level='ERROR')

if __name__ == '__main__':
    try:
        bot.add_custom_filter(StateFilter(bot))
        set_default_commands(bot)
        bot.infinity_polling()
    except ApiTelegramException as ex:
        logger.error(f'Ошибка в токене бота - {ex}')

