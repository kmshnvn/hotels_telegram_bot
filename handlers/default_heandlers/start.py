from telebot.types import Message
from loguru import logger
from loader import bot
from database.users import User


@bot.message_handler(commands=['start'])
def bot_start(message: Message) -> None:
    """
    Функция, приветствует пользователя.

    Активируется при получении от пользователя /start.
    Создает БД, если такой не было раньше

    :param message:
    :return:
    """
    bot.send_message(message.from_user.id,
                     f"Привет, {message.from_user.full_name}!\n"
                     f"\nЯ бот, который поможет тебе подобрать отель. Нажми /help, чтобы узнать мои команды"
                     )
    if not User.get_or_none(telegram_id=message.from_user.id):
        User.create(username=message.from_user.full_name, telegram_id=message.from_user.id)
        logger.info('Создал БД пользователя')
    else:
        logger.info('Такой id уже есть')
