import mysql.connector
from mysql.connector.cursor import MySQLCursor
from pathlib import Path
from sys import stderr
import os


class MariaDBConnector:
    # env variables
    DB_USER = 'root'
    DB_PASS = 'rootpass'
    DB_HOST = 'localhost'
    DB_NAME = 'tweet_analysis'

    MAX_ALLOWED_PACKET = 32000000

    # For handling error
    __ERR_NUM = 1

    # private variable of the class
    __db = None
    __cursor = None

    def __init__(self, username, password):
        """
         Istanzia la classe.
        """
        # self.username = username
        # self.password = password
        super.__init__

    def __open_connection(self, database_name=None) -> None:
        """
        Apre la connessione al database e istanzia un oggetto MySQLCursor,
        eventualmente anche selezionando il database fornito in input.
        """
        try:
            if database_name is not None and type(database_name) == str:
                self.__db = mysql.connector.connect(
                    host=self.DB_HOST,
                    user=self.DB_USER,
                    password=self.DB_PASS,
                    database=database_name
                )
            else:
                self.__db = mysql.connector.connect(
                    host=self.DB_HOST,
                    user=self.DB_USER,
                    password=self.DB_PASS
                )
        except mysql.connector.Error as err:
            print(err, file=stderr)
            exit(self.__ERR_NUM)

        self.__cursor = self.__db.cursor()

        statement = 'SET GLOBAL max_allowed_packet={};'.format(self.MAX_ALLOWED_PACKET)
        self.__cursor.execute(statement)

    def __close_connection(self) -> None:
        """
        Chiude l'oggetto MySQLCursor e la connessione al database
        """
        if self.__cursor is not None:
            self.__cursor.close()

        if self.__db is not None:
            self.__db.close()

    # TODO: da continuare a sviluppare con il nuovo assett
    def add_data(self, first_name, last_name) -> None:
        try:
            statement = "INSERT INTO employees (first_name,last_name) VALUES (%s, %s)"
            data = (first_name, last_name)
            self.__cursor.execute(statement, data)
            self.__db.commit()
            print("Successfully added entry to database")
        except Exception as e:
            print(f"Error adding entry to database: {e}")
