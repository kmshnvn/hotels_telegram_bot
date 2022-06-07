from typing import List, Dict

from datetime import date, timedelta
from telebot.types import Message, CallbackQuery, InputMediaPhoto
from loguru import logger
from telegram_bot_calendar import DetailedTelegramCalendar, RUSTEP

from loader import bot
from states.states import SortPrice
from database.users import User as user
from database.database import db_get_user, db_get_value
from utils.funcs import hotel_description
from api.request_api import api_get_hotels, api_get_photo, get_city_api
from keyboards.inline_keyboards import city_markup, request_photo, hotel_link, test_keyboard


@bot.message_handler(commands=['lowprice', 'highprice'])
def price(message: Message) -> None:
    """
    Функция, отлавливает команды /lowprice и /highprice

     Записывает данную команду, а также максимальное кол-во отелей и фотографий
     в БД, после этого запрашивает город поиска

    :param message:
    :return:
    """

    try:
        new = user.get(telegram_id=message.chat.id)
        new.command_name = message.text
        new.hotels_count = 10
        new.photo_count = 10
        new.save()
    except Exception as error:
        logger.error(f'Ошибка записи в БД - {error}')

    bot.set_state(message.from_user.id, SortPrice.start, message.chat.id)
    bot.send_message(message.chat.id, 'В каком городе ищем отель?')


@bot.message_handler(state=SortPrice.start)
def check_city(message: Message) -> None:
    """
    Функция, уточняет у пользователя город поиска через inline-клавиатуру

    :param message:
    :return:
    """

    if message.text.isalpha():
        bot.send_chat_action(message.chat.id, 'typing')
        city_list: List[Dict] = get_city_api(message.text)
        if city_list:
            bot.send_message(message.chat.id, 'Уточните, пожалуйста:',
                             reply_markup=city_markup(city_list))
            bot.set_state(message.from_user.id, SortPrice.find_city, message.chat.id)

        else:
            bot.send_message(message.chat.id, 'Город не найден. Введите город поиска')
    else:
        bot.send_message(message.chat.id, f'Город должен содержать только буквы')


@bot.callback_query_handler(func=lambda call: call.data.startswith('city#'))
def callback_city(call: CallbackQuery) -> None:
    """
    Функция, обрабатывает ответ пользователя.

    Принимает строку, которая начинается на "city#"
    Бот редактирует свое сообщение на город, в котором будет производится поиск
    Происходит запись города поиска и его id в БД

    :param call:
    :return:
    """

    try:
        search_city: str = ''
        callback, city_id = call.data.split('#')

        for element in call.message.json['reply_markup']['inline_keyboard'][0]:
            if element['callback_data'] == call.data:
                search_city = element['text']

        bot.edit_message_text(
            text=f'Город поиска:\n{search_city}',
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
            )

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
                    'Введите город поиска: '
        bot.send_message(call.message.chat.id, text)


def check_in(message: Message) -> None:
    """
    Функция, Создает календарь для выбора дат заезда

    :param message:
    :return:
    """

    calendar, step = DetailedTelegramCalendar(
        calendar_id=1, locale='ru', min_date=date.today()
    ).build()

    bot.send_message(message.chat.id,
                     f"Укажите дату заезда:\n"
                     f"\nВыберите {RUSTEP[step]}",
                     reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def callback_check_in(call: CallbackQuery) -> None:
    """
    Функция, выводит календарь для выбора дат заезда

    :param call:
    :return:
    """

    result, key, step = DetailedTelegramCalendar(
        calendar_id=1, locale='ru', min_date=date.today()
    ).process(call.data)

    try:
        if not result and key:
            bot.edit_message_text(f"Выберите {RUSTEP[step]}",
                                  call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=key)

        elif result:
            result_date = result.strftime('%d.%m.%Y')
            bot.edit_message_text(f"Дата заезда: {result_date}",
                                  call.message.chat.id,
                                  call.message.message_id)

            try:
                new = user.get(telegram_id=call.message.chat.id)
                new.check_in = result
                new.save()
            except Exception as error:
                logger.error(f'Ошибка записи в БД - {error}')

            check_out(call.message)
    except KeyError as error:
        logger.error(error)
        bot.send_message(call.message.chat.id,
                         '🤬Возникла ошибка при выборе даты заезда. Попробуйте снова')
        check_in(call.message)


def check_out(message: Message) -> None:
    """
    Функция, Создает календарь для выбора дат выезда

    :param message:
    :return:
    """

    calendar, step = DetailedTelegramCalendar(
        calendar_id=2, locale='ru',
        min_date=db_get_value(message.chat.id, 'check_in')
    ).build()

    bot.send_message(message.chat.id,
                     f"Укажите дату выезда:\n"
                     f"\nВыберите {RUSTEP[step]}",
                     reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def callback_check_in(call: CallbackQuery) -> None:
    """
    Функция, выводит календарь для выбора дат выезда

    В конце запрашивает у пользователя кол-во отелей для вывода

    :param call:
    :return:
    """

    check_out_date = db_get_value(call.message.chat.id, 'check_in') + timedelta(days=1)

    result, key, step = DetailedTelegramCalendar(
        calendar_id=2, locale='ru',
        min_date=check_out_date
    ).process(call.data)

    try:
        if not result and key:
            bot.edit_message_text(f"Выберите {RUSTEP[step]}",
                                  call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=key)
        elif result:
            result_date = result.strftime('%d.%m.%Y')

            bot.edit_message_text(f"Дата выезда: {result_date}",
                                  call.message.chat.id,
                                  call.message.message_id)

            try:
                new = user.get(telegram_id=call.message.chat.id)
                new.check_out = result
                new.save()
            except Exception as error:
                logger.error(f'Ошибка записи в БД - {error}')
            bot.send_message(call.message.chat.id, 'Сколько отелей вывести?')
            # get_city(call.message)
    except KeyError as error:
        logger.error(f'Ошибка при выборе даты заезда - {error}')
        bot.send_message(call.message.chat.id,
                         'Возникла ошибка при выборе даты выезда. Попробуйте снова')
        check_out(call.message)


@bot.message_handler(state=SortPrice.find_city)
def get_hotel_numbers(message: Message) -> None:
    """
    Функция, проверяет ввод пользователя и запрашивает вывод фото отеля

    :param message:
    :return:
    """

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
                    bot.set_state(message.from_user.id, SortPrice.hotel_numbers, message.chat.id)
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
    """
    Функция, обрабатывает ответ пользователя.

    Принимает строку, которая начинается на "photo#"
    Бот редактирует свое сообщение на ответ пользователя.
    Если пользователю нужно вывести фотографии - запрашивается их кол-во
    Если фото не нужны, происходит запись данных в БД

    :param call:
    :return:
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
            bot.set_state(call.message.chat.id, SortPrice.photos)

        elif answer.lower() == 'нет':
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f'Фото не нужны'
            )

            try:
                new = user.get(telegram_id=call.message.chat.id)
                new.photo_count = 0
                new.save()
            except Exception as error:
                logger.error(f'Ошибка записи в БД - {error}')

            output_data(call.message)
    except Exception as ex:
        logger.error(f'Ошибка при обработке ответе пользователю - {ex}')
        bot.send_message(
            chat_id=call.message.chat.id,
            text='Что-то пошло не так при обработке ответа. \nПодскажите, нужны фото?'
        )


@bot.message_handler(state=SortPrice.photos)
def data_photos(message: Message) -> None:
    """
    Функция, записывает ответ пользователя в БД
    и активирует функцию вывода результата

    :param message:
    :return:
    """
    try:
        if message.text.isdigit():
            max_photo_count: int = db_get_value(message.chat.id, 'photo_count')
            min_photo_count: int = 2

            if int(message.text) <= max_photo_count:
                if int(message.text) > min_photo_count:
                    try:
                        new = user.get(telegram_id=message.chat.id)
                        new.photo_count = message.text
                        new.save()

                        output_data(message)
                    except Exception as error:
                        logger.error(f'Ошибка записи в БД - {error}')
                        bot.send_message(chat_id=message.chat.id,
                                         text='Что-то пошло не так при обработке ответа.\n '
                                              'Подскажите, сколько фотографий вывести?')
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
    """
    Функция, готовит ответ и выводит результат пользователю

    Берет все данные из БД, ищет все отели в данном городе,
    выводит фотографии при необходимости

    :param message:
    :return:
    """
    try:
        bot.send_message(message.chat.id, 'Готовлю информацию, ожидайте')

        user_info: dict = db_get_user(message.chat.id)
        max_hotel_count: int = user_info['hotels_count'] * 4
        hotel_count = user_info['hotels_count']

        if user_info['command_name'] == '/lowprice':
            sorting: str = 'PRICE'
        elif user_info['command_name'] == '/highprice':
            sorting: str = 'PRICE_HIGHEST_FIRST'

        bot.send_chat_action(message.chat.id, 'typing')
        hotel_list_info: list = api_get_hotels(
            city_id=user_info['city_id'],
            sorting=sorting,
            check_in=user_info['check_in'],
            check_out=user_info['check_out'],
            max_hotels_number=max_hotel_count
        )
        print(hotel_list_info)
        if not hotel_list_info:
            bot.send_message(chat_id=message.chat.id,
                             text='🤕Не смог собрать информацию по отелям, давай попробуем еще раз')
            bot.set_state(message.chat.id, SortPrice.start)
            bot.send_message(chat_id=message.chat.id,
                             text='Введите город')

        else:
            try:
                for hotel in hotel_list_info[:hotel_count]:
                    text: str = hotel_description(hotel)
                    print(hotel)
                    if user_info['photo_count'] == 0:
                        bot.send_message(chat_id=message.chat.id,
                                         text=text,
                                         disable_web_page_preview=True,
                                         reply_markup=hotel_link(hotel['url']))

                    else:
                        bot.send_chat_action(message.chat.id, 'upload_photo')
                        photos: list = api_get_photo(hotel['id'], user_info['photo_count'])
                        print(photos)

                        if not photos:
                            bot.send_message(chat_id=message.chat.id,
                                             text='У отеля нет фотографий')
                            bot.send_message(chat_id=message.chat.id,
                                             text=text,
                                             disable_web_page_preview=True,
                                             reply_markup=hotel_link(hotel['url']))
                        else:
                            media: list = []
                            for element in photos:
                                if len(media) == 0:
                                    media.append(InputMediaPhoto(element, text))
                                else:
                                    media.append(InputMediaPhoto(element))

                            bot.send_media_group(message.chat.id, media)

            except Exception as ex:
                logger.error(f'Ошибка при выводе текста - {ex}')
                bot.send_message(chat_id=message.chat.id,
                                 text='🤬Возникла ошибка при выводе текста')
                bot.set_state(message.chat.id, SortPrice.start)
                bot.send_message(chat_id=message.chat.id,
                                 text='Введите город')
    except Exception as ex:
        logger.error(f'Ошибка при выводе информации - {ex}')
        bot.send_message(chat_id=message.chat.id,
                         text='🤬Не смог сделать вывод информации. Нажмите /help')
        bot.set_state(message.chat.id, SortPrice.start)
        bot.send_message(chat_id=message.chat.id,
                         text='Введите город')