from pymongo import MongoClient
from pathlib import Path
import os

class Sentiment:
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


class NoSqlDbHandler:
    __CLIENT_URL = 'mongodb://127.0.0.1:27017/'
    __DB_NAME = 'tweet_analytics'
    __COLLECTION_TWEETS = 'tweets'
    __COLLECTION_LEXICAL_RESOURCES = 'lexical_resources'
    __COLLECTION_COMMON_WORDS = 'common_words'
    __COLLECTION_SENTIMENTS = 'sentiments'

    def __init__(self):
        """
        Initialize the class: key element are 
        + MongoClient obj 
        + Database name
        """
        self.__client = MongoClient(self.__CLIENT_URL)
        self.__db = self.__client[self.__DB_NAME]


    def load_lexical_resources(self, dataset_dir: Path) -> None:
        sentiments = []
        collection = self.__db[self.__COLLECTION_LEXICAL_RESOURCES]
        collection.drop()

        for dir_name in os.listdir(dataset_dir):
            sentiment_dir = dataset_dir / dir_name
            sentiments.append(Sentiment(dir_name.lower()))


        collection = self.__db[self.__COLLECTION_SENTIMENTS]
        collection.drop()

        collection.insert_many(map(lambda x: x.to_dict(), sentiments))