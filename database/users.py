from peewee import *

db = SqliteDatabase('database/bot_database.db')


class BaseModel(Model):
    """
    Класс, описывает базовую модель БД
    """
    class Meta:
        database = db


class User(BaseModel):
    """
    Класс пользователя.

    Описывает пользовательские поля для хранения информации о том,
    что делает пользователь в данный момент
    """
    username = CharField()
    telegram_id = IntegerField(null=True, unique=True)
    command_name = CharField(null=True)
    search_city = TextField(null=True)
    city_id = IntegerField(null=True)
    sort_order = TextField(null=True)
    distance_from_center = FloatField(null=True)
    check_in = DateField(null=True)
    check_out = DateField(null=True)
    hotels_count = IntegerField(null=True)
    photo_count = IntegerField(null=True)

