def getMainMenuButtons():
    return {
        "createNewPage" : "Создание страницы",
        "Categories" : "Категории",
        "News" : "Новости",
        "Settings" : "Настройки",
        "Logs" : "Логи",
        "RegisterUser" : "Ввести код-приглашение",
        "CancelAction" : "❌ Отмена",
    }

def getSettingsMenuButtons():
    return {
        "cache" : "Кэш",
        "checkFiles" : "Просмотр файлов",
        "changeSiteInformation" : "Изменение информации о сайте",
        "manage" : "Управление",
        "admins" : "Админы",
        "version" : "Версия",
        "back" : "Назад на главную",
    }

def getSettingsAdminMenuButtons():
    return {
        "createNewAdmin" : "Создать нового администратора",
        "checkInvite" : "Просмотр приглашений",
        "backToSettings" : "Назад в настройки"
    }

def getMessages():
    return {
        "registerUserSuccess" : "{0}, приглашение активировано!\nИмя администратора: {1}",
        "welcomeRegister" : "Добрый день, {0}!\n🟢 Вы авторизованы",
        "welcomeUnRegister" : "Добрый день, {0}!\n🟥 Вы не авторизованы!",
        "unregisterAnswer" : "Вы не авторизованы.",
        "cancelAction" : "Отмена операции",
        "createPage_start" : "Для создания новой страницы необходимо ввести следующую информацию:\n1. Название\n2. Категорию\n3. Скрыть ли страницу",
        "createPage_enterName" : "Введите название новой страницы",
        "createPage_enterCategory" : "Выберите категорию",
        "createPage_isHide" : "Скрыть страницу?",
        "createPage_Confim" : "Проверьте правильность информации:\n\nНазвание: {0}\nКатегория: {1}\nСкрыть: {2}\n\nСохранить?",
        "createPage_cancel" : "Отмена создания страницы",
        "createPage_Ok" : "Создание страницы",
        "settingsText" : "Настройки",
        "settingsCache" : "Использование кэша: {0}",
        "settingsManage" : "Режим дебага: {0}\nИспользование кэша: {1}",
        "settingsAdmin" : "Список администраторов:\n{0}\n1. Создать нового администратора\n2. Просмотр приглашений\n3. Назад в настройки",
        "OpenAdmin" : "Admin ID: {0}\nTelegram ID: {1}\nДата создания: {2}\nСоздал: {3}\nИмя: {4}",
        "confimChangeAdminName" : "Действительно изменить имя администратора?\nAdminID: {0}\nНовое имя: {1}",
        "confimCreateAdmin" : "Вы действительно хотите создать приглашение для администратора {0}?",
        "adminCreated" : "Создан администратор {0}\n\nСсылка-приглашение: <code>{1}</code>"
    }