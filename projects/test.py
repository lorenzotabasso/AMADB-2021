from NoSql.nosqldbhandler import NoSqlDbHandler
import unittest
from Relational.relationaldbhandler import RelationalDbHandler

class GlobalTest(unittest.TestCase):

    def __init__(self, methodName: str) -> None:
        self.maxDiff = None 
        super().__init__(methodName=methodName)

    def setUp(self):
        self.verificationErrors = []

    def tearDown(self):
        self.assertEqual([], self.verificationErrors)

    def test_frequencty(self):
        handler_no_sql = NoSqlDbHandler()
        handler = RelationalDbHandler()
        
        for sentiment in handler_no_sql.get_sentiments():
            w_frequency = handler_no_sql.word_frequencies(sentiment, 10)
            most_present_w = handler.token_most_present(handler.WORD_TYPE, sentiment, 10)
            for (w1 , w2) in zip(w_frequency, most_present_w):
                try: 
                    self.assertEqual(w1[0], w2[0])
                except AssertionError as e:
                    self.verificationErrors.append(str(e))

if __name__ == '__main__':

    unittest.main()