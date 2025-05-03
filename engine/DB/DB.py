import mysql.connector

class Database:
    def __init__(self, username, password, hostname, database, port = 3389):
        self.username = username
        self.password = password
        self.hostname = hostname
        self.database = database
        self.port = port
    def getConnection(self):
        try:
            with mysql.connector.connect(
                user=self.username,
                password=self.password,
                host=self.hostname,
                database=self.database
            ) as connection:
                return connection
        except mysql.connector.Error as e:
            print(e) # Change me! Logging error.