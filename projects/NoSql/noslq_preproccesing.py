import json
from pathlib import Path
import re
import emoji
from nltk.corpus import stopwords
from nltk import WordNetLemmatizer, word_tokenize, pos_tag

from nosqldbhandler import Tweet, NoSqlDbHandler


class Preprocessor_NoSql:
    __PROCESSING_PATH = Path('.') / 'data' / 'processing'
    __SLANG_WORDS_PATH = __PROCESSING_PATH / 'slang_words.json'
    __PUNCTUATION_PATH = __PROCESSING_PATH / 'punctuation.txt'

    def __init__(self):
        self.__slang_words = self.__read_slang_words(self.__SLANG_WORDS_PATH)
        self.__punctuation = self.__read_punctuation(self.__PUNCTUATION_PATH)
        self.__stopwords = set(stopwords.words('english'))

    """
    Class of method for parsing utility files
    """

    @staticmethod
    def __read_slang_words(file_path: Path) -> dict:
        """
        Legge il file JSON delle slang words e lo ritorna.
        :param file_path: il path del file delle slang words.
        :return: un dizionario contenente le slang words.
        """
        with open(file_path) as json_file:
            slang_words_map = json.load(json_file)

        return slang_words_map

    @staticmethod
    def __read_punctuation(file_path: Path) -> list:
        """
        Legge il file contenente la punctuation e ritorna il suo contenuto
        incapsulato in una lista.
        :param file_path: il path del file della punctuation.
        :return: una lista contenente i segni di punteggiatura.
        """
        punctuation_list = []

        with open(file_path, 'r') as f:
            for line in f.readlines():
                punctuation_list = line.split(" ")

        return punctuation_list

    """
    Preprocessing helper methods: each for one specific task. DIVIDE ET IMPERA
    """

    @staticmethod
    def __clean_message(msg: list) -> str:
        """
        Rimuove USERNAME, URL, e il carattere \n
        :param msg: lista di messaggi
        :type msg: list
        :return: messaggio ripulito da metadati superflui (privacy by design)
        :rtype: str
        """
        msg = msg.replace("\n", "")
        msg = msg.replace("URL", "")
        msg = msg.replace("USERNAME", "")

        return msg

    def __remove_hashtag(self, msg: str) -> str:
        """
        Rimuove gli hashtags dal messaggio e nel contempo li salva sul database
        :param msg: messaggio da analizzare
        :type msg: str
        :return: messaggio ripulito da hashtag
        :rtype: str
        """
        hashtags = re.findall(r"#(\w+)", msg)

        for hashtag in hashtags:
            msg = msg.replace('#' + hashtag, "")  # rimozione hashtags

        return msg

    def __subsistute_slang_words(self, msg: str) -> str:
        """
        Rimpiazza una slang word con il suo corrispettivo in inglese
        :param msg: messaggio da analizzare
        :type msg: str
        :return: messaggio senza slang words
        :rtype: str
        """
        for word in msg.split(' '):
            if word in self.__slang_words:
                msg = msg.replace(word, self.__slang_words.get(word))
        return msg

    def __clean_punctuation(self, msg: str) -> str:
        """
        Rimuove la punteggiatura, se presente, dalla stringa e le emoticons
        :param msg: messaggio da analizzare
        :type msg: str
        :return: messaggio senza slang words
        :rtype: str
        """
        for char in msg:
            if char in self.__punctuation:
                msg = msg.replace(char, '')
        return msg

    def __words_from_msg(self, msg: str) -> list:
        """
        Utilizzando la libreria per NLP andiamo a recuperare le singole parole dal tweet
        Previa lemmatizzazione, tokenizzazione, pos tagging e filtraggio dalle stop words
        :param msg: messaggio ripulito precedentemente
        :type msg: str
        :return: Lista di parole presenti le tweet
        :rtype: list
        """
        lemmatizer = WordNetLemmatizer()

        # tokenization
        tokenized_words = word_tokenize(msg)
        # pos tagging
        tagged_words = pos_tag(
            tokenized_words, tagset='universal')
        # lowering cases
        tagged_words = [(w[0].lower(), w[1])
                        for w in tagged_words]
        # lemmatizzazione
        lemmatized_tagged_words = [(lemmatizer.lemmatize(
            w[0]), w[1]) for w in tagged_words]
        # remove stopwords
        filtered_words = [w for w in lemmatized_tagged_words if not w[0]
                          in self.__stopwords]

        return filtered_words

    def preprocess(self, msg: str, sentiment: str) -> Tweet:
        """
        Dato un messaggio in ingresso, produce un corrispondente oggetto 
        Tweet, con relative words ripulite da caratteri inutili, 
        stop words, emoji/emoticons, punteggiatura, abbreviazioni e
        processate da nltk
        :param msg: line del file da processare
        :param sentiment: sentimento recuperato da db
        """
        new_tweet = Tweet(sentiment)

        # remove USERNAME, URL, \n from msg
        msg = self.__clean_message(msg)

        # remove hashtags
        msg = self.__remove_hashtag(msg)

        # remove emoji
        msg = emoji.replace_emoji(msg)

        # substitute slang words and acronyms from the msg
        msg = self.__subsistute_slang_words(msg)

        # remove punctuation and emoticons
        msg = self.__clean_punctuation(msg)

        # append on the obj
        new_tweet.add_words(self.__words_from_msg(msg))

        return new_tweet