from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data.config import BOT_TOKEN
from loguru import logger


storage = StateMemoryStorage()
logger.info('Установка памяти')

#добавить обработку ошибки токена
bot = TeleBot(token=BOT_TOKEN, state_storage=storage)
logger.info('Задали токен')

