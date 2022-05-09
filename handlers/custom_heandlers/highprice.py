#Город
#Количество отелей
#Нужны ли фотографии
    #Кол-во фото


from loader import bot
from telebot.types import Message


@bot.message_handler(commands=['highprice'])
def survey(message: Message) -> None:
    bot.send_message(message.from_user.id, f'Привет, это команда highprice')
