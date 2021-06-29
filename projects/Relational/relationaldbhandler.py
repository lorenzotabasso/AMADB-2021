import sys

import mysql.connector
from pathlib import Path
from sys import stderr
import os


class RelationalDbHandler:
    # env variables
    DB_USER = 'root'
    DB_PASS = 'rootpass'
    DB_HOST = 'localhost'
    DB_NAME = 'tweet_analysis'

    # costanti per la gestione del db
    MAX_ALLOWED_PACKET = 32000000
    WORD_TYPE = 0

    # For handling error
    __ERR_NUM = 1

    # private variable of the class
    __db = None
    __cursor = None

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

    def create(self, sql_file_path: Path) -> None:
        """
        Crea il database e le sue tabelle secondo quanto definito in un file SQL.
        :param sql_file_path: path to .sql file
        :return: None
        """
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

    def load_lexical_resources(self, dataset_dir: Path) -> None:
        """
        Carica le risorse lessicali a partire dai file presenti in una cartella.
        :param dataset_dir: path to resource
        :return: None
        """
        self.__open_connection(self.DB_NAME)

        for dir_name in os.listdir(dataset_dir):
            sentiment_dir = dataset_dir / dir_name
            print("  {0}".format(dir_name))

            if not os.path.isdir(sentiment_dir):
                continue

            # Inserimento del sentimento.
            statement = 'INSERT INTO `sentiment`(`name`) VALUES(\"{}\")'.format(dir_name.lower())
            self.__cursor.execute(statement)

            for file_name in os.listdir(sentiment_dir):
                file_path = sentiment_dir / file_name
                print("    {0}".format(file_name))

                if not os.path.isfile(file_path):
                    continue

                # Inserimento della risorsa lessicale.
                # Il nome della risorsa è dato dal nome del file meno l'estensione.
                dataset_name = file_name.rsplit('.')[0]
                statement = 'INSERT INTO `lexical_resource`(`name`, `sentiment_id`) VALUES("{}", "{}")' \
                    .format(dataset_name, dir_name.lower())
                self.__cursor.execute(statement)

                # Gestiamo l'id dell'ultima risorsa lessicale inserita
                lexical_resource_id = self.__cursor.lastrowid

                # Inserimento di tutte le parole della risorsa.
                with open(file_path, 'r') as file:
                    for line in file.readlines():
                        # Rimozione spazi
                        text = line.strip()
                        # Scarto le parole composte.
                        if '_' in text:
                            continue

                        statement = 'SELECT `id` FROM `token` WHERE `text` = "{}" LIMIT 1;'.format(text)
                        self.__cursor.execute(statement)
                        result = self.__cursor.fetchall()

                        if len(result) > 0:
                            token_id = result[0][0]
                        else:
                            statement = 'INSERT INTO `token`(`type`, `text`) VALUES({}, "{}");' \
                                .format(self.WORD_TYPE, text)
                            self.__cursor.execute(statement)
                            # discorso analogo per il token id
                            token_id = self.__cursor.lastrowid

                        statement = 'INSERT INTO `in_resource`(`token_id`, `lexical_resource_id`) VALUES({}, {});' \
                            .format(token_id, lexical_resource_id)

                        # Gestione degli errori in caso di duplicati presenti nei dataset.
                        try:
                            self.__cursor.execute(statement)
                        except mysql.connector.errors.Error:
                            print('    Trovato duplicato nel file {}: {}'.format(file_name, text), file=sys.stderr)

        self.__db.commit()
        self.__close_connection()
