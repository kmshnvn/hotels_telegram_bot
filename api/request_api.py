from typing import List, Dict, Union, Optional, Match
import requests
import json
import re

from loguru import logger
import translators as ts

from config_data.config import headers, location_url, hotel_url, photo_url


def check_data_api(hotel: Dict) -> Dict[str, Union[str, int]]:
    """
    Функция, проверяет данные, полученные от сайта.

    Возвращает словарь с данными отеля,
    если нет названия, id или при возникновении ошибки возвращает пустой словарь
    :param hotel:
    :return:
    """
    try:
        regular_ex: str = '\$\S{,20}'

        address = hotel.get('address')
        price = hotel.get('ratePlan').get('price')
        guest_rating = hotel.get('guestReviews')
        hotel_id = hotel.get('id')
        hotel_name = hotel.get('name')

        if price.get('old'):
            hotel_price = price['old']
        elif price.get('current'):
            hotel_price = price['current']
        else:
            raise IndexError

        for location in hotel['landmarks']:
            if location['label'] == 'City center':
                hotel_dest_from_center = location['distance']
                break
            else:
                hotel_dest_from_center = None

        if address.get('streetAddress'):
            street = address['streetAddress']
        else:
            street = ''

        if address.get('locality'):
            locality = address['locality']
        else:
            locality = ''

        if address.get('region'):
            region = address['region']
        else:
            region = ''

        if address.get('postalCode'):
            postal_code = address['postalCode']
        else:
            postal_code = ''

        if guest_rating:
            hotel_rating = guest_rating.get('rating')
            hotel_reviews = guest_rating.get('total')
        else:
            hotel_rating = 0
            hotel_reviews = 0

        hotel_stars = hotel.get('starRating')

        url_of_hotel = 'https://www.hotels.com/ho' + str(hotel_id) + '/'
        hotel_full_price = re.search(regular_ex, price.get('fullyBundledPricePerStay')).group(0)

        hotel_address = f"{street}, " \
                        f"{locality}, " \
                        f"{region}, " \
                        f"{postal_code}"

        hotel_info = {
            'id': hotel_id,
            'url': url_of_hotel,
            'name': hotel_name,
            'stars': hotel_stars,
            'rating': hotel_rating,
            'total_reviews': hotel_reviews,
            'address': hotel_address,
            'price': hotel_price,
            'full_price': hotel_full_price,
            'destination': hotel_dest_from_center
        }

        return hotel_info
    except IndexError as error:
        logger.error(f'Ошибка поиска ключа {error}')
        return {}
    except Exception as ex:
        logger.error(f'Ошибка при проверке данных отеля {ex}')
        return {}


def request_to_api(url: str, querystring: Dict) -> True:
    """
    Функция, проверяет ответ от сервера

    :param url:
    :param querystring:
    :return:
    """
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)

        if response.status_code == requests.codes.ok:
            return True
        else:
            raise ConnectionError(f'Ошибка {response.status_code} при запросе к API')
    except ConnectionError as conn:
        logger.error(conn)
    except Exception as api_ex:
        logger.error(f'Возникли проблемы с сайтом - {api_ex}')


def get_city_api(city: str) -> List:
    """
    Функция, выбирает все варианты городов по названию

    Город пользователя переводится на англ язык и ищет данный город на сайте

    :param city:
    :return:
    """
    try:
        city: str = ts.google(city, from_language='ru', to_language='en')

        querystring: Dict[str, str] = {"query": city, "locale": "en_US", "currency": "USD"}

        if request_to_api(location_url, querystring):
            response = requests.request("GET", url=location_url,
                                        headers=headers, params=querystring, timeout=10)

            pattern: str = r'(?<="CITY_GROUP",).+?[\]]'
            find: Optional[Match[str]] = re.search(pattern, response.text)

            if find:
                cities: List[Dict] = list()
                regular_ex: str = '<[^<]*>'

                suggestions: Dict = json.loads(f"{{{find[0]}}}")

                for dest_id in suggestions['entities']:
                    clear_destination: str = re.sub(regular_ex, '',  dest_id['caption'])
                    cities.append({'city_name': clear_destination, 'destination_id': dest_id['destinationId']})
                return cities
            else:
                raise ConnectionError
    except ConnectionError as base:
        logger.error(f'Город не найден - {base}')
    except Exception as city_ex:
        logger.error(city_ex)


def api_get_hotels(city_id: int, sorting: str, check_in, check_out, max_hotels_number: int) -> List:
    """
    Функция, ищет отели в выбранном городе, возвращает список

    :param city_id:
    :param sorting:
    :param check_in:
    :param check_out:
    :param max_hotels_number:
    :return:
    """
    try:
        querystring: Dict[str, Union[str, int]] = {
            "destinationId": city_id,
            "pageNumber": "1",
            "pageSize": max_hotels_number,
            "checkIn": check_in,
            "checkOut": check_out,
            "adults1": "1",
            "sortOrder": sorting,
            "locale": "en_US",
            "currency": "USD"}

        if request_to_api(hotel_url, querystring):
            response = requests.request("GET", hotel_url, headers=headers, params=querystring, timeout=10)

            hotels: List[Dict[str, int]] = list()

            suggestions = json.loads(response.text)
            new = suggestions.get('data').get('body').get('searchResults').get('results')

            if new:
                for element in new:
                    print(element)

                    hotel_info = check_data_api(element)
                    if hotel_info != {}:
                        hotels.append(hotel_info)
            return hotels
        else:
            raise ConnectionError
    except ConnectionError:
        logger.error(f'Ошибка соединения')
        return []
    except Exception as error:
        logger.error(f'Ошибка при обработке поиска отелей - {error}')


def api_get_photo(hotel_id: int, max_photo: int) -> List[str]:
    """
    Функция, получает фотографии отелей

    Принимает на id отеля и сколько фотографий нужно вывести,

    :param hotel_id:
    :param max_photo:
    :return:
    """
    try:
        querystring = {"id": hotel_id}

        if request_to_api(photo_url, querystring):
            response = requests.request("GET", photo_url, headers=headers, params=querystring, timeout=10)
            photo_list = list()

            suggestions = json.loads(response.text)
            new = suggestions['hotelImages']

            size = f"{new[0]['sizes'][2]['suffix']}"
            if size:
                for element in new[:max_photo]:
                    print(element)
                    url = element.get('baseUrl')
                    if url:
                        new_url = url.replace('{size}', size)
                        photo_list.append(new_url)

            return photo_list
        else:
            raise ConnectionError
    except ConnectionError:
        logger.error(f'Фотографий не найдено')
        return []
    except Exception as error:
        logger.error(f'Ошибка при поиске фотографий отелей - {error}')
