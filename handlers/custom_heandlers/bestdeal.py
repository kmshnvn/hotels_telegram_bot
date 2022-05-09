#Город
#Диапазон цен
#Расстояние от центра
#Количество отелей
#Нужны ли фотографии
    #Кол-во фото

from loader import bot
from telebot.types import Message


@bot.message_handler(commands=['bestdeal'])
def survey(message: Message) -> None:
    bot.send_message(message.from_user.id, f'Привет, это команда bestdeal')