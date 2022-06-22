from typing import List, Dict

from telebot.types import Message, CallbackQuery, InputMediaPhoto
from loguru import logger

from loader import bot
from database.states import SortPrice
from database.model import User as user
from database.database import db_get_user, db_get_value, db_save_data
from utils.funcs import hotel_description
from utils.calendar import check_in
from api.request_api import api_get_hotels, api_get_photo, get_city_api, api_get_bestdeal
from keyboards.inline_keyboards import city_markup, request_photo, hotel_link, all_commands


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def price(message: Message) -> None:
    """    Функция, отлавливает команды /lowprice и /highprice

     Записывает данную команду, а также максимальное кол-во отелей и фотографий
     в БД, после этого запрашивает город поиска
    """
    logger.info(f'{message.chat.id} - common.py | выбор команды {message.text}')

    if message.text == '/lowprice':
        sorting: str = 'PRICE'
    elif message.text == '/highprice':
        sorting: str = 'PRICE_HIGHEST_FIRST'
    elif message.text == '/bestdeal':
        sorting: str = 'DISTANCE_FROM_LANDMARK'

    try:
        new = user.get(telegram_id=message.chat.id)
        new.command_name = message.text
        new.sorting = sorting
        new.hotels_count = 10
        new.photo_count = 10
        new.save()
    except Exception as error:
        logger.error(f'Ошибка записи в БД - {error}')
    bot.send_message(message.chat.id, 'В каком городе ищем отель?\n\nМожно ввести на 🇷🇺 и 🇺🇸 языке')
    bot.set_state(message.chat.id, SortPrice.city)



@bot.message_handler(state=SortPrice.city)
def check_city(message: Message) -> None:
    """    Функция, уточняет у пользователя город поиска через inline-клавиатуру    """
    logger.info(f'{message.chat.id} - common.py | поиск и утонение города - {message.text}')

    if message.text.isalpha():
        bot.send_chat_action(message.chat.id, 'typing')
        city_list: List[Dict] = get_city_api(message.text)
        if city_list:
            command = db_get_value(message.chat.id, 'command_name')

            bot.send_message(message.chat.id, 'Уточните, пожалуйста:',
                             reply_markup=city_markup(city_list, command))

        else:
            bot.send_message(message.chat.id, 'Город не найден. Введите город поиска на 🇷🇺 или 🇺🇸 языке:')
    else:
        bot.send_message(message.chat.id, f'Город должен содержать только буквы')


@bot.callback_query_handler(func=lambda call: call.data.startswith('city#'))
def callback_city(call: CallbackQuery) -> None:
    """    Функция, обрабатывает ответ пользователя.

    Принимает строку, которая начинается на "city#"
    Бот редактирует свое сообщение на город, в котором будет производится поиск
    Происходит запись города поиска и его id в БД
    """
    try:
        search_city: str = ''
        callback, city_id = call.data.split('#')
        element = call.message.json['reply_markup']['inline_keyboard']

        for elem in element:
            if elem[0]['callback_data'] == call.data:
                search_city = elem[0]['text']

        bot.edit_message_text(
            text=f'Город поиска:\n{search_city}',
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
            )

        logger.info(f'{call.message.chat.id} - common.py | выбран город {search_city}')

        try:
            new = user.get(telegram_id=call.message.chat.id)
            new.search_city = search_city
            new.city_id = city_id
            new.save()
        except Exception as error:
            logger.error(f'Ошибка записи в БД - {error}')

        check_in(call.message)

    except Exception as ex:
        logger.error(ex)
        text: str = '🤬Что-то пошло не так, при выборе города. Давайте попробуем еще раз.\n' \
                    'Введите город поиска на 🇷🇺 или 🇺🇸 языке: '
        bot.send_message(call.message.chat.id, text)


@bot.message_handler(state=SortPrice.find_city)
def get_hotel_numbers(message: Message) -> None:
    """    Функция, проверяет ввод пользователя и запрашивает вывод фото отеля

    """
    logger.info(f'{message.chat.id} - common.py | кол-во отелей для вывода {message.text}')

    try:
        if message.text.isdigit():
            max_hotel_count: int = db_get_value(message.chat.id, 'hotels_count')

            if int(message.text) <= max_hotel_count:
                if int(message.text) > 0:
                    try:
                        new = user.get(telegram_id=message.chat.id)
                        new.hotels_count = message.text
                        new.save()
                    except Exception as error:
                        logger.error(f'Ошибка записи в БД - {error}')

                    bot.send_message(message.chat.id, 'Нужны фото?', reply_markup=request_photo())
                    bot.set_state(message.chat.id, SortPrice.photos)
                else:
                    bot.send_message(
                        chat_id=message.chat.id,
                        text=f'Минимальное количество отелей не может быть меньше или равно 0'
                    )
            else:
                bot.send_message(
                    chat_id=message.chat.id,
                    text=f'Максимальное количество отелей не может превышать {max_hotel_count}'
                )
        else:
            bot.send_message(message.chat.id, 'Я ожидаю цифру')
    except Exception as error:
        logger.error(f'Ошибка при запросе кол-ва отелей - {error}')
        bot.send_message('Что-то пошло не так при запросе количества отелей')


@bot.callback_query_handler(func=lambda call: call.data.startswith('photo#'))
def callback_photo(call: CallbackQuery) -> None:
    """    Функция, обрабатывает ответ пользователя.

    Принимает строку, которая начинается на "photo#"
    Бот редактирует свое сообщение на ответ пользователя.
    Если пользователю нужно вывести фотографии - запрашивается их кол-во
    Если фото не нужны, происходит запись данных в БД
    """
    try:
        callback, answer = call.data.split('#')

        if answer.lower() == 'да':
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f'Вывести фото'
            )
            bot.send_message(call.message.chat.id, 'Какое кол-во фотографий вывести?')
            bot.set_state(call.message.chat.id, SortPrice.photo_numbers)
            logger.info(f'{call.message.chat.id} - common.py | Вывести фото')

        elif answer.lower() == 'нет':
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f'Фото не нужны'
            )
            logger.info(f'{call.message.chat.id} - common.py | Фото не нужны')

            try:
                new = user.get(telegram_id=call.message.chat.id)
                new.photo_count = 0
                new.save()
            except Exception as error:
                logger.error(f'Ошибка записи в БД - {error}')

            output_data(call.message)

    except Exception as ex:
        logger.error(f'Ошибка при обработке ответа пользователю - {ex}')
        bot.send_message(
            chat_id=call.message.chat.id,
            text='Что-то пошло не так при обработке ответа. \nПодскажите, нужны фото?'
        )


@bot.message_handler(state=SortPrice.photo_numbers)
def data_photos(message: Message) -> None:
    """
    Функция, записывает ответ пользователя в БД
    и активирует функцию вывода результата

    """
    logger.info(f'{message.chat.id} - common.py | вывести фото - {message.text}')

    try:
        if message.text.isdigit():
            max_photo_count: int = db_get_value(message.chat.id, 'photo_count')
            min_photo_count: int = 2

            if int(message.text) <= max_photo_count:
                if int(message.text) >= min_photo_count:
                    try:
                        new = user.get(telegram_id=message.chat.id)
                        new.photo_count = message.text
                        new.save()

                    except Exception as error:
                        logger.error(f'Ошибка записи в БД - {error}')
                        bot.send_message(chat_id=message.chat.id,
                                         text='Что-то пошло не так при обработке ответа.\n '
                                              'Подскажите, сколько фотографий вывести?')

                    output_data(message)

                else:
                    bot.send_message(
                        chat_id=message.chat.id,
                        text=f'Минимальное количество фотографий не может быть меньше {min_photo_count}'
                    )
            else:
                bot.send_message(
                    chat_id=message.chat.id,
                    text=f'Максимальное количество фотографий не может превышать {max_photo_count}'
                )
        else:
            bot.send_message(message.chat.id, 'Я ожидаю цифру')
    except Exception as error:
        logger.error(f'Ошибка при запросе фотографий - {error}')
        bot.send_message('Что-то пошло не так при запросе количества фотографий')


def output_data(message: Message) -> None:
    """    Функция, готовит ответ и выводит результат пользователю

    Берет все данные из БД, ищет все отели в данном городе,
    выводит фотографии при необходимости

    """
    logger.info(f'{message.chat.id} - common.py | вывожу информацию по отелям')

    hotels_for_db: Dict[str, str] = {}
    try:
        bot.send_message(message.chat.id, 'Готовлю информацию, ожидайте')

        user_info: dict = db_get_user(message.chat.id)
        hotel_count = user_info['hotels_count']
        hotel_list_info: list = []

        bot.send_chat_action(message.chat.id, 'typing')

        if user_info['command_name'] == '/bestdeal':
            hotel_list_info = api_get_bestdeal(
                city_id=user_info['city_id'],
                sorting=user_info['sorting'],
                check_in=user_info['check_in'],
                check_out=user_info['check_out'],
                min_price=user_info['min_price'],
                max_price=user_info['max_price'],
                min_distance=user_info['min_distance'],
                max_distance=user_info['max_distance'],
                hotel_number=hotel_count,
                message=message
            )
        else:
            max_hotel_count: int = hotel_count * 4
            hotel_list_info = api_get_hotels(
                city_id=user_info['city_id'],
                sorting=user_info['sorting'],
                check_in=user_info['check_in'],
                check_out=user_info['check_out'],
                max_hotels_number=max_hotel_count
            )
        logger.info(f'Количество отлей найдено {len(hotel_list_info)}')
        if not hotel_list_info:
            bot.send_message(chat_id=message.chat.id,
                             text='🤕Не смог собрать информацию по отелям, давай попробуем еще раз')
            bot.set_state(message.chat.id, SortPrice.start)
            bot.send_message(chat_id=message.chat.id,
                             text='Введите город на 🇷🇺 или 🇺🇸 языке')

        else:
            try:
                for hotel in hotel_list_info[:hotel_count]:
                    hotels_for_db[hotel['name']] = hotel['url']
                    text: str = hotel_description(hotel)

                    if user_info['photo_count'] == 0:
                        bot.send_message(chat_id=message.chat.id,
                                         text=text,
                                         parse_mode='Markdown',
                                         disable_web_page_preview=True,
                                         reply_markup=hotel_link(hotel['url']))

                    else:
                        bot.send_chat_action(message.chat.id, 'upload_photo')
                        photos: list = api_get_photo(hotel['id'], user_info['photo_count'])

                        if not photos:
                            bot.send_message(chat_id=message.chat.id,
                                             text='У отеля нет фотографий')
                            bot.send_message(chat_id=message.chat.id,
                                             text=text,
                                             parse_mode='Markdown',
                                             disable_web_page_preview=True,
                                             reply_markup=hotel_link(hotel['url']))
                        else:
                            media: list = []
                            for element in photos:
                                if len(media) == 0:
                                    media.append(InputMediaPhoto(element, text, parse_mode='Markdown'))
                                else:
                                    media.append(InputMediaPhoto(element))

                            bot.send_media_group(message.chat.id, media)

            except Exception as ex:
                logger.error(f'Ошибка при выводе текста - {ex}')
                bot.send_message(chat_id=message.chat.id,
                                 text='🤬Возникла ошибка при выводе текста')
                bot.set_state(message.chat.id, SortPrice.start)
                bot.send_message(chat_id=message.chat.id,
                                 text='Введите город на 🇷🇺 или 🇺🇸 языке')

        db_save_data(user_info, hotels_for_db)
        bot.send_message(chat_id=message.chat.id,
                         text='Что еще поищем?',
                         reply_markup=all_commands())


    except Exception as ex:
        logger.error(f'Ошибка при выводе информации - {ex}')
        bot.send_message(chat_id=message.chat.id,
                         text='🤬Не смог сделать вывод информации')
        bot.set_state(message.chat.id, SortPrice.start)
        bot.send_message(chat_id=message.chat.id,
                         text='Введите город на 🇷🇺 или 🇺🇸 языке')
