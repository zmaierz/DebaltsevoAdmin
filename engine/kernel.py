import configparser

import engine.DB.DB as database

import engine.modules.messages_text as messages
import engine.modules.functions as functions

class Kernel:
    def __init__(self):
        self.MainMenuButtons = messages.getMainMenuButtons()
        self.settingsButtons = messages.getSettingsMenuButtons()
        self.settingsAdminButtons = messages.getSettingsAdminMenuButtons()
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
        self.getActualAdmins()
        self.usersActions = {}
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
    def createAdminInvite(self, userID, status, data=""):
        status = int(status)
        if (status == 1): # Начало создания
            self.usersActions[userID] = ["createAdminInvite", "", "", "", 2]
        elif (status == 2): # Ввод имени
            self.usersActions[userID][1] = data
            self.usersActions[userID][4] = 3
        elif (status == 3): # Подтверждение
            inviteCode = functions.generateAdminInviteCode()
            self.botDatabase.executeQuery(f"INSERT INTO `AdminInvitings_BOT` (`ID`, `Code`, `Name`, `CreationDate`, `Creator`, `Activated`, `ActivatedBy`) VALUES (NULL, '{inviteCode}', '{self.usersActions[userID][1]}', '{functions.getActualTime()}', '{userID}', '0', NULL)")
            self.usersActions[userID][2] = inviteCode
        elif (status == 0): # Отмена. Удаление записи
            self.cancelAction(userID)
    def changeAdminName(self, userID, status, data=""):
        status = int(status)
        if (status == 1): # Начало изменения имени. data - AdminID
            self.usersActions[userID] = ["changeAdminName", data, "", "", 2]
        elif (status == 2): # Ввод нового имени
            self.usersActions[userID][2] = data
            self.usersActions[userID][4] = 3
        elif (status == 3): # Подтверждение. Изменение имени
            self.botDatabase.executeQuery(f"UPDATE `Admins_BOT` SET `Name` = '{self.usersActions[userID][2]}' WHERE `Admins_BOT`.`ID` = {self.usersActions[userID][1]};")
            self.cancelAction(userID)
        elif (status == 0): # Отмена. Удаление записи
            self.cancelAction(userID)
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
    def getSettingsMenuButtons(self):
        return self.settingsButtons
    def getSettingsAdminMenuButtons(self):
        return self.settingsAdminButtons
    def getMessages(self):
        return self.Messages
    def getIDWithOffset(self, call, startPlace):
        return functions.getIDWithOffset(call, startPlace)
    def getUsersActions(self, id = None):
        if (id == None):
            return self.usersActions
        if (id not in self.usersActions):
            print(f"ID {id} не найден!\n{self.usersActions}")
            return None
        return self.usersActions[id]
    def getCategoryList(self):
        return self.categoryList
    def getAdminList(self, adminID = None):
        adminList = self.botDatabase.getData("SELECT * FROM `Admins_BOT`")
        if (adminID == None):
            return adminList
        for i in adminList:
            if (str(i[0]) == adminID):
                return i
        return None
    def deleteAdmin(self, adminID):
        self.botDatabase.executeQuery(f"DELETE FROM Admins_BOT WHERE `Admins_BOT`.`ID` = {adminID}")
    def getCategoryFromID(self, categoryID):
        categoryID = int(categoryID)
        for i in self.categoryList:
            if (i[0] == categoryID):
                return i[1]
        return None
    def getStrFromBool(self, temp):
        temp = int(temp)
        if (temp == 1):
            return "🟢 Да"
        else:
            return "🟥 Нет"
    def cancelAction(self, id):
        del self.usersActions[id]
    def isDebug(self):
        return self.debug
    def changeCacheStatus(self, newStatus):
        if (newStatus):
            newStatus = "true"
            oldStatus = "false"
        else:
            newStatus = "false"
            oldStatus = "true"
        webConfig = functions.getFileContent(self.webPath + "engine/config/kernelConfig.php")
        cacheStatus = webConfig.partition("\"useCache\" =>")
        newConfig = cacheStatus[0] + cacheStatus[1]
        endConfig = cacheStatus[2].partition(oldStatus)
        newConfig += newStatus + endConfig[2]
        functions.writeFileContent(self.webPath + "engine/config/kernelConfig.php", newConfig)
    def getCacheStatus(self):
        webConfig = functions.getFileContent(self.webPath + "engine/config/kernelConfig.php")
        cacheStatus = webConfig.partition("\"useCache\" =>")[2].strip()[0]
        if (cacheStatus == "t"):
            return True
        return False
    def getDebugStatus(self):
        webConfig = functions.getFileContent(self.webPath + "engine/config/kernelConfig.php")
        cacheStatus = webConfig.partition("\"debug\" =>")[2].strip()[0]
        if (cacheStatus == "t"):
            return True
        return False
    def changeDebugStatus(self, newStatus):
        if (newStatus):
            newStatus = "true"
            oldStatus = "false"
        else:
            newStatus = "false"
            oldStatus = "true"
        webConfig = functions.getFileContent(self.webPath + "engine/config/kernelConfig.php")
        cacheStatus = webConfig.partition("\"debug\" =>")
        newConfig = cacheStatus[0] + cacheStatus[1]
        endConfig = cacheStatus[2].partition(oldStatus)
        newConfig += newStatus + endConfig[2]
        functions.writeFileContent(self.webPath + "engine/config/kernelConfig.php", newConfig)
    def deleteAllCache(self):
        functions.deleteDirectoryContent(self.webPath + self.cachePath + "system/")
        functions.deleteDirectoryContent(self.webPath + self.cachePath + "pages/")
    def isAdmin(self, id):
        if (str(id) in self.actualAdmins):
            return True
        else:
            return False
    def getActualAdmins(self):
        self.adminList = self.botDatabase.getData("SELECT * FROM `Admins_BOT`")
        self.actualAdmins = []
        for admin in self.adminList:
            self.actualAdmins.append(admin[1])
    def checkButtonFromList(self, type, data):
        if (type == "settings"):
            for i in self.settingsButtons:
                if (self.settingsButtons[i] == data):
                    return True
            return False
        elif (type == "settingsAdmin"):
            for i in self.settingsAdminButtons:
                if (self.settingsAdminButtons[i] == data):
                    return True
            return False