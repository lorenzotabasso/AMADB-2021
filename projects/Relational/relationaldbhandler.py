import json
import sys
import emoji
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

    # Tipologia di token: token type nel db
    WORD_TYPE = 0
    EMOJI_TYPE = 1
    EMOTICON_TYPE = 2
    HASHTAG_TYPE = 3

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

        statement = 'SET GLOBAL max_allowed_packet={};'.format(
            self.MAX_ALLOWED_PACKET)
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

        self.__cursor.execute(
            'DROP DATABASE IF EXISTS `{}`;'.format(self.DB_NAME))
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
        :param dataset_dir: path to resource folder
        :return: None
        """
        self.__open_connection(self.DB_NAME)

        for dir_name in os.listdir(dataset_dir):
            sentiment_dir = dataset_dir / dir_name
            print("  {0}".format(dir_name))

            if not os.path.isdir(sentiment_dir):
                continue

            # Inserimento del sentimento.
            statement = 'INSERT INTO `sentiment`(`name`) VALUES(\"{}\")'.format(
                dir_name.lower())
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

                # Inserimento di tutte le parole relative alla risorsa appena inserita
                with open(file_path, 'r') as file:
                    for line in file.readlines():
                        # Rimozione spazi
                        text = line.strip()
                        # Scarto le parole composte.
                        if '_' in text:
                            continue

                        # query sul db per recuperare, se presente il token
                        statement = 'SELECT `id` FROM `token` WHERE `text` = "{}" LIMIT 1;'.format(
                            text)
                        self.__cursor.execute(statement)
                        result = self.__cursor.fetchall()

                        if len(result) > 0:
                            token_id = result[0][0]
                        else:
                            # se non è presente vado ad inserirlo
                            statement = 'INSERT INTO `token`(`type`, `text`) VALUES({}, "{}");' \
                                .format(self.WORD_TYPE, text)
                            self.__cursor.execute(statement)
                            # discorso analogo per il token id
                            token_id = self.__cursor.lastrowid

                        # collegamento tra token e risorsa lessicale
                        statement = 'INSERT INTO `in_resource`(`token_id`, `lexical_resource_id`) VALUES({}, {});' \
                            .format(token_id, lexical_resource_id)

                        # Gestione degli errori in caso di duplicati presenti nei dataset.
                        try:
                            self.__cursor.execute(statement)
                        except mysql.connector.errors.Error:
                            print('    Trovato duplicato nel file {}: {}'.format(
                                file_name, text), file=sys.stderr)

        self.__db.commit()
        self.__close_connection()

    def __read_emo_json(self, file_path: Path) -> dict:
        """
        Legge il file JSON delle emojis/emoticons e lo ritorna.
        :param file_path: il path del file delle emoji words.
        :return: un dizionario contenente le emoji.
        """
        with open(file_path) as json_file:
            emoji_map = json.load(json_file)

        return emoji_map

    def load_emoticon_or_emoij(self, token_type: int, file_path: Path) -> None:
        """
        Carica le emoticon o le emoji a partire dal file in input con alcuni dettagli; 
        la distinzione tra emoticon ed emoji è data da token_type
        :param token_type: tipologia di token che lo identifica, vedi ddl schema e costanti della classe
        :type token_type: int
        :param file_path: percorso del file json
        :type file_path: Path
        """        """"""
        self.__open_connection(self.DB_NAME)

        emo = self.__read_emo_json(file_path)

        for key in emo:
            if token_type == self.EMOJI_TYPE:
                # Caso delle emoji: Python interpreta quanto letto come sequenza di caratteri UTF-8. Ma quelli dati dalla professoressa
                # sono code-point unicode in formato ASCII escape.
                # Ecco quindi il file json: converto quindi la stringa in rappresentazione binaria trattandola come ASCII,
                # per poi riconvertirla in UTF-8
                # Ho così già caratteri delle emoji e non più la loro rappresentazione tramite ASCII escape.
                pass
            else:
                # Caso delle emoticon: devo sostituire il carattere '\' con '\\' per evitare che il DBMS lo tratti come carattere di escape.
                key = key.replace('\\', '\\\\')

            # Controllo che non sia presente nel db per evitare i DUPLICATI
            statement = 'SELECT `id` FROM `token` WHERE `type` = {} AND `text` = "{}" LIMIT 1;'.format(
                token_type, key)
            self.__cursor.execute(statement)
            result = self.__cursor.fetchall()

            if len(result) <= 0:
                # Debug print(f"Vado ad inserire il l'emo {key}")
                statement = 'INSERT INTO `token`(`type`, `text`) VALUES({}, "{}");'.format(
                    token_type, key)
                self.__cursor.execute(statement)

        self.__db.commit()
        self.__close_connection()

    """
    Query methods for internal use
    """

    def get_sentiments(self) -> list:
        """
        Restituisce la lista dei sentimenti presenti nel DB.
        :return: lista di sentimenti (8)
        :rtype: list
        """
        self.__open_connection(self.DB_NAME)
        statement = 'SELECT `name` FROM `sentiment`'
        self.__cursor.execute(statement)
        result = self.__cursor.fetchall()

        self.__db.commit()
        self.__close_connection()

        return [r[0] for r in result]

    def get_max_token_id(self) -> int:
        """
        :return: Restituisce l'id massimo tra tutti i tokens nel DB
        :rtype: int
        """
        self.__open_connection(self.DB_NAME)

        statement = 'SELECT max(`id`) FROM `token`'
        self.__cursor.execute(statement)
        result = self.__cursor.fetchall()

        self.__close_connection()

        if result[0][0] == None:
            return 0
        else:
            return result[0][0]

    def get_max_tweet_id(self) -> int:
        """
        :return: Restituisce l'id massimo tra tutti i tweets nel DB
        :rtype: int
        """
        self.__open_connection(self.DB_NAME)

        statement = 'SELECT max(`id`) FROM `tweet`'
        self.__cursor.execute(statement)
        result = self.__cursor.fetchall()

        self.__close_connection()

        if result[0][0] == None:
            return 0
        else:
            return result[0][0]

    def get_max_contained_in_id(self) -> int:
        """
        :return: Restituisce l'id massimo tra tutte le coppie token-tweet presenti nel DB
        :rtype: int
        """
        self.__open_connection(self.DB_NAME)

        statement = 'SELECT max(`id`) FROM `contained_in`'
        self.__cursor.execute(statement)
        result = self.__cursor.fetchall()

        self.__close_connection()

        if result[0][0] == None:
            return 0
        else:
            return result[0][0]

    # TODO Rimuovere questi metodi

    def load_twitter_messages(self, twitter_messages_dir) -> None:
        self.__open_connection(self.DB_NAME)

        exit = False  # just for debug

        for file_name in os.listdir(twitter_messages_dir):
            file_path = twitter_messages_dir / file_name
            print("  {0}".format(file_name))

            if not os.path.isfile(file_path):
                continue
            elif exit:  # just for debug
                break

            with open(file_path, 'r') as file:
                counter = 0  # just for debug
                emoji_dict = {}
                for line in file.readlines():
                    if counter <= 15:  # just for debug
                        # prep.preprocess_tweet(line, emoji_dict)
                        self.preprocess_tweet_aux(line, emoji_dict)
                        counter += 1
                    else:  # just for debug
                        exit = True
                        break

                print(emoji_dict)
        self.__close_connection()

    def preprocess_tweet_aux(self, tweet, emoji_dict):
        print(tweet)
        for word in tweet.split():
            if word == "USERNAME":
                print("\tFound USERNAME, skipping", file=sys.stderr)
                continue
            elif word[0] == '#':
                print("\tFound #, skipping", file=sys.stderr)
                continue
                # TODO: memorizzarlo nel DB
            else:
                # for emoji_category in self.__emojis:
                #     if word in emoji_category:
                #         # TODO: fare qualcosa
                #         print(emoji_category, word)
                #         continue

                if word in emoji.UNICODE_EMOJI['en']:
                    print("\tFound Emoji, skipping", file=sys.stderr)
                    if word in emoji_dict:
                        emoji_dict[word] += 1
                    else:
                        emoji_dict[word] += 1
                    continue
                    # TODO: memorizzarlo nel DB
