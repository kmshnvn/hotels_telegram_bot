from telebot.types import Message
from loader import bot


@bot.message_handler(commands=['start'])
def bot_start(message: Message):
    bot.send_message(message.from_user.id,
                     f"Привет, {message.from_user.full_name}!\n"
                     f"\nЯ бот, который поможет тебе подобрать отель. Нажми /help, чтобы узнать мои команды"
                     )
