from typing import List
from pymongo import MongoClient
from pathlib import Path
import os


class WordList:
    """
    Because Python has multiple inheritance possiamo definire una classe meta
    da utilizzare successivamente.
    """

    def __init__(self,  words=None) -> None:
        if words is None:
            self.__words = []
        else:
            self.__words = words

    def add_word(self, new_word: str) -> None:
        """
        Aggiunge una sola parola alla lista
        :param new_word: parola
        :type new_word: str
        """
        self.__words.append(new_word)

    def add_words(self, new_words: set) -> None:
        """
        Estende la lista di parole con un'ulteriore lista
        :param: new_word: parola
        :type: new_word: str
        """
        words = list(new_words)
        self.__words.extend(words)


class Sentiment:
    """
    Classe che rappresenta il singolo sentimento
    Caraterizzata dal nome_s e da proprio identificatore univoco
    """

    def __init__(self, name: str, id=None) -> None:
        self.__name = name
        self.__id = id

    def to_dict(self) -> dict:
        representation = {
            'name': self.__name
        }
        if self.__id is not None:
            representation.update({'_id': self.__id})

        return representation


class Lexical_resource(WordList):
    """
    Classe che rappresenta la risorsa lessicale
    Caraterizzata dal nome, dal sentimento a cui si riferisce,
    da una lista di parole associate e
    da un proprio identificatore univoco
    """

    def __init__(self, name: str, sentiment: str, words=None, id=None) -> None:
        self.__name = name
        self.__sentiment = sentiment
        if words is None:
            self._WordList__words = []
        else:
            self._WordList__words = words
        self.__id = id

    def to_dict(self) -> dict:
        representation = {
            'name': self.__name,
            'sentiment': self.__sentiment,
            'words': self._WordList__words
        }
        if self.__id is not None:
            representation.update({'_id': self.__id})

        return representation


class Tweet(WordList):
    """
    Classe che rappresenta il singolo tweet, simile a :class:`Lexical_resource`.
    Caraterizzata dal sentimento a cui si riferisce,
    da una lista di parole contenute nel tweet
    da un proprio identificatore univoco
    """

    def __init__(self, sentiment: str, words=None, id=None) -> None:
        self.__id = id
        self.__sentiment = sentiment
        if words is None:
            self._WordList__words = []
        else:
            self._WordList__words = words
        self.__id = id

    def to_dict(self) -> dict:
        representation = {
            'sentiment': self.__sentiment,
            'words': self._WordList__words
        }
        if self.__id is not None:
            representation.update({'_id': self.__id})

        return representation


class Common_words(WordList):
    """
    Classe che rappresenta un join tra i tweets e le risorse lessicali
    Il focus è sulle parole in comune tra i due dato un sentimento e la risorsa lessicale.
    Presenza del proprio identificatore univoco
    """

    def __init__(self, lexical_resource: str, sentiment: str, words=None, id=None) -> None:
        self.__sentiment = sentiment
        self.__lexical_resource = lexical_resource
        if words is None:
            self._WordList__words = []
        else:
            self._WordList__words = words
        self.__id = id

    def to_dict(self) -> dict:
        representation = {
            'sentiment': self.__sentiment,
            'lexical_resource': self.__lexical_resource,
            'words': self._WordList__words
        }
        if self.__id is not None:
            representation.update({'_id': self.__id})

        return representation


class NoSqlDbHandler:
    __CLIENT_URL = 'mongodb://127.0.0.1:27017/'
    __DB_NAME = 'tweet_analytics'
    __COLLECTION_LEXICAL_RESOURCES = 'lexical_resources'
    __COLLECTION_SENTIMENTS = 'sentiments'
    __COLLECTION_TWEETS = 'tweets'
    __COLLECTION_COMMON_WORDS = 'common_words'

    def __init__(self):
        """
        Initialize the class: key element are 
        + MongoClient obj 
        + Database name
        """
        self.__client = MongoClient(self.__CLIENT_URL)
        self.__db = self.__client[self.__DB_NAME]

    def load_lexical_resources(self, dataset_dir: Path) -> None:
        """
        Inserimento in mongo dei sentimenti, delle risorse lessicali e relative parole associate
        tramite l'uso di collezioni.
        Se già presenti nel database vengono eliminate e rimpiazzate
        :param dataset_dir: percorso da cui recuperare i documenti
        :type dataset_dir: Path
        """
        sentiments = []
        collection = self.__db[self.__COLLECTION_LEXICAL_RESOURCES]
        collection.drop()

        for dir_name in os.listdir(dataset_dir):
            # Inserimento del sentimento
            sentiments.append(Sentiment(dir_name.lower()))

            sentiment_dir = dataset_dir / dir_name
            if not os.path.isdir(sentiment_dir):
                continue

            for file_name in os.listdir(sentiment_dir):
                file_path = sentiment_dir / file_name

                if not os.path.isfile(file_path):
                    continue

                # Inserimento della risorsa lessicale.
                # Il nome della risorsa è dato dal nome del file meno l'estensione.
                dataset_name = file_name.rsplit('.')[0]

                new_res = Lexical_resource(dataset_name, str(dir_name).lower())

                # Inserimento di tutte le parole della risorsa.
                words = set()
                with open(file_path, 'r') as file:
                    for line in file.readlines():
                        text = line.strip()

                        # Scarto le parole composte.
                        if '_' not in text:
                            words.add(text)

                new_res.add_words(words)
                # Scrittura su db
                collection.insert_one(new_res.to_dict())

        collection = self.__db[self.__COLLECTION_SENTIMENTS]
        collection.drop()
        # Scrittura su db
        collection.insert_many(map(lambda x: x.to_dict(), sentiments))

    def load_tweets(self, tweets: list) -> None:
        """
        Inserimento in mongo dei tweets, già pre processati
        :param tweets: lista di tweet ripulità
        :type tweets: list
        """
        collection = self.__db[self.__COLLECTION_TWEETS]

        collection.insert_many(map(lambda x: x.to_dict(), tweets))

    def load_common_words(self, common_words: list) -> None:
        """
        Inserimento delle paroli comuni tra tweets e risorse lessicali
        :param common_words: lista di common words
        :type common_words: list
        """
        collection = self.__db[self.__COLLECTION_COMMON_WORDS]

        collection.insert_many(map(lambda x: x.to_dict(), common_words))

    def drop_tweets(self) -> None:
        """
        Droppa dal db la collezione relativa ai tweets
        """
        collection = self.__db[self.__COLLECTION_TWEETS]
        collection.drop()

    def drop_common_words(self) -> None:
        """
        Droppa dal db la collezione relativa alle common_words
        """
        collection = self.__db[self.__COLLECTION_COMMON_WORDS]
        collection.drop()

    """ 
    Getter methods
    """

    def get_sentiments(self) -> list:
        """
        :return: Restituisce la lista dei sentimenti 
        :rtype: list
        """
        sentiments = []
        collection = self.__db[self.__COLLECTION_SENTIMENTS]

        for x in collection.find():
            sentiments.append(x['name'])

        return sentiments

    def get_lexical_resources(self) -> List[List]:
        """
        :return: Restituisce la lista di risorse lessicali
        ognuna composta da (nome:str, sentimento:str, parole:List[str])
        :rtype: List[List]
        """
        lexical_resources = []
        collection = self.__db[self.__COLLECTION_LEXICAL_RESOURCES]

        for x in collection.find():
            lexical_resources.append((x['name'], x['sentiment'], x['words']))

        return lexical_resources

    def get_tweets(self) -> list:
        """
        :return: Restituisce la lista dei tweets
        :rtype: list
        """
        tweets = []
        collection = self.__db[self.__COLLECTION_TWEETS]

        for x in collection.find():
            tweets.append((x['sentiment'], x['words']))
        
        return tweets
    
    def get_common_words(self) -> list:
        """
        :return: Restituisce la lista delle common_words
        :rtype: list
        """
        tweets = []
        collection = self.__db[self.__COLLECTION_COMMON_WORDS]

        for x in collection.find():
            tweets.append((x['lexical_resource'], x['sentiment'], x['words']))
        
        return tweets

