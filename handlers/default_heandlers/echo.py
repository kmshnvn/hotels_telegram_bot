from telebot.types import Message

from loguru import logger

from loader import bot


@bot.message_handler(content_types=['text'])
def bot_echo(message: Message):
    """    Функция, отлавливает текст, который не относится ни к одному состоянию    """
    bot.send_message(
        chat_id=message.chat.id,
        text=f"Чтобы узнать подробнее о боте: /help"
        )
    logger.info(f'{message.chat.id} - echo.py | команда echo {message.text}')
