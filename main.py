import telebot
from telebot import types
import engine.kernel as Core

kernel = Core.Kernel()
bot = telebot.TeleBot(kernel.getToken())

mainMenuButtons = kernel.getMainMenuButtons()

mainMenuMarkup = types.ReplyKeyboardMarkup(resize_keyboard=True)
mainMenuMarkup.add(types.KeyboardButton(mainMenuButtons["createNewPage"]), types.KeyboardButton(mainMenuButtons["Categories"]), types.KeyboardButton(mainMenuButtons["News"]))
mainMenuMarkup.add(types.KeyboardButton(mainMenuButtons["Settings"]), types.KeyboardButton(mainMenuButtons["Logs"]))

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "Приветствую!", reply_markup=mainMenuMarkup)

@bot.message_handler(commands=['clear'])
def clear(message):
    bot.send_message(message.chat.id, "Очищено!", reply_markup=None)

@bot.message_handler(content_types='text')
def answer(message):
    bot.send_message(message.chat.id, message.text)

bot.infinity_polling()