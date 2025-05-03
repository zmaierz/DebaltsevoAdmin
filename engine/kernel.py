import configparser

class Kernel:
    def __init__(self):
        self.kernelConfig = configparser.ConfigParser()
        self.kernelConfig.read('engine/config/kernel.conf')
        self.botToken = self.kernelConfig.get("BOT", "token")
    def getToken(self):
        return self.botToken