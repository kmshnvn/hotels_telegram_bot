import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')

DEFAULT_COMMANDS = (
    ('help', 'команды бота'),
    ('lowprice', 'самые дешёвые отели в городе'),
    ('highprice', 'самые дорогие отели в городе'),
    ('bestdeal', 'отели, наиболее подходящие по цене и расположению от центра'),
    ('history', 'вывод истории поиска отелей')
)

headers = {
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com",
    "X-RapidAPI-Key": RAPID_API_KEY
}

location_url = "https://hotels4.p.rapidapi.com/locations/v2/search"
hotel_url = "https://hotels4.p.rapidapi.com/properties/list"
photo_url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
