from relationaldbhandler import RelationalDbHandler
import json
import os
import re
import sys
from optparse import OptionParser
from pathlib import Path

import emoji
import nltk

nltk.download('pnkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('universal_tagset')


class Preprocessor:
    __PROCESSING_PATH = Path('.') / 'data' / 'processing'
    __SLANG_WORDS_PATH = __PROCESSING_PATH / 'slang_words.json'
    __PUNCTUATION_PATH = __PROCESSING_PATH / 'punctuation.txt'

    # Collection of dictonary for data
    __emojis = {}
    __sentiments = []
    __emoticons = {}
    __words = {}
    __hashtags = {}
    __data = {}

    # Counter variables for support, later initialized
    __max_token_id = -1
    __max_tweet_id = -1
    __max_contained_in_id = -1

    # Variables for data
    __DATA_TWEETS = 'tweets'
    __DATA_CONTAINED_INS = 'contained_ins'
    __DATA_TOKENS = 'tokens'

    # Datastructures for support files
    __slang_words = {}
    __punctuation = []
    __stopwords = None

    def __init__(self):
        self.__handler = RelationalDbHandler()

        # Read tokens from the db
        self.__emoticons = self.__handler.read_tokens(
            self.__handler.EMOTICON_TYPE)
        self.__emojis = self.__handler.read_tokens(self.__handler.EMOJI_TYPE)
        self.__words = self.__handler.read_tokens(self.__handler.WORD_TYPE)
        self.__hashtags = self.__handler.read_tokens(
            self.__handler.HASHTAG_TYPE)

        self.__data = {
            self.__DATA_TWEETS: [],
            self.__DATA_CONTAINED_INS: [],
            self.__DATA_TOKENS: []
        }

        # retrive necessary information from the relational database
        self.__sentiments = self.__handler.get_sentiments()
        self.__max_token_id = self.__handler.get_max_token_id()
        self.__max_tweet_id = self.__handler.get_max_tweet_id()
        self.__max_contained_in_id = self.__handler.get_max_contained_in_id()

        self.__slang_words = self.__read_slang_words(self.__SLANG_WORDS_PATH)
        self.__punctuation = self.__read_punctuation(self.__PUNCTUATION_PATH)
        self.__stopwords = set(nltk.corpus.stopwords.words('english'))

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
        Legge il file contenente la puncuation e ritorna il suo contenuto
        incapsulato in una lista.
        :param file_path: il path del file della punctuation.
        :return: una lista contenente i segni di punteggiatura.
        """
        punctuation_list = []

        with open(file_path, 'r') as f:
            for line in f.readlines():
                punctuation_list = line.split(" ")

        return punctuation_list

    @staticmethod
    def load_data(self, raw_data) -> list:
        """
        Legge raw_data una linea per volta e la carica in una lista.
        :return: una lista contenente i dati in raw_data
        """
        emoSN = []

        with open(options.input, "r", encoding="utf-8") as dataset:
            for line in dataset:
                emoSN.append(line)

            print("finished!")
            return emoSN

    """
    Class of method for interacting with data in the datastructures
    """

    def get_sentiments(self) -> list:
        """
        :return: lista dei sentimenti recuperata dal database
        :rtype: list
        """
        return self.__sentiments

    def __add_data_tweet(self, sentiment: str) -> None:
        """
        :param sentiment: string reppresenting the sentiment 
        :type sentiment: str
        """
        self.__max_tweet_id += 1
        self.__data[self.__DATA_TWEETS].append(
            (self.__max_tweet_id, sentiment))

    def __add_data_token(self, type: int, text: str) -> None:
        """
        Aggiorno la mia mappa di token:token_id
        :param type: token_type
        :type type: int
        :param text: token da processare
        :type text: str
        """
        self.__max_token_id += 1
        self.__data[self.__DATA_TOKENS].append(
            (self.__max_token_id, type, text))

        # Aggiungo il token al dizionario/mappa appropriato sfruttando le costanti definite nel dbhandler
        if type == self.__handler.WORD_TYPE:
            self.__words[text] = self.__max_token_id
        elif type == self.__handler.EMOTICON_TYPE:
            self.__emoticons[text] = self.__max_token_id
        elif type == self.__handler.EMOJI_TYPE:
            self.__emojis[text] = self.__max_token_id
        elif type == self.__handler.HASHTAG_TYPE:
            self.__hashtags[text] = self.__max_token_id

    def __add_data_contained_in(self, tweet_id: int, token_id: int, pos=None) -> None:
        """[summary]

        :param tweet_id: [description]
        :type tweet_id: int
        :param token_id: [description]
        :type token_id: int
        :param pos: [description], defaults to None
        :type pos: [type], optional
        """        """"""
        self.__max_contained_in_id += 1
        self.__data[self.__DATA_CONTAINED_INS].append(
            (self.__max_contained_in_id, tweet_id, token_id, pos))

    """
    Preprocessing helper methods
    """

    def __clean_message(self, msg: list) -> str:
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

    def __process_hashtag(self, msg: str) -> str:
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

            hashtag_id = self.__hashtags.get('#' + hashtag)
            if hashtag_id is None:
                # Nuovo hashtag da inserire
                self.__add_data_token(
                    self.__handler.HASHTAG_TYPE, '#' + hashtag)
                hashtag_id = self.__max_token_id

            # Nuovo contained_in da inserire
            self.__add_data_contained_in(self.__max_tweet_id, hashtag_id)

        return msg

    def __process_emo(self, msg:str) -> str:
        """
        Verifico se word è una emoticon/emoij conosciuta
        Agisco di conseguenza con il caso emoij più complicato
        :param msg: messaggio da analizzare
        :type msg: str
        :return: messaggio ripulito da emoji ed emoticons
        :rtype: str
        """
        for word in msg.split(' '):
            is_emoji_or_emoticon = False

            # Verifico se word è una emoticon conosciuta; se sì,
            # la aggiungo alla relazione contained_in
            emo_id = self.__emoticons.get(word)

            if emo_id != None:
                is_emoji_or_emoticon = True
            else:
                emo_id = self.__emojis.get(word)

                if emo_id != None:
                    is_emoji_or_emoticon = True
                # Controllo se word è una emoji. Alcune emoji sono formate da più
                # emoji unite dal carattere ZWJ (zero width join) e alcune hanno
                # in coda un carattere di selezione per mostrarle come disegno
                # o rappresentazione grafica. Ad oggi, le combinazioni massime di
                # emoji sono di 7 caratteri. 169 e 129750 sono i limiti entro cui
                # sono contenute le emoji allo stato attuale di Unicode.
                elif len(word) > 0 and \
                    len(word) <= 7 and \
                    ord(word[0]) >= 169 and \
                    ord(word[0]) <= 129750:

                    self.__add_data_token(self.__handler.EMOJI_TYPE, word)
                    emo_id = self.__max_token_id
                    is_emoji_or_emoticon = True
            
            if is_emoji_or_emoticon:
                msg = msg.replace(word, "") # rimozione emoji
                self.__add_data_contained_in(self.__max_tweet_id, emo_id, None) # update dict

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
        Rimuove la punteggiatura, se presente, dalla stringa
        :param msg: messaggio da analizzare
        :type msg: str
        :return: messaggio senza slang words
        :rtype: str
        """
        for char in msg:
            if char in self.__punctuation:
                # print(char)
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
        lemmatizer = nltk.WordNetLemmatizer()

        # tokenization
        tokenized_words = nltk.word_tokenize(msg)
        # pos tagging
        tagged_words = nltk.pos_tag(
            tokenized_words, tagset='universal')
        # lowering cases
        tagged_words = [(w[0].lower(), w[1])
                        for w in tagged_words]
        # lemmatizzazion
        lemmatized_tagged_words = [(lemmatizer.lemmatize(
            w[0]), w[1]) for w in tagged_words]
        # remove stopwords
        filtered_words = [w for w in lemmatized_tagged_words if not w[0]
                          in self.__stopwords]

        return filtered_words

    @staticmethod
    def preprocess(self, raw_data):
        """
        It preprocess the raw_data removing all the '-' in the composite words.
        :param raw_data:
        :return:
        """
        preprocessed_data = []

        for line in raw_data:
            if "_" not in line:
                preprocessed_data.append(line)

        print("{0} ok!".format(len(preprocessed_data)))

    def get(self):
        # Semplici print di controllo. TODO: rimuoverlo.
        print("SLANG: {0}".format(self.__slang_words))
        print("PUNCTUATION: {0}".format(self.__punctuation))
        print("STOPWORDS: {0}".format(self.__stopwords))

    def preprocess(self, msg: str, sentiment: str) -> None:
        '''
        TODO:
        ✓ Rimuovere USERNAME e URL
        ✓ Eliminare Stop Words
        ✓ Gestire le emoij/Emoticons
        1. Lemmatizzare parole -> match con risorse lessicali
        2. Conteggiare presenza nei tweet delle parole associate a ogni sentimento
        3. Memorizzare le parole nuove
        '''
        self.__add_data_tweet(sentiment)

        # remove USERNAME, URL, \n from msg
        msg = self.__clean_message(msg)

        # remove hashtags and load them into db
        msg = self.__process_hashtag(msg)

        # remove emoticons and emojis and load them into db
        msg = self.__process_emo(msg)

        # substitute slang words and acronyms from the msg
        msg = self.__subsistute_slang_words(msg)

        print(msg)

        # remove puntuaction from the msg
        msg = self.__clean_punctuation(msg)

        # tokenization, pos tagging, lemmatization, lower case and stop words elimination
        filtered_words = self.__words_from_msg(msg)

        print(filtered_words)

        # TODO Insert words in Database


if __name__ == "__main__":
    sentiment_path = Path('.') / 'data' / 'lexical-resources' / 'Sentiments'
    anger_p = sentiment_path / "Anger" / "EmoSN_anger.txt"
    dataset_dir = Path('.') / 'data' / 'twitter-messagges'
    output_p = Path('.') / 'output'

    # Parte nuova
    prep = Preprocessor()
    # prep.get()  # TODO: debug toglierlo

    # data = prep.load_data(options.input)
    # prep.preprocess(data)

    # Test gestione twitter
    for file_name in os.listdir(dataset_dir):
        file_path = dataset_dir / file_name

        for sentiment in prep.get_sentiments():
            if(sentiment in file_name):
                current_sentiment_name = sentiment
                break

        print('Prepocessing delle frasi del sentimento {}'.format(
            current_sentiment_name))

        with open(file_path, 'r', encoding='utf8') as file:
            count = 1
            for line in file.readlines():
                print('{}:\t{}'.format(count, line))
                count += 1
                prep.preprocess(line, current_sentiment_name)