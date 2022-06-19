from datetime import datetime

from peewee import *
from playhouse.sqlite_ext import JSONField

db = SqliteDatabase('database/bot_database.db')


class BaseModel(Model):
    """ Класс, описывает базовую модель БД """

    class Meta:
        database = db


class User(BaseModel):
    """ Класс пользователя.

    Описывает пользовательские поля для хранения информации о том,
    что делает пользователь в данный момент
    """
    registration_date = DateTimeField(default=datetime.now())
    telegram_id = IntegerField(null=True, unique=True)
    username = CharField()
    command_name = CharField(null=True)
    sorting = TextField(null=True)
    search_city = TextField(null=True)
    city_id = IntegerField(null=True)
    min_price = IntegerField(null=True)
    max_price = IntegerField(null=True)
    sort_order = TextField(null=True)
    min_distance = FloatField(null=True)
    max_distance = FloatField(null=True)
    check_in = DateField(null=True)
    check_out = DateField(null=True)
    hotels_count = IntegerField(null=True)
    photo_count = IntegerField(null=True)


class History(BaseModel):
    """ Класс истории.

    Описывает поля для хранения информации истории пользователей
    """
    user_id = IntegerField(null=True)
    create_date = DateTimeField(default=datetime.now())
    command_name = CharField(null=True)
    search_city = TextField(null=True)
    check_in = DateField(null=True)
    check_out = DateField(null=True)
    hotels = JSONField()
