import mysql.connector
from mysql.connector import errorcode


class MySQL:
    def __init__(self, app):
        self.app = app
        self.host = "mysqldb"
        self.port = 3306
        self.user = "root"
        self.password = "p@ssw0rd1"
        self.init()

    def get_connection(self, database=None):
        try:
            if database is None:
                return mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password
                )
            else:
                return mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=database
                )
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your username or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

    def init(self):
        # ---
        # Create Main Database
        cnx = self.get_connection()
        cursor = cnx.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS birthday_reminder")
        cursor.close()

        # ---
        # Create Tables in Main Database
        cnx = self.get_connection("birthday_reminder")
        cursor = cnx.cursor()

        # Create users table
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS `users` ("
            "`id` INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL, "
            "`username` TEXT NOT NULL, "
            "`hash` TEXT NOT NULL"
            ")")

        # Create birthdays table
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS `birthdays` ("
            "`id` INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL, "
            "`user_id` INTEGER NOT NULL, "
            "`name` TEXT NOT NULL, "
            "`birth_date` DATE NOT NULL, "
            "`gender` ENUM('m','f'), "
            "`display_on_main_page` BOOLEAN NOT NULL, "
            "`email_notification` BOOLEAN NOT NULL"
            ")")

        cursor.close()
