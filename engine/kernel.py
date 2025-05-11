import configparser
import logging

import engine.DB.DB as database

import engine.modules.messages_text as messages
import engine.modules.functions as functions

logging.basicConfig(level=logging.INFO, filename="engine/main.log", filemode="a")

class Kernel:
    def __init__(self):
        self.MainMenuButtons = messages.getMainMenuButtons()
        self.settingsButtons = messages.getSettingsMenuButtons()
        self.settingsAdminButtons = messages.getSettingsAdminMenuButtons()
        self.categoryMenuButtons = messages.getCategoryMenuButtons()
        self.Messages = messages.getMessages()

        self.kernelConfig = configparser.ConfigParser()
        self.DBConfig = configparser.ConfigParser()

        self.kernelConfig.read('engine/config/kernel.conf')
        self.DBConfig.read('engine/config/db.conf')

        self.botToken = self.kernelConfig.get("BOT", "token")
        self.webPath = self.kernelConfig.get("BOT", "web-path")
        self.cachePath = self.kernelConfig.get("BOT", "cache-path")
        debug = self.kernelConfig.get("BOT", "debug")
        self.hostVersion = self.kernelConfig.get("BOT", "hostname")
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
        self.systemData = functions.getSystemData()
        self.getActualAdmins()
        self.usersActions = {}
        self.usersAuth = {}
        self.updateCategoryList()

    def getVersions(self):
        return [self.systemData["version"]["botVersion"], self.systemData["version"]["siteVersion"], self.hostVersion]
    def authUser(self, userID, status, data = ""):
        status = int(status)
        if (status == 1): # Начало авторизации
            self.usersAuth[userID] = ""
        elif (status == 2): # Ввод кода
            self.usersAuth[userID] = data
    
    def checkAdminInvite(self, code):
        admin = self.botDatabase.getData(f"SELECT * FROM `AdminInvitings_BOT` WHERE `Code` = \"{code}\";")
        if (admin == []):
            return False
        else:
            return admin[0][2]
        
    def delAuthUser(self, userID):
        del self.usersAuth[userID]

    def createAdmin(self, userID, inviteCode):
        invite = self.botDatabase.getData(f"SELECT * FROM `AdminInvitings_BOT` WHERE `Code` = \"{inviteCode}\";")[0]
        inviteID = invite[0]
        inviteCreator = invite[4]
        inviteAdminName = invite[2]
        try:
            self.botDatabase.executeQuery(functions.generateActionLogQuery(userID, "useAdminInvite"))
            self.botDatabase.executeQuery(f"UPDATE `AdminInvitings_BOT` SET `Activated` = '1' WHERE `AdminInvitings_BOT`.`ID` = {inviteID};")
            self.botDatabase.executeQuery(f"INSERT INTO `Admins_BOT` (`ID`, `TID`, `CreationDate`, `Creator`, `Name`) VALUES (NULL, '{userID}', '{functions.getActualTime()}', '{inviteCreator}', '{inviteAdminName}')")
            self.botDatabase.executeQuery(f"UPDATE `AdminInvitings_BOT` SET `ActivatedBy` = '{userID}' WHERE `AdminInvitings_BOT`.`ID` = {inviteID};")
        except database.mysql.connector.Error as e:
            try:
                self.botDatabase.executeQuery(functions.generateBotLogQuery("DB", e))
            except:
                print("Ошибка записи в БД!")
                logging.critical("Ошибка при записи лога в БД!")
            finally:
                logging.error(f"{functions.getActualTime()}:e")
        self.getActualAdmins()

    def getInvitings(self, id = None):
        if (id == None):
            inviteList = self.botDatabase.getData("SELECT * FROM `AdminInvitings_BOT` WHERE `Activated` = 0;")
        else:
            inviteList = self.botDatabase.getData(f"SELECT * FROM `AdminInvitings_BOT` WHERE `ID` = {id};")[0]
        return inviteList

    def deleteAdminInvite(self, id, adminID):
        self.botDatabase.executeQuery(functions.generateActionLogQuery(adminID, "deleteAdminInvite", id))
        self.botDatabase.executeQuery(f"DELETE FROM AdminInvitings_BOT WHERE `AdminInvitings_BOT`.`ID` = {id}")

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
            self.createPageToWeb(self.usersActions[adminID][1], alias, self.getCategoryFromID(self.usersActions[adminID][2]), self.usersActions[adminID][3], adminID)
            self.cancelAction(adminID)
        elif (status == 0): # Отмена. Удаление записи
            self.cancelAction(adminID)
    def blockCreate(self, adminID, status, data=""):
        status = int(status)
        if (status == 1): # Начало создания блока (Указание PageID)
            self.usersActions[adminID] = ["blockCreate", "", "", "", 2, data]
        elif (status == 2): # Ввод типа блока
            self.usersActions[adminID][1] = data
            self.usersActions[adminID][4] = 3
        elif (status == 3): # Ввод subdata
            self.usersActions[adminID][2] = data
            self.usersActions[adminID][4] = 4
        elif (status == 4): # Ввод data
            self.usersActions[adminID][3] = data
            self.usersActions[adminID][4] = 5
        elif (status == 5): # Подтверждение
            pageTable = self.getPageData(self.usersActions[adminID][5])[0][4]
            self.botDatabase.executeQuery(functions.generateActionLogQuery(adminID, "createBlock", f"PageTable: {pageTable}, blockType: {self.usersActions[adminID][1]}, subdata: {self.usersActions[adminID][2]}, data: {self.usersActions[adminID][3]}"))
            self.webDatabase.executeQuery(f"INSERT INTO `{pageTable}_Page` (`ID`, `type`, `subdata`, `data`) VALUES (NULL, '{self.usersActions[adminID][1]}', '{self.usersActions[adminID][2]}', '{self.usersActions[adminID][3]}')")
            self.deletePageCache(self.usersActions[adminID][5], adminID)
        elif (status == 6): # Отмена
            self.cancelAction(adminID)
    def changeBlock(self, adminID, status, data=""):
        status = int(status)
        if (status == 1): # Начало редактирования блока (Указание pageID)
            self.usersActions[adminID] = ["blockEdit", "", "", "", 2, data] # 0 - Type, 1 - blockID, 2 - BlockContentType, 3 - Data, 4 - Status, 5 - PageID
        elif (status == 2): # Указание BlockID
            self.usersActions[adminID][1] = data
            self.usersActions[adminID][4] = 3
        elif (status == 3): # Указание BlockTypeID
            self.usersActions[adminID][2] = data
            self.usersActions[adminID][4] = 3
        elif (status == 4): # Указание data
            self.usersActions[adminID][3] = data
            self.usersActions[adminID][4] = 4
        elif (status == 5): # Подтверждение
            pageTable = self.getPageData(self.usersActions[adminID][5])[0][4]
            if (pageTable[-5] != "_"):
                pageTable += "_Page"
            blockType = "data"
            if (int(self.usersActions[adminID][2]) == 1):
                blockType = "subdata"
            query = f"UPDATE `{pageTable}` SET `{blockType}` = '{self.usersActions[adminID][3]}' WHERE `{pageTable}`.`ID` = {self.usersActions[adminID][1]};"
            self.botDatabase.executeQuery(functions.generateActionLogQuery(adminID, "editBlock", f"PageTable: {pageTable}, blockID: {self.usersActions[adminID][1]}, blockContentType: {self.usersActions[adminID][2]}, data: {self.usersActions[adminID][3]}"))
            self.webDatabase.executeQuery(query)
            self.deletePageCache(self.usersActions[adminID][5], adminID)
        elif (status == 6): # Отмена
            self.cancelAction(adminID)
    def getBlockTypeList(self):
        typeList = self.webDatabase.getData(f"SELECT * FROM `typeList`")
        return typeList
    def checkTypeInList(self, type):
        typeList = self.webDatabase.getData(f"SELECT * FROM `typeList`")
        for i in typeList:
            if (type == i[0]):
                return True
        return False
    def createCategory(self, adminID, status, data = ""):
        status = int(status)
        if (status == 1): # Начало создания категории
            self.usersActions[adminID] = ["categoryCreate", "", "", "", 2]
        elif (status == 2): # Ввод имени
            self.usersActions[adminID][1] = data
            self.usersActions[adminID][4] = 3
        elif (status == 3): # Подтверждение. Создание категории
            categoryName = self.usersActions[adminID][1]
            categoryUrl = functions.translitText(categoryName)
            categoryUrl = categoryUrl.replace(" ", "-")
            functions.createDirectory(self.webPath + categoryUrl)
            self.createCategoryInDB(categoryName, categoryUrl, adminID)
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
            self.botDatabase.executeQuery(functions.generateActionLogQuery(userID, "createAdminInvite", inviteCode))
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
            self.botDatabase.executeQuery(functions.generateActionLogQuery(userID, "changeAdminName", f"AdminID: {self.usersActions[userID][1]}, New name: {self.usersActions[userID][2]}"))
            self.botDatabase.executeQuery(f"UPDATE `Admins_BOT` SET `Name` = '{self.usersActions[userID][2]}' WHERE `Admins_BOT`.`ID` = {self.usersActions[userID][1]};")
            self.cancelAction(userID)
        elif (status == 0): # Отмена. Удаление записи
            self.cancelAction(userID)
    def isUserActive(self, id):
        if (id in self.usersActions):
            return True
        return False
    def isUserAuth(self, id):
        if (id in self.usersAuth):
            return True
        return False
    def createPageToWeb(self, pageName, pageAlias, pageCategory, pageHide, adminID):
        addPageToListQuery = f"INSERT INTO `pageList` (`ID`, `name`, `alias`, `category`, `tableName`, `cacheName`, `isHide`) VALUES (NULL, '{pageName}', '{pageAlias}', '{pageCategory}', '{pageAlias}', NULL, '{pageHide}')"
        createPageTableQuery = f"CREATE TABLE `debaltsevo-web`.`{pageAlias}_Page` (`ID` INT NOT NULL AUTO_INCREMENT , `type` VARCHAR(32) NOT NULL , `subdata` VARCHAR(128) NOT NULL , `data` TEXT NOT NULL , PRIMARY KEY (`ID`)) ENGINE = InnoDB;"
        createPageConnectionQuery = f"ALTER TABLE `{pageAlias}_Page` ADD FOREIGN KEY (`type`) REFERENCES `typeList`(`Name`) ON DELETE RESTRICT ON UPDATE RESTRICT;"
        self.botDatabase.executeQuery(functions.generateActionLogQuery(adminID, "createPage", f"PageName: {pageName}, Category: {pageCategory}"))
        self.webDatabase.executeQuery(addPageToListQuery)
        self.webDatabase.executeQuery(createPageTableQuery)
        self.webDatabase.executeQuery(createPageConnectionQuery)
        systemCachePath = self.webPath + self.cachePath + "system/"
        functions.deleteFile(systemCachePath + "footer.html")
        functions.deleteFile(systemCachePath + "header.html")
    def getPageData(self, pageID):
        pageData = self.webDatabase.getData(f"SELECT * FROM `pageList` WHERE `ID` = \"{pageID}\";")
        if (pageData == []):
            return None
        else:
            pageData = pageData[0]
            pageTable = pageData[4]
            pageContent = self.webDatabase.getData(f"SELECT * FROM `{pageTable}_Page`")
            return pageData, pageContent
    def getBlockData(self, pageTable, blockID):
        if (pageTable[-5] != "_"):
            pageTable += "_Page"
        blockData = self.webDatabase.getData(f"SELECT * FROM `{pageTable}` WHERE `ID` = \"{blockID}\";")
        if (blockData == []):
            return None
        return blockData[0]
    def deleteBlock(self, pageID, blockID, adminID):
        pageData, pageContent = self.getPageData(pageID)
        self.webDatabase.executeQuery(functions.generateActionLogQuery(adminID, "deleteBlock"))
        self.webDatabase.executeQuery(f"DELETE FROM `{pageData[4]}_Page` WHERE `{pageData[4]}_Page`.`ID` = {blockID}")
    def createCategoryInDB(self, categoryName, categoryUrl, adminID):
        highNumber = int(self.getCategoryLastNumber()) + 1
        self.botDatabase.executeQuery(functions.generateActionLogQuery(adminID, "CreateCategory", categoryName))
        self.webDatabase.executeQuery(f"INSERT INTO `categoryList` (`number`, `name`, `url`) VALUES ('{highNumber}', '{categoryName}', '{categoryUrl}')")
        systemCachePath = self.webPath + self.cachePath + "system/"
        functions.deleteFile(systemCachePath + "footer.html")
        functions.deleteFile(systemCachePath + "header.html")
        self.updateCategoryList()
    def deleteCategoryFromDB(self, categoryName, adminID):
        categoryFolder = self.webDatabase.getData(f"SELECT * FROM `categoryList` WHERE `name` = \"{categoryName}\";")[0][2]
        categoryPath = self.webPath + categoryFolder
        functions.deleteDirectory(categoryPath)
        pageCategoryList = self.getCategoryPageList(categoryName)
        self.botDatabase.executeQuery(functions.generateActionLogQuery(adminID, "deleteCategory", categoryName))
        for i in pageCategoryList:
            pageTable = i[4]
            print(f"Удаляемая таблица: {pageTable}")
            if (len(pageTable) < 5):
                pageTable += "_Page"
            elif (pageTable[-5] != "_"):
                pageTable += "_Page"
            self.webDatabase.executeQuery(f"DROP TABLE `{pageTable}`")
        self.webDatabase.executeQuery(f"DELETE FROM pageList WHERE `pageList`.`category` = \"{categoryName}\";")
        self.webDatabase.executeQuery(f"DELETE FROM `categoryList` WHERE `categoryList`.`name` = '{categoryName}'")
        systemCachePath = self.webPath + self.cachePath + "system/"
        functions.deleteFile(systemCachePath + "footer.html")
        functions.deleteFile(systemCachePath + "header.html")
        self.updateCategoryList()
    def deletePage(self, pageID, adminID):
        pageData = self.webDatabase.getData(f"SELECT * FROM `pageList` WHERE `ID` = \"{pageID}\";")[0]
        pageTable = pageData[4]
        self.botDatabase.executeQuery(functions.generateActionLogQuery(adminID, "deletePage", pageID))
        self.webDatabase.executeQuery(f"DELETE FROM `pageList` WHERE `pageList`.`ID` = {pageID}")
        self.webDatabase.executeQuery(f"DROP TABLE `{pageTable}_Page`")
    def getCategoryPageList(self, categoryName):
        pageCategoryList = self.webDatabase.getData(f"SELECT * FROM `pageList` WHERE `category` = \"{categoryName}\";")
        return pageCategoryList
    def getCategoryLastNumber(self):
        highNumber = 0
        for i in self.categoryList:
            if (i[0] > highNumber):
                highNumber = i[0]
        return highNumber
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
    def getCategoryMenuButtons(self):
        return self.categoryMenuButtons
    def getMessages(self):
        return self.Messages
    def getIDWithOffset(self, call, startPlace):
        return functions.getIDWithOffset(call, startPlace)
    def updateCategoryList(self):
        self.categoryList = self.webDatabase.getData("SELECT * FROM `categoryList`")
    def getUsersActions(self, id = None):
        if (id == None):
            return self.usersActions
        if (id not in self.usersActions):
            return None
        return self.usersActions[id]
    def getCategoryList(self):
        return self.categoryList
    def generateString(self, leng = 20):
        out = functions.generateAdminInviteCode(leng)
        return out
    def getWebPath(self):
        return self.webPath
    def getAdminList(self, adminID = None):
        adminList = self.botDatabase.getData("SELECT * FROM `Admins_BOT`")
        if (adminID == None):
            return adminList
        for i in adminList:
            if (str(i[0]) == adminID):
                return i
        return None
    def deleteAdmin(self, adminID, creatorID):
        adminTID = self.getAdminList(adminID)[1]
        self.botDatabase.executeQuery(functions.generateActionLogQuery(creatorID, "DeleteAdmin", "adminID"))
        self.botDatabase.executeQuery(f"DELETE FROM AdminInvitings_BOT WHERE `AdminInvitings_BOT`.`ActivatedBy` = {adminTID}")
        self.botDatabase.executeQuery(f"DELETE FROM Admins_BOT WHERE `Admins_BOT`.`ID` = {adminID}")
    def getCategoryFromID(self, categoryID):
        categoryID = int(categoryID)
        for i in self.categoryList:
            if (i[0] == categoryID):
                return i[1]
        return None
    def getStrFromBool(self, temp):
        if (temp == None):
            temp = 0
        if (temp == 0 or temp == "0"):
            return "🟥 Нет"
        else:
            return "🟢 Да"
    def getLog(self, type):
        data = None
        if (type == "bot"):
            data = self.botDatabase.getData("SELECT * FROM `log_BOT`")
        elif (type == "action"):
            data = self.botDatabase.getData("SELECT * FROM `logAction_BOY`")
        elif (type == "site"): # In dev.
            pass
        elif (type == "incident"):
            data = self.webDatabase.getData("SELECT * FROM `immunityIncidents`")
        return data
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
    def deletePageCache(self, pageID, adminID):
        pageData = self.webDatabase.getData(f"SELECT * FROM `pageList` WHERE `ID` = \"{pageID}\";")[0]
        pageCacheName = pageData[5]
        if (pageCacheName != None):
            systemCachePath = self.webPath + self.cachePath + "pages/" + pageCacheName
            functions.deleteFile(systemCachePath)
            self.botDatabase.executeQuery(functions.generateActionLogQuery(adminID, "deletePageCache", pageID))
            self.webDatabase.executeQuery(f"UPDATE `pageList` SET `cacheName` = NULL WHERE `pageList`.`ID` = \"{pageID}\";")
    def deleteAllCache(self, adminID):
        self.botDatabase.executeQuery(functions.generateActionLogQuery(adminID, "deleteAllCache"))
        functions.deleteDirectoryContent(self.webPath + self.cachePath + "system/")
        functions.deleteDirectoryContent(self.webPath + self.cachePath + "pages/")
        self.webDatabase.executeQuery("UPDATE `pageList` SET `cacheName` = NULL WHERE `pageList`.`cacheName` IS NOT NULL;")
    def isAdmin(self, id):
        if (str(id) in self.actualAdmins):
            return True
        else:
            return False
    def isPageHide(self, pageID):
        pageData = self.webDatabase.getData(f"SELECT * FROM `pageList` WHERE `ID` = \"{pageID}\";")[0]
        isPageHide = pageData[6]
        if (isPageHide == "0" or isPageHide == 0):
            return True
        return False
    def hidePage(self, pageID, action):
        query = f"UPDATE `pageList` SET `isHide` = '{action}' WHERE `pageList`.`ID` = \"{pageID}\";"
        self.webDatabase.executeQuery(query)
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
        elif (type == "category"):
            for i in self.categoryMenuButtons:
                if (self.categoryMenuButtons[i] == data):
                    return True
            return False