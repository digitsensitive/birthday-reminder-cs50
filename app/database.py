import mysql.connector
from mysql.connector import errorcode


class MySQL:
    def __init__(self, app):
        self.app = app
        self.init()

    def init(self):
        cnx = mysql.connector.connect(
            host="mysqldb",
            user="root",
            password="p@ssw0rd1"
        )

        cursor = cnx.cursor()

        cursor.execute("CREATE DATABASE IF NOT EXISTS users")
        cursor.close()

        cnx = mysql.connector.connect(
            host="mysqldb",
            user="root",
            password="p@ssw0rd1",
            database="users"
        )

        cursor = cnx.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS `users` ("
            "`id` INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL, "
            "`username` TEXT NOT NULL, "
            "`hash` TEXT NOT NULL"
            ")")
        cursor.close()

    def connection(self, db):
        config = {
            'host': 'mysqldb',
            'user': 'root',
            'password': 'p@ssw0rd1',
            'database': db
        }

        try:
            cnx = mysql.connector.connect(**config)
            return cnx
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your username or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
