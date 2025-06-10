import mysql.connector
import logging

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
        try:
            cursor.execute(query)
            result = cursor.fetchall()
        except Exception as e:
            print(f"Возникло исключение SQL!\nОшибка: {e}")
        finally:
            cursor.close()
            connection.close()
        return result
    def executeQuery(self, query):
        connection = self.getConnection()
        cursor = connection.cursor()
        try:
            cursor.execute(query)
            connection.commit()
        except Exception as e:
            print(f"Возникло исключение SQL!\nОшибка: {e}")
        finally:
            cursor.close()
            connection.close()