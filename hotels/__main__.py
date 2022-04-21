import requests
import telebot
import json
from decouple import config
import sqlite3

bot_api = config('BOT_API')
site_api = config('SITE_API')

bot = telebot.TeleBot(bot_api)

conn = sqlite3.connect('db/database.db', check_same_thread=False)
cursor = conn.cursor()



	# cursor.execute('INSERT INTO users (user_id, user_name) VALUES (?, ?)', (user_id, user_name))
	# conn.commit()
#
#
def db_table_value(id, name):
	for row in cursor.execute('SELECT user_id FROM users'):
		if id in row:
			break
	else:
		cursor.execute('INSERT INTO users (user_id, user_name) VALUES (?, ?)', (id, name))
		conn.commit()



@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	help_commands = 'Привет, я бот и помогу тебе подобрать лучший отель\n' \
					'\nПодсказка по моим командам:\n' \
					'\n/help - команды бота\n' \
					'/lowprice - самые дешёвые отели в городе\n' \
					'/highprice - самые дорогие отели в городе\n' \
					'/bestdeal - отели, наиболее подходящие по цене и расположению от центра\n' \
					'/history - вывод истории поиска отелей\n'

	db_table_value(message.from_user.id, message.from_user.first_name)
	bot.send_message(message.from_user.id, help_commands)


@bot.message_handler(commands=['hello-world'])
def send_welcome(message):
	bot.send_message(message.from_user.id, 'Привет')


@bot.message_handler(content_types=['text'])
def send_welcome(message):
	if message.text.lower() == 'привет':
		bot.send_message(message.from_user.id, 'Привет')
	else:
		echo_all(message)


@bot.message_handler(content_types=['text'])
def echo_all(message):
	bot.reply_to(message, message.text)


bot.infinity_polling()
