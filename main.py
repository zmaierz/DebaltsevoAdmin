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

cancelMarkup = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton(mainMenuButtons["CancelAction"]))

@bot.message_handler(commands=['start'])
def welcome(message):
    if (kernel.isAdmin(message.from_user.id)):
        bot.send_message(message.chat.id, botMessages["welcomeRegister"].format(message.from_user.first_name), reply_markup=mainMenuMarkup)
    elif (kernel.isDebug()):
        bot.send_message(message.chat.id, "Запущен режим дебага", reply_markup=mainMenuMarkup)
    else:
        bot.send_message(message.chat.id, botMessages["welcomeUnRegister"].format(message.from_user.first_name), reply_markup=unregisterMarkup)

@bot.message_handler(content_types='text')
def answer(message):
    if ((kernel.isAdmin(message.from_user.id)) or (kernel.isDebug())):
        if (message.text == mainMenuButtons["CancelAction"]):
            kernel.cancelAction(message.from_user.id)
            bot.send_message(message.chat.id, botMessages["cancelAction"], reply_markup=mainMenuMarkup)
        elif (kernel.isUserActive(message.from_user.id)):
            usersActions = kernel.getUsersActions(message.from_user.id)
            if (usersActions[0] == "pageCreate"):
                if (usersActions[4] == 2): # Ввод имени
                    kernel.pageCreate(message.from_user.id, 2, message.text)
                    categoriesMarkup = types.InlineKeyboardMarkup()
                    categoryList = kernel.getCategoryList()
                    for i in categoryList:
                        categoriesMarkup.add(types.InlineKeyboardButton(text=i[1], callback_data=f"c-p-3-{i[0]}"))
                    categoriesMarkup.add(types.InlineKeyboardButton(text="Без категории", callback_data="c-p-3-0"))
                    bot.send_message(message.chat.id, botMessages["createPage_enterCategory"], reply_markup=categoriesMarkup)
        elif (message.text == mainMenuButtons["createNewPage"]):
            kernel.pageCreate(message.from_user.id, 1)
            bot.send_message(message.chat.id, botMessages["createPage_enterName"], reply_markup=cancelMarkup)
        elif (message.text == mainMenuButtons["Categories"]):
            bot.send_message(message.chat.id, "Категории в разработке!")
        elif (message.text == mainMenuButtons["News"]):
            bot.send_message(message.chat.id, "Новости в разработке!")
        elif (message.text == mainMenuButtons["Settings"]):
            bot.send_message(message.chat.id, "Настройки в разработке!")
        elif (message.text == mainMenuButtons["Logs"]):
            bot.send_message(message.chat.id, "Логи в разработке!")
    elif (message.text == mainMenuButtons["RegisterUser"]):
        bot.send_message(message.chat.id, "Регистрация пользователя в разработке")
    else:
        bot.send_message(message.chat.id, botMessages["unregisterAnswer"])

@bot.callback_query_handler(func=lambda call: True)
def process(call):
    if (call.data[0] == "c"): # Create
        if (call.data[2] == "p"): # Page
            if ((call.data[4] == "3")): # Ввод категории
                data = call.data[6]
                hidePageMarkup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text="Да", callback_data="c-p-4-1"), types.InlineKeyboardButton(text="Нет", callback_data="c-p-4-0"))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=botMessages["createPage_isHide"], reply_markup=hidePageMarkup)
                kernel.pageCreate(call.from_user.id, call.data[4], data)
            if (call.data[4] == "4"): # Скрыть ли страницу
                data = call.data[6]
                kernel.pageCreate(call.from_user.id, call.data[4], data)
                userActionData = kernel.getUsersActions(call.from_user.id)
                createPageMarkup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text="Создать", callback_data="c-p-5-1"), types.InlineKeyboardButton(text="Отмена", callback_data="c-p-5-0"))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=botMessages["createPage_Confim"].format(userActionData[1], kernel.getCategoryFromID(userActionData[2]), kernel.getStrFromBool(userActionData[3])), reply_markup=createPageMarkup)
            if (call.data[4] == "5"): # Подтверждение удаления
                data = call.data[6]
                if (data == "0"): # Отмена
                    kernel.pageCreate(call.from_user.id, 0)
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=botMessages["createPage_cancel"], reply_markup=None)
                    bot.send_message(call.message.chat.id, "Главное меню", reply_markup=mainMenuMarkup)
                elif (data == "1"): # Подтвердить
                    kernel.pageCreate(call.from_user.id, 5)
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=botMessages["createPage_Ok"], reply_markup=None)
                    bot.send_message(call.message.chat.id, "Главное меню", reply_markup=mainMenuMarkup)

bot.infinity_polling()