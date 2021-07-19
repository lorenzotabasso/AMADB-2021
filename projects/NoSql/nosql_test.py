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
