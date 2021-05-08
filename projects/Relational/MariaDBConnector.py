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

    def __init__(self):
        """
         Istanzia la classe.
        """
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

    '''
       Crea il database e le sue tabelle secondo quanto definito in un file SQL.
       '''

    def create(self, sql_file_path: Path) -> None:
        self.__open_connection()

        self.__cursor.execute('DROP DATABASE IF EXISTS `{}`;'.format(self.DB_NAME))
        self.__cursor.execute(
            'CREATE DATABASE `{}` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin */;'.format(self.DB_NAME))
        self.__db.database = self.DB_NAME

        with open(sql_file_path, 'r') as sql_file:
            statement = ''

            for line in sql_file.readlines():
                if line != '\n':
                    statement += line.rstrip('\n')
                else:
                    self.__cursor.execute(statement)
                    statement = ''

            # Esecuzione dell'ultimo statement prima della fine del file.
            self.__cursor.execute(statement)

        self.__db.commit()
        self.__close_connection()
