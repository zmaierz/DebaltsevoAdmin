import configparser

import engine.DB.DB as database

import engine.modules.messages_text as messages
import engine.modules.functions as functions

class Kernel:
    def __init__(self):
        self.MainMenuButtons = messages.getMainMenuButtons()
        self.Messages = messages.getMessages()

        self.kernelConfig = configparser.ConfigParser()
        self.DBConfig = configparser.ConfigParser()

        self.kernelConfig.read('engine/config/kernel.conf')
        self.DBConfig.read('engine/config/db.conf')

        self.botToken = self.kernelConfig.get("BOT", "token")
        self.webPath = self.kernelConfig.get("BOT", "web-path")
        self.cachePath = self.kernelConfig.get("BOT", "cache-path")
        debug = self.kernelConfig.get("BOT", "debug")
        if (debug == "true"):
            self.debug = True
        else:
            self.debug = False

        self.webDBConfig = {
            "username" : self.DBConfig.get("WEB", "username"),
            "password" : self.DBConfig.get("WEB", "password"),
            "hostname" : self.DBConfig.get("WEB", "hostname"),
            "database" : self.DBConfig.get("WEB", "database"),
            "port" : self.DBConfig.get("WEB", "port"),
        }
        if (self.DBConfig.get("BOT", "as-web") == "true"):
            self.botDBConfig = self.webDBConfig
        else:
            self.botDBConfig = {
                "username" : self.DBConfig.get("BOT", "username"),
                "password" : self.DBConfig.get("BOT", "password"),
                "hostname" : self.DBConfig.get("BOT", "hostname"),
                "database" : self.DBConfig.get("BOT", "database"),
                "port" : self.DBConfig.get("BOT", "port"),
            }
        
        self.webDatabase = database.Database(
            username=self.webDBConfig["username"],
            password=self.webDBConfig["password"],
            hostname=self.webDBConfig["hostname"],
            database=self.webDBConfig["database"],
            port=self.webDBConfig["port"],
        )
        self.botDatabase = database.Database(
            username=self.botDBConfig["username"],
            password=self.botDBConfig["password"],
            hostname=self.botDBConfig["hostname"],
            database=self.botDBConfig["database"],
            port=self.botDBConfig["port"],
        )
        self.usersActions = {}
        self.adminList = self.botDatabase.getData("SELECT * FROM `Admins_BOT`")
        self.actualAdmins = []
        for admin in self.adminList:
            self.actualAdmins.append(admin[1])
        self.categoryList = self.webDatabase.getData("SELECT * FROM `categoryList`")

    def pageCreate(self, adminID, status, data = ""):
        status = int(status)
        if (status == 1): # Начала создания страницы
            self.usersActions[adminID] = ["pageCreate", "", "", "", 2]
        elif (status == 2): # Ввод имени
            self.usersActions[adminID][1] = data
            self.usersActions[adminID][4] = 3
        elif (status == 3): # Ввод категории
            self.usersActions[adminID][2] = data
            self.usersActions[adminID][4] = 4
        elif (status == 4): # Скрытие страницы
            self.usersActions[adminID][3] = data
            self.usersActions[adminID][4] = 5
        elif (status == 5): # Подтверждение. Создание страницы
            alias = functions.translitText(self.usersActions[adminID][1])
            alias = alias.replace(" ", "_")
            self.createPageToWeb(self.usersActions[adminID][1], alias, self.getCategoryFromID(self.usersActions[adminID][2]), self.usersActions[adminID][3])
            self.cancelAction(adminID)
        elif (status == 0): # Отмена. Удаление записи
            self.cancelAction(adminID)
    def isUserActive(self, id):
        if (id in self.usersActions):
            return True
        return False
    def createPageToWeb(self, pageName, pageAlias, pageCategory, pageHide):
        addPageToListQuery = f"INSERT INTO `pageList` (`ID`, `name`, `alias`, `category`, `tableName`, `cacheName`, `isHide`) VALUES (NULL, '{pageName}', '{pageAlias}', '{pageCategory}', '{pageAlias}_Page', NULL, '{pageHide}')"
        createPageTableQuery = f"CREATE TABLE `debaltsevo-web`.`{pageAlias}_Page` (`ID` INT NOT NULL AUTO_INCREMENT , `type` VARCHAR(32) NOT NULL , `subdata` VARCHAR(128) NOT NULL , `data` TEXT NOT NULL , PRIMARY KEY (`ID`)) ENGINE = InnoDB;"
        createPageConnectionQuery = f"ALTER TABLE `{pageAlias}_Page` ADD FOREIGN KEY (`type`) REFERENCES `typeList`(`Name`) ON DELETE RESTRICT ON UPDATE RESTRICT;"
        self.webDatabase.executeQuery(addPageToListQuery)
        self.webDatabase.executeQuery(createPageTableQuery)
        self.webDatabase.executeQuery(createPageConnectionQuery)
        systemCachePath = self.webPath + self.cachePath + "system/"
        functions.deleteFile(systemCachePath + "footer.html")
        functions.deleteFile(systemCachePath + "header.html")
    def getToken(self):
        return self.botToken
    def getWebDBConfig(self):
        return self.webDBConfig
    def getBotDBConfig(self):
        return self.botDBConfig
    def getMainMenuButtons(self):
        return self.MainMenuButtons
    def getMessages(self):
        return self.Messages
    def getUsersActions(self, id = None):
        if (id == None):
            return self.usersActions
        if (id not in self.usersActions):
            print(f"ID {id} не найден!\n{self.usersActions}")
            return None
        return self.usersActions[id]
    def getCategoryList(self):
        return self.categoryList
    def getCategoryFromID(self, categoryID):
        categoryID = int(categoryID)
        for i in self.categoryList:
            if (i[0] == categoryID):
                return i[1]
        return None
    def getStrFromBool(self, temp):
        temp = int(temp)
        if (temp == 1):
            return "Да"
        else:
            return "Нет"
    def cancelAction(self, id):
        del self.usersActions[id]
    def isDebug(self):
        return self.debug
    def isAdmin(self, id):
        if (str(id) in self.actualAdmins):
            return True
        else:
            return False