
from nosqldbhandler import NoSqlDbHandler
import unittest


class NoSqlTest(unittest.TestCase):

    def test_sentiments(self):
        handler = NoSqlDbHandler()
        sentiments = ['anger', 'anticipation', 'disgust',
                      'fear', 'joy', 'sadness', 'surprise', 'trust']
        self.assertEqual(handler.get_sentiments(), sentiments)


if __name__ == '__main__':
    unittest.main()
    handler = NoSqlDbHandler()

    for sentiment in handler.get_sentiments():
        w_frequency = handler.word_frequencies(sentiment, 15)
        print(f'For sentiment {sentiment} the top 10 tokens most present are:\n{w_frequency[5:]}')