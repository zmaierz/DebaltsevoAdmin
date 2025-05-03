import configparser
import engine.DB.DB as database
import engine.modules.messages_text as messages

class Kernel:
    def __init__(self):
        self.MainMenuButtons = messages.getMainMenuButtons()
        self.Messages = messages.getMessages()

        self.kernelConfig = configparser.ConfigParser()
        self.DBConfig = configparser.ConfigParser()

        self.kernelConfig.read('engine/config/kernel.conf')
        self.DBConfig.read('engine/config/db.conf')

        self.botToken = self.kernelConfig.get("BOT", "token")
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
        self.adminList = self.botDatabase.getData("SELECT * FROM `Admins_BOT`")
        self.actualAdmins = []
        for admin in self.adminList:
            self.actualAdmins.append(admin[1])

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
    def isDebug(self):
        return self.debug
    def isAdmin(self, id):
        if (str(id) in self.actualAdmins):
            return True
        else:
            return False