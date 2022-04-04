import requests
import telebot
import json
from decouple import config

bot_api = config('BOT_API')
site_api = config('SITE_API')

bot = telebot.TeleBot(bot_api)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	help_commands = 'Привет, я бот и помогу тебе подобрать лучший отель\n' \
					'\nПодсказка по моим командам:\n' \
					'\n/help - команды бота\n' \
					'/lowprice - самые дешёвые отели в городе\n' \
					'/highprice - самые дорогие отели в городе\n' \
					'/bestdeal - отели, наиболее подходящие по цене и расположению от центра\n' \
					'/history - вывод истории поиска отелей\n'
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
