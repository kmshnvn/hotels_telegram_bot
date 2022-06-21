from telebot.types import Message
from loguru import logger
from loader import bot
from database.model import User


@bot.message_handler(commands=['start'])
def bot_start(message: Message) -> None:
    """
    Функция, приветствует пользователя.

    Активируется при получении от пользователя /start.
    Создает БД, если такой не было раньше

    """
    bot.send_message(
        chat_id=message.from_user.id,
        text=f"Привет, {message.from_user.full_name}!\n"
             f"\nЯ бот, который поможет тебе подобрать отель. Нажми /help, чтобы узнать мои команды\n"
             f"\n*К сожалению, из-за некоторых ограничений поиск по России не доступен*\n"
             f"\n🔍Для поиска города можно использовать русский и английский язык",
        parse_mode='Markdown'
    )
    logger.info(f'{message.chat.id} - команда start')
    if not User.get_or_none(telegram_id=message.from_user.id):
        User.create(username=message.from_user.full_name, telegram_id=message.from_user.id, hotels={1: 'url', 2: 'url'})
        logger.info('Создал БД пользователя')
    else:
        logger.info('Такой id уже есть')
