# Город
# Количество отелей
# Нужны ли фотографии
# Кол-во фото

from keyboards.reply_keyboards import request_photo
from loader import bot
from states.states import SortPrice
from telebot.types import Message
from api.request_api import get_city

max_hotel_count = 5
max_photo_count = 5


# Ожидание команды и запрос города
@bot.message_handler(commands=['lowprice'])
def price(message: Message) -> None:
    bot.set_state(message.from_user.id, SortPrice.start, message.chat.id)
    bot.send_message(message.from_user.id, f'В каком городе ищем отель?')



# Запрос кол-ва отелей
@bot.message_handler(state=SortPrice.start)
def get_city(message: Message) -> None:
    if message.text.isalpha():
        bot.send_message(message.from_user.id, get_city(message))
        bot.send_message(message.from_user.id, 'Сколько отелей вывести?')
        bot.set_state(message.from_user.id, SortPrice.city, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Название города может содержать только буквы')


# Запрос фото
@bot.message_handler(state=SortPrice.city)
def get_hotel_numbers(message: Message) -> None:
    if message.text.isdigit() and int(message.text) <= max_hotel_count:
        bot.send_message(message.from_user.id, 'Вывести фото отелей?', reply_markup=request_photo())
        bot.set_state(message.from_user.id, SortPrice.hotel_numbers, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['hotel_numbers'] = int(message.text)
    else:
        bot.send_message(
            message.from_user.id,
            f'Максимальное количество отелей не может превышать {max_hotel_count}'
        )


# Если фото не нужны - вывод результата, если нужны - запрос кол-ва фото
@bot.message_handler(state=SortPrice.hotel_numbers)
def get_photos(message: Message) -> None:
    if message.text == 'Фото не нужны':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['photos'] = message.text

            text = f'Спасибо за информацию. Ваши данные:\n' \
                   f'Город - {data["city"]}\nКол-во отелей - {data["hotel_numbers"]}'

            bot.send_message(message.from_user.id, text)

    elif message.text == 'Вывести фото':
        bot.send_message(message.from_user.id, 'Какое кол-во фотографий вывести?')
        bot.set_state(message.from_user.id, SortPrice.photos, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['photos'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Выберите ответ с клавиатуры')


# Обработка фото
@bot.message_handler(state=SortPrice.photos)
def get_photo_numbers(message: Message) -> None:
    if message.text.isdigit() and int(message.text) <= max_photo_count:
        bot.set_state(message.from_user.id, SortPrice.photo_numbers, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['photo_numbers'] = int(message.text)

            text = f'Спасибо за информацию. Ваши данные:\n' \
                   f'Город - {data["city"]}\nКол-во отелей - {data["hotel_numbers"]}\n' \
                   f'Фото - {data["photos"]}\nКол-во фото - {data["photo_numbers"]}'

            bot.send_message(message.from_user.id, text)
    else:
        bot.send_message(
            message.from_user.id,
            f'Максимальное количество отелей не может превышать {max_photo_count}'
        )
