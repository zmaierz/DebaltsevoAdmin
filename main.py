import telebot
from telebot import types
import engine.kernel as Core

Core.logging.info(f"{Core.functions.getActualTime()}:Запуск бота")

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

@bot.message_handler(content_types=['photo'])
def photo(message):
    if (kernel.isUserActive(message.from_user.id)):
        usersActions = kernel.getUsersActions(message.from_user.id)
        if (usersActions[0] == "blockCreate"):
            if ((usersActions[4] == 4) and (usersActions[1] == "photo")): # Ввод data            
                fileID = message.photo[-1].file_id   
                file_info = bot.get_file(fileID)
                downloaded_file = bot.download_file(file_info.file_path)
                imageName = kernel.generateString(10)  + ".jpg"
                webPath = kernel.getWebPath()
                saveName = webPath + "engine/templates/media/images/" + imageName
                with open(saveName, 'wb') as new_file:
                    new_file.write(downloaded_file)
                kernel.blockCreate(message.from_user.id, 4, imageName)
                userAction = kernel.getUsersActions(message.from_user.id)
                outText = botMessages["checkNewBlock"].format(userAction[1], userAction[2], userAction[3])
                confimBlockCreateMarkup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Да", callback_data=f"c-d-1-{userAction[5]}"), types.InlineKeyboardButton("Отмена", callback_data=f"c-d-2-{userAction[5]}"))
                bot.send_message(message.chat.id, outText, reply_markup=confimBlockCreateMarkup)
            else:
                bot.send_message(message.chat.id, "Неверный тип данных!")
        else:
            bot.send_message(message.chat.id, "Неверный тип данных!")
    else:
        bot.send_message(message.chat.id, "Неверный тип данных!")

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
                    if (kernel.checkStringValid(message.text) == False):
                        bot.send_message(message.chat.id, "Используются запрещенные символы!\nРазрешено использовать только цифры, русские и латинские символы")
                    else:
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
                    elif (kernel.checkStringValid(message.text) == False):
                        bot.send_message(message.chat.id, "Используются запрещенные символы!\nРазрешено использовать только цифры, русские и латинские символы")
                    else:
                        kernel.createCategory(message.from_user.id, 2, message.text)
                        confimCreateCategoryMarkup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Да", callback_data="c-c-1"), types.InlineKeyboardButton("Нет", callback_data="c-c-2"))
                        outText = f"Вы действительно хотите создать категорию {message.text}?"
                        bot.send_message(message.chat.id, outText, reply_markup=confimCreateCategoryMarkup)
            elif (usersActions[0] == "blockCreate"):
                if (usersActions[4] == 2): # Ввод типа блока
                    if (kernel.checkTypeInList(message.text)):
                        kernel.blockCreate(message.from_user.id, 2, message.text)
                        if (message.text == "doc"):
                            bot.send_message(message.chat.id, "Укажите название документа")
                        elif (message.text == "block"):
                            bot.send_message(message.chat.id, "Укажите заголовок")
                        else:
                            kernel.usersActions[message.from_user.id][4] = 4
                            bot.send_message(message.chat.id, "Укажите контент")
                    else:
                        bot.send_message(message.chat.id, "Указана неверная категория!")
                elif (usersActions[4] == 3):
                    kernel.blockCreate(message.from_user.id, 3, message.text)
                    bot.send_message(message.chat.id, "Укажите контент")
                elif (usersActions[4] == 4):
                    kernel.blockCreate(message.from_user.id, 4, message.text)
                    userAction = kernel.getUsersActions(message.from_user.id)
                    outText = botMessages["checkNewBlock"].format(userAction[1], userAction[2], userAction[3])
                    confimBlockCreateMarkup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Да", callback_data=f"c-d-1-{userAction[5]}"), types.InlineKeyboardButton("Отмена", callback_data=f"c-d-2-{userAction[5]}"))
                    bot.send_message(message.chat.id, outText, reply_markup=confimBlockCreateMarkup)
            elif (usersActions[0] == "blockEdit"):
                if (int(usersActions[4]) == 3): # Ввод данных
                    kernel.changeBlock(message.from_user.id, 4, message.text)
                    outText = botMessages["editBlock"].format(usersActions[5], usersActions[1], usersActions[2], usersActions[3])
                    editBlockMarkup = types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("Изменить", callback_data=f"s-b-{usersActions[5]}-{usersActions[1]}-{usersActions[2]}-1"),
                        types.InlineKeyboardButton("Отменить", callback_data=f"s-b-{usersActions[5]}-{usersActions[1]}-{usersActions[2]}-2"),
                    )
                    bot.send_message(message.chat.id, outText, reply_markup=editBlockMarkup)
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
            openLogMarkup = types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("Лог бота", callback_data="o-l-1"),
                types.InlineKeyboardButton("Лог действий администраторов", callback_data="o-l-2"),
                types.InlineKeyboardButton("Лог сайта", callback_data="o-l-3"),
                types.InlineKeyboardButton("Лог инцидентов сайта", callback_data="o-l-4")
            )
            bot.send_message(message.chat.id, "Выберите, что вы хотите увидеть", reply_markup=openLogMarkup)
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
        elif (call.data[2] == "a"): # Admin
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
        elif (call.data[2] == "b"): # Page Block
            if (call.data[5] == "-"):
                pageID = call.data[4]
                offset = 0
            else:
                pageID, offset = kernel.getIDWithOffset(call.data, 4)
                offset -= 1
            kernel.blockCreate(call.from_user.id, 1, pageID)
            typeList = kernel.getBlockTypeList()
            outText = "Выберите блок:\n"
            typeListMarkup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            j = 1
            for i in typeList:
                outText += f"{j}. {i[0]}\n"
                typeListMarkup.add(types.KeyboardButton(i[0]))
                j += 1
            typeListMarkup.add(types.KeyboardButton(mainMenuButtons["CancelAction"]))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Создание блока", reply_markup=None)
            bot.send_message(call.message.chat.id, outText, reply_markup=typeListMarkup)
        elif (call.data[2] == "d"): # Page block confim
            pageID, offset = kernel.getIDWithOffset(call.data, 6)
            if (call.data[4] == "1"): # Confim ok
                kernel.blockCreate(call.from_user.id, 5)
                backToPageMarkup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Назад", callback_data=f"s-r-{pageID}"))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Блок создан", reply_markup=backToPageMarkup)
                bot.send_message(call.message.chat.id, "Главное меню", reply_markup=mainMenuMarkup)
            elif (call.data[4] == "2"): # Confim no
                backToPageMarkup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Назад", callback_data=f"s-r-{pageID}"))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Создание блока отменено", reply_markup=backToPageMarkup)
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
        elif (call.data[2] == "h"): # Page hide/open
            if (call.data[5] == "-"):
                pageID = call.data[4]
                offset = 0
            else:
                pageID, offset = kernel.getIDWithOffset(call.data, 4)
                offset -= 1
            status = int(call.data[6 + offset])
            if (status == 0): # Confim None
                confimChangeHidePageMarkup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Да", callback_data=f"s-h-{pageID}-1"), types.InlineKeyboardButton("Нет", callback_data=f"s-h-{pageID}-2"))
                if (kernel.isPageHide(pageID)):
                    action = "скрыть"
                else:
                    action = "открыть"
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=f"Вы действительно хотите {action} страницу?", reply_markup=confimChangeHidePageMarkup)
            elif (status == 1): # Confim Ok
                if (kernel.isPageHide(pageID)):
                    action = 1
                    actionText = "скрыта"
                else:
                    action = 0
                    actionText = "открыта"
                kernel.hidePage(pageID, action)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=f"Страница {actionText}", reply_markup=None)
                bot.send_message(call.message.chat.id, "Главная", reply_markup=mainMenuMarkup)
            elif (status == 2): # Confim No
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Отменено", reply_markup=None)
                bot.send_message(call.message.chat.id, "Главная", reply_markup=mainMenuMarkup)
        elif (call.data[2] == "r"): # Page content
            if (len(call.data) == 4):
                pageID = call.data[4]
                offset = 0
            else:
                pageID, offset = kernel.getIDWithOffset(call.data, 4)
            pageData, pageContent = kernel.getPageData(pageID)
            outData = "Содержание страницы:\n"
            j = 0
            pageOpenContentMarkup = types.InlineKeyboardMarkup()
            for i in pageContent:
                outData += f"{j}. {i[1]}: {i[3]} ({i[2]})\n"
                pageOpenContentMarkup.add(types.InlineKeyboardButton(text=f"{j}. {i[3][:10]}", callback_data=f"o-b-{pageID}-{i[0]}"))
                j += 1
            pageOpenContentMarkup.add(types.InlineKeyboardButton(text="Создать блок", callback_data=f"c-b-{pageID}-0"))
            pageOpenContentMarkup.add(types.InlineKeyboardButton(text="Назад", callback_data=f"o-p-{pageID}"))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=outData, reply_markup=pageOpenContentMarkup)
        elif (call.data[2] == "b"): # Block
            if (call.data[5] == "-"):
                pageID = call.data[4]
                pageOffset = 0
            else:
                pageID, pageOffset = kernel.getIDWithOffset(call.data, 4)
                pageOffset -= 1
            if (call.data[7 + pageOffset] == "-"):
                blockID = call.data[6 + pageOffset]
                blockOffset = 0
            else:
                blockID, blockOffset = kernel.getIDWithOffset(call.data, pageOffset)
                blockOffset -= 1
            blockContentType = int(call.data[8 + pageOffset + blockOffset])
            confim = int(call.data[10 + pageOffset + blockOffset])
            if (confim == 0): # Confim None
                kernel.changeBlock(call.from_user.id, 1, int(pageID))
                kernel.changeBlock(call.from_user.id, 2, int(blockID))
                kernel.changeBlock(call.from_user.id, 3, int(blockContentType))
                changeType = "содержания"
                if (blockContentType == 1):
                    changeType = "заголовка"
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=f"Изменение {changeType}", reply_markup=None)
                bot.send_message(call.message.chat.id, "Введите новые данные", reply_markup=cancelMarkup)
            elif (confim == 1): # Confim Ok
                kernel.changeBlock(call.from_user.id, 5)
                editBlockBackMarkup = types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("Назад", callback_data=f"o-b-{pageID}-{blockID}")
                )
                kernel.cancelAction(call.from_user.id)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Изменено", reply_markup=editBlockBackMarkup)
                bot.send_message(call.message.chat.id, "Главное меню", reply_markup=mainMenuMarkup)
            elif (confim == 2): # Confim No
                editBlockBackMarkup = types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("Назад", callback_data=f"o-b-{pageID}-{blockID}")
                )
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Отменено", reply_markup=editBlockBackMarkup)
    elif (call.data[0] == "d"): # Delete
        if (call.data[2] == "s"): # Cache
            if (call.data[4] == "0"): # Confirm None
                confimDeleteCacheMarkup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Да", callback_data="d-s-1"), types.InlineKeyboardButton("Нет", callback_data="d-s-2"))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Вы действительно хотите очистить весь кэш?", reply_markup=confimDeleteCacheMarkup)
            elif (call.data[4] == "1"): # Confim Ok
                kernel.deleteAllCache(call.from_user.id)
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
                kernel.deleteAdmin(adminID, call.from_user.id)
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
                kernel.deleteAdminInvite(inviteID, call.from_user.id)
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
                kernel.deleteCategoryFromDB(categoryName, call.from_user.id)
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
                kernel.deletePageCache(pageID, call.from_user, id)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Кэш страницы удален", reply_markup=None)
                bot.send_message(call.message.chat.id, "Главное меню", reply_markup=mainMenuMarkup)
            elif (deleteStatus == 2): # Confim No
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Отменено", reply_markup=None)
                bot.send_message(call.message.chat.id, "Главное меню", reply_markup=mainMenuMarkup)
        elif (call.data[2] == "p"): # Page
            if (call.data[5] == "-"):
                pageID = call.data[4]
                offset = 0
            else:
                pageID, offset = kernel.getIDWithOffset(call.data, 4)
                offset -= 1
            pageID = int(pageID)
            deleteStatus = int(call.data[6 + offset])
            if (deleteStatus == 0): # Confim None
                confimPageDeleteMarkup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Да", callback_data=f"d-p-{pageID}-1"), types.InlineKeyboardButton("Нет", callback_data=f"d-p-{pageID}-2"))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Вы действительно хотите удалить страницу?", reply_markup=confimPageDeleteMarkup)
            elif (deleteStatus == 1): # Confim Ok
                kernel.deletePage(pageID, call.from_user.id)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Страница удалена", reply_markup=None)
                bot.send_message(call.message.chat.id, "Главное меню", reply_markup=mainMenuMarkup)
            elif (deleteStatus == 2): # Confim No
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Отменено", reply_markup=None)
                bot.send_message(call.message.chat.id, "Главное меню", reply_markup=mainMenuMarkup)
        elif (call.data[2] == "b"): # Block
            if (call.data[5] == "-"):
                pageID = call.data[4]
                pageOffset = 0
            else:
                pageID, pageOffset = kernel.getIDWithOffset(call.data, 4)
                pageOffset -= 1
            if (pageOffset == 0):
                blockID = call.data[6]
                blockOffset = 0
            else:
                blockID, blockOffset = kernel.getIDWithOffset(call.data, 6 + pageOffset)
                pageOffset -= 1
            if (pageOffset == 0 and blockOffset == 0):
                deleteStatus = int(call.data[8])
            else:
                deleteStatus = int(call.data[8 + pageOffset + blockOffset])
            if (deleteStatus == 0): # Confim none
                confimDeleteBlockMarkup = types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("Да", callback_data=f"d-b-{pageID}-{blockID}-1"),
                    types.InlineKeyboardButton("Нет", callback_data=f"d-b-{pageID}-{blockID}-2")
                )
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Вы действительно хотите удалить блок?", reply_markup=confimDeleteBlockMarkup)
            elif (deleteStatus == 1): # Confim ok
                kernel.deleteBlock(pageID, blockID, call.from_user.id)
                backToOpenBlockMarkup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Назад", callback_data=f"o-p-{pageID}"))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Удалено", reply_markup=backToOpenBlockMarkup)
            elif (deleteStatus == 2): # Confim No
                backToOpenBlockMarkup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Назад", callback_data=f"o-b-{pageID}-{blockID}"))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Отменено", reply_markup=backToOpenBlockMarkup)
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
        elif (call.data[2] == "p"): # Page
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
            if (kernel.isPageHide(pageID)):
                pageHideAction = "Скрыть"
            else:
                pageHideAction = "Открыть"
            pageOpenMarkup.add(
                types.InlineKeyboardButton(f"{pageHideAction} страницу", callback_data=f"s-h-{pageID}-0"),
                types.InlineKeyboardButton("Удалить страницу", callback_data=f"d-p-{pageID}-0")
            )
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=outText, reply_markup=pageOpenMarkup)
        elif (call.data[2] == "l"): # Log
            if (call.data[4] == "1"): # Log bot
                data = kernel.getLog("bot")
                outData = "Лог бота:\n"
                j = 1
                for i in data:
                    outData += f"{j}.\nID: {i[0]}\nSource: {i[1]}\nData: {i[2]}\nДата: {i[3]}"
                    j += 1
            elif (call.data[4] == "2"): # Log action
                data = kernel.getLog("action")
                outData = "Лог действий администраторов:\n"
                j = 1
                for i in data:
                    outData += f"{j}.\nID: {i[0]}\nAdminID: {i[1]}\nActionType: {i[2]}\nData:{i[3]}\nДата: {i[4]}\n\n"
                    j += 1
            elif (call.data[4] == "3"): # Log site
                outData = "В разработке."
            elif (call.data[4] == "4"): # Log incident
                data = kernel.getLog("incident")
                outData = "Лог инцидентов:\n"
                j = 1
                for i in data:
                    outData += f"{j}.\nID: {i[0]}\nТип инцидента: {i[1]}\nНазвание: {i[2]}\nОписание: {i[3]}\nSubdata: {i[4]}\nData: {i[5]}, Дата: {i[6]}\n\n"
                    j += 1
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=outData)
        elif (call.data[2] == "b"): # Block
            if (call.data[5] == "-"):
                pageID = call.data[4]
                offsetPage = 0
            else:
                pageID, offsetPage = kernel.getIDWithOffset(call.data, 4)
                offsetPage -= 1
            if (offsetPage == 0):
                blockID = call.data[6]
            else:
                blockID, offsetBlock = kernel.getIDWithOffset(call.data, 6 + offsetPage)
            pageData, pageContent = kernel.getPageData(pageID)
            blockData = kernel.getBlockData(pageData[4], blockID)
            outData = botMessages["blockContent"].format(blockData[0], blockData[1], blockData[2], blockData[3])
            openBlockMarkup = types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("Изменить Заголовок", callback_data=f"s-b-{pageID}-{blockID}-1-0"),
                types.InlineKeyboardButton("Изменить содержание", callback_data=f"s-b-{pageID}-{blockID}-2-0"),
                types.InlineKeyboardButton("Удалить блок", callback_data=f"d-b-{pageID}-{blockID}-0"),
                types.InlineKeyboardButton("Назад", callback_data=f"s-r-{pageID}")
            )
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=outData, reply_markup=openBlockMarkup)

bot.infinity_polling()