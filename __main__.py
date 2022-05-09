from loader import bot
from loguru import logger
from telebot.custom_filters import StateFilter
from utils.set_bot_commands import set_default_commands

logger.add('logger.log', format='{time} {level} {message}', level='ERROR')

if __name__ == '__main__':
    bot.add_custom_filter(StateFilter(bot))
    logger.info('Старт')
    set_default_commands(bot)
    logger.info('Передаем команды боту')
    logger.info('Переход в бота')
    bot.infinity_polling()

