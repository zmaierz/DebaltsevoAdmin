import telebot
from telebot import types
import engine.kernel as Core

kernel = Core.Kernel()
bot = telebot.TeleBot(kernel.getToken())

mainMenuButtons = kernel.getMainMenuButtons()
botMessages = kernel.getMessages()

mainMenuMarkup = types.ReplyKeyboardMarkup(resize_keyboard=True)
mainMenuMarkup.add(types.KeyboardButton(mainMenuButtons["createNewPage"]), types.KeyboardButton(mainMenuButtons["Categories"]), types.KeyboardButton(mainMenuButtons["News"]))
mainMenuMarkup.add(types.KeyboardButton(mainMenuButtons["Settings"]), types.KeyboardButton(mainMenuButtons["Logs"]))

unregisterMarkup = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton(mainMenuButtons["RegisterUser"]))

@bot.message_handler(commands=['start'])
def welcome(message):
    if (kernel.isAdmin(message.from_user.id)):
        bot.send_message(message.chat.id, botMessages["welcomeRegister"].format(message.from_user.first_name), reply_markup=mainMenuMarkup)
    elif (kernel.isDebug()):
        bot.send_message(message.chat.id, "Запущен режим дебага", reply_markup=mainMenuMarkup)
    else:
        bot.send_message(message.chat.id, botMessages["welcomeUnRegister"].format(message.from_user.first_name), reply_markup=unregisterMarkup)

@bot.message_handler(commands=['clear'])
def clear(message):
    bot.send_message(message.chat.id, "Очищено!", reply_markup=None)

@bot.message_handler(content_types='text')
def answer(message):
    if ((kernel.isAdmin(message.from_user.id)) or (kernel.isDebug())):
        if (message.text == mainMenuButtons["createNewPage"]):
            bot.send_message(message.chat.id, "Создание новой страницы в разработке!")
        if (message.text == mainMenuButtons["Categories"]):
            bot.send_message(message.chat.id, "Категории в разработке!")
        if (message.text == mainMenuButtons["News"]):
            bot.send_message(message.chat.id, "Новости в разработке!")
        if (message.text == mainMenuButtons["Settings"]):
            bot.send_message(message.chat.id, "Настройки в разработке!")
        if (message.text == mainMenuButtons["Logs"]):
            bot.send_message(message.chat.id, "Логи в разработке!")
    elif (message.text == mainMenuButtons["RegisterUser"]):
        bot.send_message(message.chat.id, "Регистрация пользователя в разработке")
    else:
        bot.send_message(message.chat.id, botMessages["unregisterAnswer"])

bot.infinity_polling()