#Команда
#Дата и время
#Отели


from loader import bot
from telebot.types import Message


@bot.message_handler(commands=['history'])
def survey(message: Message) -> None:
    bot.send_message(message.from_user.id, f'Привет, это команда history')
