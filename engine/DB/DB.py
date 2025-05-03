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
            connection = mysql.connector.connect(
                user=self.username,
                password=self.password,
                host=self.hostname,
                database=self.database
            )
            return connection
        except mysql.connector.Error as e:
            print(e) # Change me! Logging error.
    def getData(self, query):
        connection = self.getConnection()
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result
    def executeQuery(self, query):
        connection = self.getConnection()
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        cursor.close()
        connection.close()