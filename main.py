import telebot
import engine.kernel as Core

kernel = Core.Kernel()

print(f"Token: \"{kernel.getToken()}\"")

bot = telebot.TeleBot(kernel.getToken())

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "Приветствую!")

@bot.message_handler(content_types='text')
def answer(message):
    bot.send_message(message.chat.id, message.text)

bot.infinity_polling()