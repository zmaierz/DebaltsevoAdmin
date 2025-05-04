import telebot
from telebot import types
import engine.kernel as Core

kernel = Core.Kernel()
bot = telebot.TeleBot(kernel.getToken())

mainMenuButtons = kernel.getMainMenuButtons()
settingsMenuButtons = kernel.getSettingsMenuButtons()
settingsAdminMenuButtons = kernel.getSettingsAdminMenuButtons()
categoryMenuButtons = kernel.getCategoryMenuButtons()
botMessages = kernel.getMessages()

mainMenuMarkup = types.ReplyKeyboardMarkup(resize_keyboard=True)
mainMenuMarkup.add(types.KeyboardButton(mainMenuButtons["createNewPage"]), types.KeyboardButton(mainMenuButtons["Categories"]), types.KeyboardButton(mainMenuButtons["News"]))
mainMenuMarkup.add(types.KeyboardButton(mainMenuButtons["Settings"]), types.KeyboardButton(mainMenuButtons["Logs"]))

settingsMenuMarkup = types.ReplyKeyboardMarkup(resize_keyboard=True)
settingsMenuMarkup.add(types.KeyboardButton(settingsMenuButtons["cache"]), types.KeyboardButton(settingsMenuButtons["checkFiles"]))
settingsMenuMarkup.add(types.KeyboardButton(settingsMenuButtons["changeSiteInformation"]))
settingsMenuMarkup.add(types.KeyboardButton(settingsMenuButtons["manage"]), types.KeyboardButton(settingsMenuButtons["admins"]), types.KeyboardButton(settingsMenuButtons["version"]))
settingsMenuMarkup.add(types.KeyboardButton(settingsMenuButtons["back"]))

settingsAdminMarkup = types.ReplyKeyboardMarkup(resize_keyboard=True)
settingsAdminMarkup.add(types.KeyboardButton(settingsAdminMenuButtons["createNewAdmin"]))
settingsAdminMarkup.add(types.KeyboardButton(settingsAdminMenuButtons["checkInvite"]))
settingsAdminMarkup.add(types.KeyboardButton(settingsAdminMenuButtons["backToSettings"]))

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
    if (kernel.isUserAuth(message.from_user.id)):
        kernel.authUser(message.from_user.id, 2, message.text)
        isActive = kernel.checkAdminInvite(message.text)
        if (isActive == False):
            bot.send_message(message.chat.id, "Неверный код-приглашение!")
            kernel.delAuthUser()
        else:
            kernel.createAdmin(message.from_user.id, message.text)
            outText = botMessages["registerUserSuccess"].format(message.from_user.first_name, isActive)
            kernel.delAuthUser(message.from_user.id)
            bot.send_message(message.chat.id, outText, reply_markup=mainMenuMarkup)
    elif ((kernel.isAdmin(message.from_user.id)) or (kernel.isDebug())):
        if (message.text == mainMenuButtons["CancelAction"]):
            try:
                kernel.cancelAction(message.from_user.id)
            except:
                pass
            finally:
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
            elif (usersActions[0] == "changeAdminName"):
                if (usersActions[4] == 2): # Ввод имени
                    kernel.changeAdminName(message.from_user.id, 2, message.text)
                    confimChangeAdminNameMarkup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Изменить", callback_data=f"s-a-{usersActions[1]}-1"), types.InlineKeyboardButton("Отменить", callback_data=f"s-a-{usersActions[1]}-2"))
                    outText = botMessages["confimChangeAdminName"].format(usersActions[1], message.text)
                    bot.send_message(message.chat.id, outText, reply_markup=confimChangeAdminNameMarkup)
            elif (usersActions[0] == "createAdminInvite"):
                if (usersActions[4] == 2): # Ввод имени
                    if (len(message.text) > 100):
                        bot.send_message(message.chat.id, "Слишком длинное имя!")
                    else:
                        kernel.createAdminInvite(message.from_user.id, 2, message.text)
                        confimCreateAdminMarkup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Да", callback_data="c-a-1"), types.InlineKeyboardButton("Отмена", callback_data="c-a-2"))
                        outText = botMessages["confimCreateAdmin"].format(message.text)
                        bot.send_message(message.chat.id, outText, reply_markup=confimCreateAdminMarkup)
            elif (usersActions[0] == "categoryCreate"):
                if (usersActions[4] == 2): # Ввод имени
                    if (len(message.text) > 100):
                        bot.send_message(message.chat.id, "Слишком длинное имя!")
                    else:
                        kernel.createCategory(message.from_user.id, 2, message.text)
                        confimCreateCategoryMarkup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Да", callback_data="c-c-1"), types.InlineKeyboardButton("Нет", callback_data="c-c-2"))
                        outText = f"Вы действительно хотите создать категорию {message.text}?"
                        bot.send_message(message.chat.id, outText, reply_markup=confimCreateCategoryMarkup)
        elif (message.text == mainMenuButtons["createNewPage"]):
            kernel.pageCreate(message.from_user.id, 1)
            bot.send_message(message.chat.id, botMessages["createPage_enterName"], reply_markup=cancelMarkup)
        elif (message.text == mainMenuButtons["Categories"]):
            categoryList = kernel.getCategoryList()
            categoryMenuMarkup = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton(categoryMenuButtons["createCategory"]))
            categoryMenuMarkup.add(types.KeyboardButton(settingsMenuButtons["back"]))
            categoryListMarkup = types.InlineKeyboardMarkup()
            outText = "Список категорий:\n"
            j = 1
            for i in categoryList:
                outText += f"{j}. {i[1]}\n"
                categoryListMarkup.add(types.InlineKeyboardButton(i[1], callback_data=f"o-c-{i[0]}"))
                j += 1
            bot.send_message(message.chat.id, "Настройка категорий", reply_markup=categoryMenuMarkup)
            bot.send_message(message.chat.id, outText, reply_markup=categoryListMarkup)
        elif (message.text == mainMenuButtons["News"]):
            bot.send_message(message.chat.id, "Новости в разработке!")
        elif (message.text == mainMenuButtons["Settings"]):
            bot.send_message(message.chat.id, botMessages["settingsText"], reply_markup=settingsMenuMarkup)
        elif (message.text == mainMenuButtons["Logs"]):
            bot.send_message(message.chat.id, "Логи в разработке!")
        elif (kernel.checkButtonFromList("category", message.text)):
            if (message.text == categoryMenuButtons["createCategory"]):
                kernel.createCategory(message.from_user.id, 1)
                bot.send_message(message.chat.id, "Введите название новой категории", reply_markup=cancelMarkup)
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
                adminList = kernel.getAdminList()
                adminListText = ""
                adminListMarkup = types.InlineKeyboardMarkup()
                j = 1
                for i in adminList:
                    adminListText += f"{j}. {i[4]}\n"
                    adminListMarkup.add(types.InlineKeyboardButton(i[4], callback_data=f"o-a-{i[0]}"))
                    j += 1
                bot.send_message(message.chat.id, "Настройка администраторов", reply_markup=settingsAdminMarkup)
                bot.send_message(message.chat.id, botMessages["settingsAdmin"].format(adminListText), reply_markup=adminListMarkup)
            elif (message.text == settingsMenuButtons["version"]):
                versions = kernel.getVersions()
                outText = botMessages["checkSystemVersion"].format(versions[0], versions[1], versions[2])
                bot.send_message(message.chat.id, outText)
            elif (message.text == settingsMenuButtons["back"]):
                bot.send_message(message.chat.id, "Главная", reply_markup=mainMenuMarkup)
        elif (kernel.checkButtonFromList("settingsAdmin", message.text)):
            if (message.text == settingsAdminMenuButtons["createNewAdmin"]):
                kernel.createAdminInvite(message.from_user.id, 1)
                bot.send_message(message.chat.id, "Введине имя нового администратора", reply_markup=cancelMarkup)
            elif (message.text == settingsAdminMenuButtons["checkInvite"]):
                inviteList = kernel.getInvitings()
                outText = botMessages["inviteList"]
                inviteListMarkup = types.InlineKeyboardMarkup()
                j = 1
                for i in inviteList:
                    outText += f"{j}. {i[2]}\n"
                    inviteListMarkup.add(types.InlineKeyboardButton(i[2], callback_data=f"o-i-{i[0]}"))
                    j += 1
                bot.send_message(message.chat.id, outText, reply_markup=inviteListMarkup, parse_mode="html")
            elif (message.text == settingsAdminMenuButtons["backToSettings"]):
                bot.send_message(message.chat.id, "Настройки", reply_markup=settingsMenuMarkup)
    elif (message.text == mainMenuButtons["RegisterUser"]):
        bot.send_message(message.chat.id, "Введите код-приглашение")
        kernel.authUser(message.from_user.id, 1)
    else:
        bot.send_message(message.chat.id, botMessages["unregisterAnswer"], reply_markup=unregisterMarkup)

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
        elif (call.data[2] == "c"): # Category
            if (call.data[4] == "1"): # Confim Ok
                kernel.createCategory(call.from_user.id, 3)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Категория создана!")
                bot.send_message(call.message.chat.id, "Главное меню", reply_markup=mainMenuMarkup)
            elif (call.data[4] == "2"): # Confim 
                kernel.createCategory(call.from_user.id, 0)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Отменено", reply_markup=None)
                bot.send_message(call.message.chat.id, "Главное меню", reply_markup=mainMenuMarkup)
        if (call.data[2] == "a"): # Admin
            if (call.data[4] == "1"): # Confirmed
                kernel.createAdminInvite(call.from_user.id, 3)
                userAction = kernel.getUsersActions(call.from_user.id)
                outText = botMessages["adminCreated"].format(userAction[1], userAction[2])
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=outText, parse_mode="html", reply_markup=None)
                bot.send_message(call.message.chat.id, "Настройки", reply_markup=settingsMenuMarkup)
                kernel.cancelAction(call.from_user.id)
            elif (call.data[4] == "2"): # Cancel
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Отменено", reply_markup=None)
                bot.send_message(call.message.chat.id, "Настройки", reply_markup=settingsMenuMarkup)
                kernel.cancelAction(call.from_user.id)
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
        elif (call.data[2] == "a"): # Admin (Name)
            if (call.data[5] == "-"):
                adminID = call.data[4]
                offset = 0
            else:
                adminID, offset = kernel.getIDWithOffset(call.data, 4)
            confirmation = int(call.data[6 + offset])
            if (confirmation == 0):
                kernel.changeAdminName(call.from_user.id, 1, adminID)
                bot.send_message(call.message.chat.id, "Изменение имени администратора", reply_markup=cancelMarkup)
                bot.send_message(call.message.chat.id, text="Введите новое имя администратора")
            elif (confirmation == 1):
                kernel.changeAdminName(call.from_user.id, 3)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Изменено", reply_markup=None)
                bot.send_message(call.message.chat.id, "Настройки", reply_markup=settingsMenuMarkup)
            elif (confirmation == 2):
                kernel.changeAdminName(call.from_user.id, 0)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Отменено", reply_markup=None)
                bot.send_message(call.message.chat.id, "Настройки", reply_markup=settingsMenuMarkup)
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
        elif (call.data[2] == "a"): # Admin
            if (call.data[5] == "-"):
                adminID = call.data[4]
                offset = 0
            else:
                adminID, offset = kernel.getIDWithOffset(call.data, 4)
                offset -= 1
            if (call.data[6 + offset] == "0"): # Confim None
                confimDeleteAdminMarkup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Да", callback_data=f"d-a-{adminID}-1-0"), types.InlineKeyboardButton("Нет", callback_data=f"d-a-{adminID}-2"))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Вы действительно хотите удалить администратора?", reply_markup=confimDeleteAdminMarkup)
            elif (call.data[6 + offset] == "1"): # Confim Ok
                kernel.deleteAdmin(adminID)
                kernel.getActualAdmins()
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Удалено", reply_markup=None)
                bot.send_message(call.message.chat.id, "Настройки", reply_markup=settingsMenuMarkup)
            elif (call.data[6 + offset] == "2"): # Confim No
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Отменено", reply_markup=None)
                bot.send_message(call.message.chat.id, "Настройки", reply_markup=settingsMenuMarkup)
        elif (call.data[2] == "i"): # Invite
            if (call.data[5] == "-"):
                inviteID = call.data[4]
                offset = 0
            else:
                inviteID, offset = kernel.getIDWithOffset(call.data, 4)
                offset -= 1
            if (call.data[6 + offset] == "0"): # Confim None
                confimDeleteInviteMarkup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Да", callback_data=f"d-i-{inviteID}-1"), types.InlineKeyboardButton("Нет", callback_data=f"d-i-{inviteID}-2"))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Вы действительно хотите удалить приглашение?", reply_markup=confimDeleteInviteMarkup)
            elif (call.data[6 + offset] == "1"): # Confim Ok
                kernel.deleteAdminInvite(inviteID)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Удалено", reply_markup=None)
            elif (call.data[6 + offset] == "2"): # Confim No
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Отменено", reply_markup=None)
        elif (call.data[2] == "c"): # Category
            if (call.data[5] == "-"):
                categoryID = call.data[4]
                offset = 0
            else:
                categoryID, offset = kernel.getIDWithOffset(call.data, 4)
            categoryID = int(categoryID)
            categoryList = kernel.getCategoryList()
            categoryName = None
            for i in categoryList:
                if categoryID == i[0]:
                    categoryName = i[1]
                    break
            deleteStatus = int(call.data[6 + offset])
            if (deleteStatus == 0): # Confim None
                confimDeleteCategoryMarkup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Да", callback_data=f"d-c-{categoryID}-1"), types.InlineKeyboardButton("Нет", callback_data=f"d-c-{categoryID}-2"))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Вы действительно хотите удалить категорию?", reply_markup=confimDeleteCategoryMarkup)
            elif (deleteStatus == 1): # Confim Ok
                kernel.deleteCategoryFromDB(categoryName)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Удалено", reply_markup=None)
                bot.send_message(call.message.chat.id, "Главное меню", reply_markup=mainMenuMarkup)
            elif (deleteStatus == 2): # Confim No
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Отменено", reply_markup=None)
                bot.send_message(call.message.chat.id, "Главное меню", reply_markup=mainMenuMarkup)
        elif (call.data[2] == "r"): # Page Cache
            if (call.data[5] == "-"):
                pageID = call.data[4]
                offset = 0
            else:
                pageID, offset = kernel.getIDWithOffset(call.data, 4)
            pageID = int(pageID)
            deleteStatus = int(call.data[6 + offset - 1])
            if (deleteStatus == 0): # Confim None
                confimDeletePageCache = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Да", callback_data=f"d-r-{pageID}-1"), types.InlineKeyboardButton("Нет", callback_data=f"d-r-{pageID}-2"))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Вы действительно хотите очистить кэш страницы?", reply_markup=confimDeletePageCache)
            elif (deleteStatus == 1): # Confim Ok
                kernel.deletePageCache(pageID)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Кэш страницы удален", reply_markup=None)
                bot.send_message(call.message.chat.id, "Главное меню", reply_markup=mainMenuMarkup)
            elif (deleteStatus == 2): # Confim No
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Отменено", reply_markup=None)
                bot.send_message(call.message.chat.id, "Главное меню", reply_markup=mainMenuMarkup)
    elif (call.data[0] == "o"): # Open
        if (call.data[2] == "a"): # Admin
            if (len(call.data) == 4):
                adminID = call.data[4]
            else:
                adminID, offset = kernel.getIDWithOffset(call.data, 4)
            adminData = kernel.getAdminList(adminID)
            outText = botMessages["OpenAdmin"].format(adminData[0], adminData[1], adminData[2], adminData[3], adminData[4])
            editAdminMarkup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Изменить имя", callback_data=f"s-a-{adminData[0]}-0"), types.InlineKeyboardButton("Удалить", callback_data=f"d-a-{adminData[0]}-0"))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=outText, reply_markup=editAdminMarkup)
        elif (call.data[2] == "i"): # Invite
            if (len(call.data) == 4):
                inviteID, offset = call.data[4]
            else:
                inviteID, offset = kernel.getIDWithOffset(call.data, 4)
            invite = kernel.getInvitings(inviteID)
            outText = botMessages["inviteListItemOpen"].format(invite[0], invite[1], invite[2], invite[3])
            inviteDeleteMarkup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Удалить", callback_data=f"d-i-{inviteID}-0"))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=outText, parse_mode="html", reply_markup=inviteDeleteMarkup)
        elif (call.data[2] == "c"): # Category
            if (len(call.data) == 4):
                categoryID = call.data[4]
                offset = 0
            else:
                categoryID, offset = kernel.getIDWithOffset(call.data, 4)
            categoryID = int(categoryID)
            categoryList = kernel.getCategoryList()
            for i in categoryList:
                if categoryID == i[0]:
                    category = i
                    break
            outText = botMessages["openCategory"].format(category[0], category[1], category[2])
            openCategoryMarkup = types.InlineKeyboardMarkup()
            openCategoryMarkup.add(
                types.InlineKeyboardButton("Просмотр страниц", callback_data=f"o-s-{categoryID}"),
                types.InlineKeyboardButton("Удалить категорию", callback_data=f"d-c-{categoryID}-0")
            )
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=outText, reply_markup=openCategoryMarkup)
        elif (call.data[2] == "s"): # Category pages
            if (len(call.data) == 4):
                categoryID = call.data[4]
                offset = 0
            else:
                categoryID, offset = kernel.getIDWithOffset(call.data, 4)
            categoryID = int(categoryID)
            categoryList = kernel.getCategoryList()
            categoryName = None
            for i in categoryList:
                if categoryID == i[0]:
                    categoryName = i[1]
                    break
            pageList = kernel.getCategoryPageList(categoryName)
            outText = "Список страниц:\n"
            pageListMarkup = types.InlineKeyboardMarkup()
            j = 1
            for i in pageList:
                outText += f"{j}. {i[1]}\n"
                pageListMarkup.add(types.InlineKeyboardButton(i[1], callback_data=f"o-p-{i[0]}"))
                j += 1
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=outText, reply_markup=pageListMarkup)
        elif (call.data[2] == "p"):
            if (len(call.data) == 4):
                pageID = call.data[4]
                offset = 0
            else:
                pageID, offset = kernel.getIDWithOffset(call.data, 4)
            pageID = int(pageID)
            pageData, pageContent = kernel.getPageData(pageID)
            outText = botMessages["pageData"].format(pageData[0], pageData[1], pageData[2], pageData[3], pageData[4], kernel.getStrFromBool(pageData[5]), kernel.getStrFromBool(pageData[6]))
            pageOpenMarkup = types.InlineKeyboardMarkup()
            pageOpenMarkup.add(
                types.InlineKeyboardButton("Переименовать страницу", callback_data=f"s-p-{pageID}"),
                types.InlineKeyboardButton("Изменить контент страницы", callback_data=f"s-r-{pageID}"),
            )
            if (pageData[5] != None):
                pageOpenMarkup.add(types.InlineKeyboardButton("Удалить кэш страницы", callback_data=f"d-r-{pageID}-0"))
            pageOpenMarkup.add(
                types.InlineKeyboardButton("Скрыть страницу", callback_data=f"s-h-{pageID}-0"),
                types.InlineKeyboardButton("Удалить страницу", callback_data=f"d-p-{pageID}-0")
            )
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=outText, reply_markup=pageOpenMarkup)
            
bot.infinity_polling()