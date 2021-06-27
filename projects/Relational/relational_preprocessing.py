import csv
import sys
import nltk
from pathlib import Path
from optparse import OptionParser

from projects.Relational.relationaldbhandler import RelationalDbHandler


class Preprocessor:
    __PROCESSING_PATH = Path('../..') / 'data' / 'processing'
    __SLANG_WORDS_PATH = __PROCESSING_PATH / 'slang_words.txt'
    __PUNCTUATION_PATH = __PROCESSING_PATH / 'punctuation.txt'

    __slang_words = {}
    __punctuation = []
    __stopwords = None

    def __init__(self):
        self.__handler = RelationalDbHandler()

        self.__slang_words = self.__read_slang_words(self.__SLANG_WORDS_PATH)
        self.__punctuation = self.__read_punctuation(self.__PUNCTUATION_PATH)
        self.__stopwords = set(nltk.corpus.stopwords.words('english'))

    @staticmethod
    def __read_slang_words(file_path: Path) -> dict:
        slang_words_map = {}

        with open(file_path, 'r') as f:
            for line in f.readlines():
                text = line.strip()
                splitted_txt = text.split(':')  # Split on :
                slang_words_map[splitted_txt[0].strip()] = splitted_txt[1].strip()

    @staticmethod
    def __read_punctuation(file_path: Path) -> list:
        punctuation_list = []

        with open(file_path, 'r') as f:
            for line in f.readlines():
                punctuation_list.append(line.strip())

        return punctuation_list

    def load_data(self) -> list:
        """
        It reads che definition's CSV
        :return: four list containing the read definitions.
        """
        emoSN = []

        with open(options.input, "r", encoding="utf-8") as dataset:
            for line in dataset:
                emoSN.append(line)

            print("finished!")
            return emoSN

    def preprocess(self, raw_data):
        preprocessed_data = []

        for line in raw_data:
            if "_" not in line:
                preprocessed_data.append(line)

        print("{0} ok!".format(len(preprocessed_data)))


if __name__ == "__main__":
    sentiment_path = Path('../..') / 'data' / 'lexical-resources' / 'Sentiments'
    anger_p = sentiment_path / "Anger" / "EmoSN_anger.txt"
    output_p = Path('../..') / 'output'

    argv = sys.argv[1:]
    parser = OptionParser()

    parser.add_option("-i", "--input", help='input file', action="store", type="string", dest="input",
                      default=anger_p)

    parser.add_option("-o", "--output", help='output directory', action="store", type="string", dest="output",
                      default=output_p / "Es1/")

    (options, args) = parser.parse_args()

    # Parte nuova
    prep = Preprocessor()

    data = prep.load_data()
    prep.preprocess(data)

    if options.input is None:
        print("Missing mandatory parameters")
        sys.exit(2)
