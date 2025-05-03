import telebot
from telebot import types
import engine.kernel as Core

kernel = Core.Kernel()
bot = telebot.TeleBot(kernel.getToken())

mainMenuButtons = kernel.getMainMenuButtons()
settingsMenuButtons = kernel.getSettingsMenuButtons()
botMessages = kernel.getMessages()

mainMenuMarkup = types.ReplyKeyboardMarkup(resize_keyboard=True)
mainMenuMarkup.add(types.KeyboardButton(mainMenuButtons["createNewPage"]), types.KeyboardButton(mainMenuButtons["Categories"]), types.KeyboardButton(mainMenuButtons["News"]))
mainMenuMarkup.add(types.KeyboardButton(mainMenuButtons["Settings"]), types.KeyboardButton(mainMenuButtons["Logs"]))

settingsMenuMarkup = types.ReplyKeyboardMarkup(resize_keyboard=True)
settingsMenuMarkup.add(types.KeyboardButton(settingsMenuButtons["cache"]), types.KeyboardButton(settingsMenuButtons["checkFiles"]))
settingsMenuMarkup.add(types.KeyboardButton(settingsMenuButtons["changeSiteInformation"]))
settingsMenuMarkup.add(types.KeyboardButton(settingsMenuButtons["manage"]), types.KeyboardButton(settingsMenuButtons["admins"]), types.KeyboardButton(settingsMenuButtons["version"]))
settingsMenuMarkup.add(types.KeyboardButton(settingsMenuButtons["back"]))

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
            bot.send_message(message.chat.id, botMessages["settingsText"], reply_markup=settingsMenuMarkup)
        elif (message.text == mainMenuButtons["Logs"]):
            bot.send_message(message.chat.id, "Логи в разработке!")
        elif (kernel.checkButtonFromList("settings", message.text)):
            if (message.text == settingsMenuButtons["cache"]):
                cacheStatus = kernel.getCacheStatus()
                if (cacheStatus):
                    cacheOnOffButton = types.InlineKeyboardButton("Выключить", callback_data="s-c-0-0")
                else:
                    cacheOnOffButton = types.InlineKeyboardButton("Включить", callback_data="s-c-1")
                cacheSettingMarkup = types.InlineKeyboardMarkup().add(cacheOnOffButton, types.InlineKeyboardButton("Очистить", callback_data="d-s-0"))
                bot.send_message(message.chat.id, botMessages["settingsCache"].format(kernel.getStrFromBool(cacheStatus)), reply_markup=cacheSettingMarkup)
            elif (message.text == settingsMenuButtons["checkFiles"]):
                bot.send_message(message.chat.id, "Просмотр файлов в разработке")
            elif (message.text == settingsMenuButtons["changeSiteInformation"]):
                bot.send_message(message.chat.id, "Изменение информации о сайте в разработке")
            elif (message.text == settingsMenuButtons["manage"]):
                debugStatus = kernel.getDebugStatus()
                if (debugStatus):
                    debugOnOffButton = types.InlineKeyboardButton("Выключить дебаг", callback_data="s-d-0")
                else:
                    debugOnOffButton = types.InlineKeyboardButton("Включить дебаг", callback_data="s-d-1-0")
                debugSettingMarkup = types.InlineKeyboardMarkup().add(debugOnOffButton)
                bot.send_message(message.chat.id, botMessages["settingsManage"].format(kernel.getStrFromBool(debugStatus), kernel.getStrFromBool(kernel.getCacheStatus())), reply_markup=debugSettingMarkup)
            elif (message.text == settingsMenuButtons["admins"]):
                bot.send_message(message.chat.id, "Управление админами в разработке")
            elif (message.text == settingsMenuButtons["version"]):
                bot.send_message(message.chat.id, "Просмотр версии в разработке")
            elif (message.text == settingsMenuButtons["back"]):
                bot.send_message(message.chat.id, "Главная", reply_markup=mainMenuMarkup)
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
    elif (call.data[0] == "s"): # Setting
        if (call.data[2] == "c"): # Cache
            if (call.data[4] == "1"): # On
                kernel.changeCacheStatus(True)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Кэш включен", reply_markup=None)
            elif (call.data[4] == "0"): # Off
                if (call.data[6] == "0"): # Confim None
                    configCacheOffMarkup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text="Да", callback_data="s-c-0-1"), types.InlineKeyboardButton(text="Нет", callback_data="s-c-0-2"))
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Вы точно уверены в том, что хотите отключить кэш?", reply_markup=configCacheOffMarkup)
                elif (call.data[6] == "1"): # Confim Ok
                    kernel.changeCacheStatus(False)
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Кэш выключен", reply_markup=None)
                elif (call.data[6] == "2"): # Config No
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Отменено", reply_markup=None)
        elif (call.data[2] == "d"): # Debug
            if (call.data[4] == "1"): # On
                if (call.data[6] == "0"): # Confim None
                    confimDebugOnMarkup = types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("Да", callback_data="s-d-1-1"),
                        types.InlineKeyboardButton("Нет", callback_data="s-d-1-2")
                    )
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Вы точно уверены в том, что хотите включить дебаг?", reply_markup=confimDebugOnMarkup)
                elif (call.data[6] == "1"): # Confim Ok
                    kernel.changeDebugStatus(True)
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Дебаг включен", reply_markup=None)
                elif (call.data[6] == "2"): # Confim No
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Отменено", reply_markup=None)
            elif (call.data[4] == "0"): # Off
                kernel.changeDebugStatus(False)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Дебаг выключен")
    elif (call.data[0] == "d"): # Delete
        if (call.data[2] == "s"): # Cache
            if (call.data[4] == "0"): # Confirm None
                confimDeleteCacheMarkup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Да", callback_data="d-s-1"), types.InlineKeyboardButton("Нет", callback_data="d-s-2"))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Вы действительно хотите очистить весь кэш?", reply_markup=confimDeleteCacheMarkup)
            elif (call.data[4] == "1"): # Confim Ok
                kernel.deleteAllCache()
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Удалено", reply_markup=None)
            elif (call.data[4] == "2"): # Confim No
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Отменено", reply_markup=None)

bot.infinity_polling()