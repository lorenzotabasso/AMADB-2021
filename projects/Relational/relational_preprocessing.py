import time
from relationaldbhandler import RelationalDbHandler
import json
import os
import re
import emoji
from pathlib import Path

import nltk


class Preprocessor:
    __PROCESSING_PATH = Path('.') / 'data' / 'processing'
    __SLANG_WORDS_PATH = __PROCESSING_PATH / 'slang_words.json'
    __PUNCTUATION_PATH = __PROCESSING_PATH / 'punctuation.txt'

    # Collection of dictionary for data
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

        # Read tokens from the db one for each type
        self.__emoticons = self.__handler.read_tokens(
            self.__handler.EMOTICON_TYPE)
        self.__emojis = self.__handler.read_tokens(self.__handler.EMOJI_TYPE)
        self.__words = self.__handler.read_tokens(self.__handler.WORD_TYPE)
        self.__hashtags = self.__handler.read_tokens(
            self.__handler.HASHTAG_TYPE)

        # struttura che conterrà i risultati intermedi del flusso
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
    Class of method for interacting with data in the datastructures
    Once filled with data they will be flushed to the DB
    """

    def get_sentiments(self) -> list:
        """
        :return: lista dei sentimenti recuperata dal database
        :rtype: list
        """
        return self.__sentiments

    def __add_data_tweet(self, sentiment: str) -> None:
        """
        Appendi alla lista dei twitter la tupla (tweet_id, sentiment)
        :param sentiment: string reppresenting the sentiment 
        :type sentiment: str
        """
        self.__max_tweet_id += 1
        self.__data[self.__DATA_TWEETS].append(
            (self.__max_tweet_id, sentiment))

    def __add_data_token(self, type: int, text: str) -> None:
        """
        Appendi alla lista dei dei token la tripletta (tkn_id, tkn_type, text)
        :param type: token_type
        :type type: int
        :param text: token da processare
        :type text: str
        """
        self.__max_token_id += 1
        self.__data[self.__DATA_TOKENS].append(
            (self.__max_token_id, type, text))

        # Aggiungo il token al dizionario/mappa appropriato sfruttando le costanti definite nel db-handler
        if type == self.__handler.WORD_TYPE:
            self.__words[text] = self.__max_token_id
        elif type == self.__handler.EMOTICON_TYPE:
            self.__emoticons[text] = self.__max_token_id
        elif type == self.__handler.EMOJI_TYPE:
            self.__emojis[text] = self.__max_token_id
        elif type == self.__handler.HASHTAG_TYPE:
            self.__hashtags[text] = self.__max_token_id

    def __add_data_contained_in(self, tweet_id: int, token_id: int, pos=None) -> None:
        """
        Appendi alla lista di "dato_contenuto_in" la quadruplets (dci_id, tweet_id, tkn_id, POS)
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
    Preprocessing helper methods: each for one specific task. DIVIDE ET IMPERA
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
    
    @staticmethod
    def de_emoji_fy(text) -> str:
        """
        Rimozione totale di emoticons/emoji ecc.
        :param text: messaggio da pulire
        :type text: str
        :return: ritorna una stringa pulita dal pattern regex
        :rtype: str
        """
        regrex_pattern = re.compile(pattern = "["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                            "]+", flags = re.UNICODE)
        return regrex_pattern.sub(r'',text)

    def __process_emo(self, msg: str) -> str:
        """
        Verifico se word è una emoticon/emoji conosciuta
        Agisco di conseguenza con il caso emoji più complicato
        :param msg: messaggio da analizzare
        :type msg: str
        :return: messaggio ripulito da emoji ed emoticons
        :rtype: str
        """
        # get_emoji_regexp from the https://pypi.org/project/emoji/, together with the usual split function
        for word in emoji.get_emoji_regexp().split(msg):
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
                self.__add_data_contained_in(
                    self.__max_tweet_id, emo_id, None)  # update dict & table

            msg = self.de_emoji_fy(msg)  # rimozione emoji
            
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
        # lemmatizzazione
        lemmatized_tagged_words = [(lemmatizer.lemmatize(
            w[0]), w[1]) for w in tagged_words]
        # remove stopwords
        filtered_words = [w for w in lemmatized_tagged_words if not w[0]
                          in self.__stopwords]

        return filtered_words

    def preprocess(self, msg: str, sentiment: str) -> None:
        '''
        TODO:
        ✓ Rimuovere USERNAME e URL
        ✓ Eliminare Stop Words
        ✓ Gestire le emoji/Emoticons
        ✓ Lemmatizzare parole 
        1. Memorizzare le parole nuove
        2. Conteggiare presenza nei tweet delle parole associate a ogni sentimento
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

        # remove punctuation from the msg
        msg = self.__clean_punctuation(msg)

        # tokenization, pos tagging, lemmatization, lower case and stop words elimination
        filtered_words = self.__words_from_msg(msg)

        # print(filtered_words)

        # Insert words in Database
        for word in filtered_words:
            word_id = self.__words.get(word[0])

            if word_id is None:
                self.__add_data_token(self.__handler.WORD_TYPE, word[0])
                word_id = self.__max_token_id

            self.__add_data_contained_in(self.__max_tweet_id, word_id, word[1])

        
    def common_world_removal(self) -> None:
        """

        """
        from collections import Counter

        cnt = Counter()
        for text in values:
            for word in text.split():
                cnt[word] += 1
                
        cnt.most_common(10)

        # Removing the frequent words
        freq = set([w for (w, _) in cnt.most_common(10)])
        # function to remove the frequent words
        def freqwords(text):
            return " ".join([word for word in str(text).split() if word not 
        in freq])
        # Passing the function freqwords




    def write_to_db(self) -> None:
        """
        Ogni lista presente in __data viene resa persistente, tramite
        opportune chiamate al DB-handler e reinizializzata 
        """
        self.__handler.load_tweets_batch(self.__data[self.__DATA_TWEETS])
        self.__data[self.__DATA_TWEETS] = []

        # TODO Problematica catena di emoji, missclassification.
        self.__handler.load_tokens_batch(self.__data[self.__DATA_TOKENS])
        self.__data[self.__DATA_TOKENS] = []

        self.__handler.load_contained_ins_batch(self.__data[self.__DATA_CONTAINED_INS])
        self.__data[self.__DATA_CONTAINED_INS] = []


if __name__ == "__main__":
    sentiment_path = Path('.') / 'data' / 'lexical-resources' / 'Sentiments'
    anger_p = sentiment_path / "Anger" / "EmoSN_anger.txt"
    dataset_dir = Path('.') / 'data' / 'twitter-messages'
    output_p = Path('.') / 'output'

    prep = Preprocessor()
    # prep.get()  # TODO: debug toglierlo

    # Test gestione twitter
    print('Inserimento dei twitter messages.')
    
    total_time = 0

    for file_name in os.listdir(dataset_dir):
        file_path = dataset_dir / file_name

        start = time.time()
        print(f'Sto lavorando sul file: {file_name}')

        for sentiment in prep.get_sentiments():
            if(sentiment in file_name):
                current_sentiment_name = sentiment
                break

        print('Preprocessing delle frasi del sentimento {}'.format(
            current_sentiment_name))

        with open(file_path, 'r', encoding='utf8') as file:
            count = 1
            for line in file.readlines():
                # print('{}:\t{}'.format(count, line))
                count += 1
                prep.preprocess(line, current_sentiment_name)
                if count == 1000:
                    break
                    
            print('Scrittura su database.')
            prep.write_to_db()

        end = time.time()
        print('Processamento del file {} compiuto in {:.2f} secondi'.format(
            file_name, end - start))
        total_time += end - start

    print('Inserimento concluso in {:.2f} secondi'.format(total_time))
