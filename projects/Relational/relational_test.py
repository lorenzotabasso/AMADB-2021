from relationaldbhandler import RelationalDbHandler

import unittest

class RelationalTest(unittest.TestCase):

    def test_sentiments(self):
        handler = RelationalDbHandler()
        sentiments = ['anger', 'anticipation', 'disgust', 'fear', 'joy', 'sadness', 'surprise', 'trust']
        self.assertEqual(handler.read_attributes(), sentiments)


if __name__ == '__main__':

    handler = RelationalDbHandler()
    limit = 7

    for sentiment in handler.read_attributes():
        most_present_j = handler.token_most_present(handler.EMOJI_TYPE, sentiment, limit)
        most_present_h = handler.token_most_present(handler.HASHTAG_TYPE, sentiment, limit)
        print(f'For sentiment {sentiment} the top {limit} tokens most present are:\n{most_present_j}\n{most_present_h}\n')

    unittest.main()
    
