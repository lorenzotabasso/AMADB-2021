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
        Apre la connessione al database e istanza un oggetto MySQLCursor,
        eventualmente anche selezionando il database fornito in input.
        """
        try:
            if database_name is not None and type(database_name) == str:
                self.__db = mysql.connector.connect(
                    host=self.DB_HOST,
                    user=self.DB_USER,
                    password=self.DB_PASS,
                    database=database_name,
                    #charset="utf8mb4"
                )
            else:
                self.__db = mysql.connector.connect(
                    host=self.DB_HOST,
                    user=self.DB_USER,
                    password=self.DB_PASS,
                    #charset="utf8mb4"
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

    """
    Methods for loading resources in the DB
    """

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
        Legge il file JSON delle emojis/emoticons
        :param file_path: il path del file delle emoji words.
        :return: un dizionario contenente le emoji.
        """
        with open(file_path) as json_file:
            emoji_map = json.load(json_file)

        return emoji_map

    def load_emoticon_or_emoji(self, token_type: int, file_path: Path) -> None:
        """
        Carica le emoticon o le emoji a partire dal file in input con alcuni dettagli; 
        la distinzione tra emoticon ed emoji è data da token_type
        :param token_type: tipologia di token che lo identifica, vedi ddl schema e costanti della classe
        :type token_type: int
        :param file_path: percorso del file json
        :type file_path: Path
        """        """"""
        self.__open_connection(self.DB_NAME)

        statement = ''
        emo = self.__read_emo_json(file_path)

        for key in emo:
            if token_type == self.EMOJI_TYPE:
                # Caso delle emoji: Python interpreta quanto letto come sequenza di caratteri UTF-8. Ma quelli dati dalla professoressa
                # sono code-point unicode in formato ASCII escape.
                # Ecco quindi il file json: converto quindi la stringa in rappresentazione binaria trattandola come ASCII,
                # per poi riconvertirla in UTF-8
                # Ho così già caratteri delle emoji e non più la loro rappresentazione tramite ASCII escape.
                key = key.encode('ascii').decode('unicode_escape')
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
                # Debug print(f"Vado ad inserire il l'emmo {key}")
                statement = 'INSERT INTO `token`(`type`, `text`) VALUES({}, "{}");'.format(
                    token_type, key)
                self.__cursor.execute(statement)

        self.__db.commit()
        self.__close_connection()

    def load_tweets_batch(self, tweets: list) -> None:
        """
        Carica una lista di tweets facendo riferimento a uno specifico sentimento.
        :param tweets: lista di tuple (tweet_id, sentiment)
        :type tweets: list
        """
        statement = 'INSERT INTO `tweet`(`id`, `sentiment_id`) VALUES(%s, %s);'

        self.__open_connection(self.DB_NAME)

        self.__cursor.executemany(statement, tweets)
        self.__db.commit()

        self.__close_connection()

    def load_tokens_batch(self, tokens: list) -> None:
        """
        Carica un token facendo riferimento a un tipo specifico.
        :param tokens: lista di triplette (tkn_id, tkn_type, text)
        :type tokens: list
        """
        statement = 'INSERT INTO `token`(`id`, `type`, `text`) VALUES(%s, %s, %s);'

        self.__open_connection(self.DB_NAME)

        self.__cursor.executemany(statement, tokens)
        self.__db.commit()

        self.__close_connection()

    def load_contained_ins_batch(self, contained_ins: list) -> None:
        """
        Collega la relazione contained_in facendo riferimento a un tweet_id e ad un token_id.
        :param contained_ins: lista di quadruplets (dci_id, tweet_id, tkn_id, POS)
        :type contained_ins: list
        """
        statement = 'INSERT INTO `contained_in`(`id`, `tweet_id`, `token_id`, `part_of_speech`) VALUES(%s, %s, %s, %s);'

        self.__open_connection(self.DB_NAME)

        self.__cursor.executemany(statement, contained_ins)
        self.__db.commit()

        self.__close_connection()

    """
    Query methods for internal preprocessing use. Con ID massimo si intende il maggiore (ultimo)
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

    def get_tokens(self, token_type: int):
        """
        Restituisce la lista di tutte le coppie (token, id) nel DB specificando il tipo del token.

        :param token_type: [description]
        :type token_type: int
        :return: [description]
        :rtype: [type]
        """
        self.__open_connection(self.DB_NAME)
        statement = "SELECT `id`,`text`  FROM `token` WHERE `type` = {}".format(
            token_type)
        self.__cursor.execute(statement)

        tokens = self.__cursor.fetchall()
        self.__db.commit()
        self.__close_connection()

        return [(t[0], t[1]) for t in tokens]

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

    """ 
    Query semplici di lettura
    """

    def read_tokens(self, token_type: int):
        """
        Restituisce una mappa di token:token_id in base al tipo specificato dal parametro token_type
        :param token_type: identificativo della tipologia di token
        :type token_type: int
        :return: mappa token:token_id
        :rtype: dict
        """
        tokens_map = {}

        self.__open_connection(self.DB_NAME)
        statement = f'SELECT text, id FROM token WHERE type = {token_type}'
        self.__cursor.execute(statement)
        result = self.__cursor.fetchall()
        self.__db.commit()
        self.__close_connection()

        tokens_list = [(r[0], r[1]) for r in result]

        for (token_text, token_id) in tokens_list:
            tokens_map.update({token_text: token_id})
        return tokens_map

    def read_attributes(self) -> list:
        """
        :return: Restituisce la lista dei sentimenti presenti nel DB.
        :rtype: list
        """
        self.__open_connection(self.DB_NAME)
        statement = 'SELECT `name` FROM `sentiment`'
        self.__cursor.execute(statement)
        result = self.__cursor.fetchall()

        self.__db.commit()
        self.__close_connection()

        return [r[0] for r in result]

    def get_all_lexical_resources(self):
        # Ritorna ua lista di tutte le risorse lessicali
        statement = "SELECT lr.name AS lex_name \
                     FROM lexical_resource lr \
                     ORDER BY lr.name;"

        self.__open_connection(self.DB_NAME)
        self.__cursor.execute(statement)

        result = self.__cursor.fetchall()

        self.__db.commit()
        self.__close_connection()

        return [r[0] for r in result]

    def get_all_sentiments(self):
        # Ritorna ua lista di tutte i sentimenti
        statement = "SELECT s.name \
                     FROM sentiment s;"

        self.__open_connection(self.DB_NAME)
        self.__cursor.execute(statement)

        result = self.__cursor.fetchall()

        self.__db.commit()
        self.__close_connection()

        return [r[0] for r in result]

    def get_all_lex_resources_for_sentiment(self, sentiment):
        # Ritorna la lista di tuttel e risorse lessicali per un dato sentimento
        statement = "SELECT s.name AS s_name, lr.name AS lr_name \
                     FROM lexical_resource lr JOIN sentiment s ON lr.sentiment_id = s.name \
                     AND s.name = '{}' \
                     ORDER BY s.name;".format(sentiment)

        self.__open_connection(self.DB_NAME)
        self.__cursor.execute(statement)

        result = self.__cursor.fetchall()

        self.__db.commit()
        self.__close_connection()

        return [r[1] for r in result]


    def get_n_lex_words(self, lex_resource) -> int:
        """
        Restituisce il totale delle parole presenti nel DB per la risorsa lessicale in input.
        :param lex_resource: risorsa lessicale di cui si vuole il conteggio.
        :return: il conteggio delle parole presenti nella risorsa lessicale.
        """

        # Ritorna il numero di parole per la risorsa lessicale
        statement = "SELECT COUNT(t.id) \
                     FROM token t JOIN in_resource ir ON t.id = ir.token_id  \
                     JOIN lexical_resource lr ON ir.lexical_resource_id = lr.id \
                     WHERE lr.name = '{}' \
                     GROUP BY lr.name;".format(lex_resource)

        self.__open_connection(self.DB_NAME)
        self.__cursor.execute(statement)

        result = self.__cursor.fetchall()

        self.__db.commit()
        self.__close_connection()

        # La struttura è del formato [(354,)], per questo il [0][0] finale
        return result[0][0]

    def get_n_twitter_words(self, sentiment) -> int:
        """
        Restituisce il totale dei tweets etichettati con lo stesso sentimento dato in input.
        :param sentiment: il sentimento di cui si vuole il conteggio.
        :return: il conteggio dei tweet presenti nel sentimento.
        """

        statement = "SELECT COUNT(t.id) \
                    FROM token t JOIN contained_in ci ON t.id = ci.token_id \
                    JOIN tweet tw ON ci.tweet_id = tw.id \
                    JOIN sentiment s ON tw.sentiment_id = s.name \
                    AND s.name = '{}' \
                    GROUP BY s.name;".format(sentiment)

        self.__open_connection(self.DB_NAME)
        self.__cursor.execute(statement)

        result = self.__cursor.fetchall()

        self.__db.commit()
        self.__close_connection()

        # La struttura è del formato [(354,)], per questo il [0][0] finale
        return result[0][0]

    def get_shared_words(self, lex_resource, sentiment) -> int:
        """
        Ritorna il numero di parole in comune tra la risorsa lessicale e il sentimento.
        :param lex_resource: risorsa lessicale in input
        :param sentiment:  sentimento in input
        :return: conteggio delle parole in comune tra la risorsa lessicale e l'input.
        """

        #statement = "SELECT COUNT(t.id) \
        #            FROM token t JOIN in_resource ir ON t.id = ir.token_id  \
        #            JOIN lexical_resource lr ON ir.lexical_resource_id = lr.id \
        #            JOIN contained_in ci ON t.id = ci.token_id  \
        #            JOIN tweet tw ON ci.id = tw.id \
        #            JOIN sentiment s ON tw.sentiment_id = s.name \
        #            WHERE lr.name = '{}' AND s.name = '{}';".format(lex_resource, sentiment)

        statement = "SELECT COUNT(t.id) \
                    FROM token t JOIN in_resource ir ON t.id = ir.token_id \
                    JOIN lexical_resource lr ON ir.lexical_resource_id = lr.id \
                    AND lr.name = '{}' \
                    WHERE t.id IN \
                    (SELECT t.id \
                    FROM token t JOIN contained_in ci ON t.id = ci.token_id \
                    JOIN tweet tw ON ci.id = tw.id \
                    JOIN sentiment s ON tw.sentiment_id = s.name \
                    AND s.name = '{}');".format(lex_resource, sentiment)

        self.__open_connection(self.DB_NAME)
        self.__cursor.execute(statement)

        result = self.__cursor.fetchall()

        self.__db.commit()
        self.__close_connection()

        # La struttura è del formato [(354,)], per questo il [0][0] finale
        return result[0][0]

    """ 
    Query complesse per l'output
    """

    def token_most_present(self, token_type: int, sentiment: str, limit: int):
        """[summary]
        Restituisce i token più presenti nei tweet relativi al sentimento `sentiment` con rispettive occorrenze.
        Si deve specificare il tipo del token e il numero delle parole massime che devono essere restituite
        :param token_type: tipologia di token da recuperare (WORD_TYPE = 0, EMOJI_TYPE = 1, EMOTICON_TYPE = 2, HASHTAG_TYPE = 3)
        :param sentiment: sentimento da interrogare
        :param limit: upper bound
        """
        statement = "SELECT token.text, count(contained_in.id) \
            FROM tweet join contained_in on tweet.id = contained_in.tweet_id \
                join token on token.id = contained_in.token_id \
            WHERE token.type = {} AND tweet.sentiment_id = '{}' \
            GROUP BY tweet.sentiment_id, token.text, contained_in.part_of_speech \
            ORDER BY count(contained_in.id) DESC \
            LIMIT {};".format(token_type, sentiment, limit)

        self.__open_connection(self.DB_NAME)
        self.__cursor.execute(statement)
        result = self.__cursor.fetchall()

        self.__db.commit()
        self.__close_connection()

        #return [(r[0], r[1]) for r in result]
        return {r[0]: r[1] for r in result}
