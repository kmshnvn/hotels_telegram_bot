from typing import Dict


def hotel_description(hotel: Dict) -> str:
    """
    Функция, собирает текст для вывода по отелю

    :param hotel:
    :return:
    """
    if hotel['stars'] == 0:
        stars = ''
    else:
        stars = int(hotel['stars']) * "⭐"

    text = f'{hotel["name"]}\n' \
           f'{stars}\n' \
           f'Рейтинг (Всего оценок) {hotel["rating"]} - {hotel["total_reviews"]}' \
           f'\nАдрес - {hotel["address"]}\n' \
           f'Расстояние от центра - {hotel["destination"]}\n' \
           f'\nЦена за ночь - {hotel["price"]}\n' \
           f'{hotel["full_price"]}'

    return text
