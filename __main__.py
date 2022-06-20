from time import sleep

from telebot.apihelper import ApiTelegramException, ApiException, Timeout
from telebot.custom_filters import StateFilter
from loguru import logger

from loader import bot
import handlers
from utils.set_bot_commands import set_default_commands
from database import database

logger.add('user_logger.log', format='{time:HH:mm:ss DD-MM-YY} {level} {message}', level='INFO', rotation="2 MB")
logger.add('logger.log', format='{time:HH:mm:ss DD-MM-YY} {level} {message}', level='ERROR')

if __name__ == '__main__':
    try:
        bot.add_custom_filter(StateFilter(bot))
        set_default_commands(bot)
        while True:
            try:
                logger.info('Запуск бота')
                bot.infinity_polling()
                break
            except ApiException as e:
                logger.error(e)
                bot.stop_polling()
                sleep(15)
            except Timeout as time_ex:
                logger.error(time_ex)

    except ApiTelegramException as ex:
        logger.error(f'Ошибка в токене бота - {ex}')
