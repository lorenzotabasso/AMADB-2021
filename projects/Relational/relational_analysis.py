from projects.relational.relationaldbhandler import RelationalDbHandler

if __name__ == '__main__':
    handler = RelationalDbHandler()

    print(handler.get_n_lex_words('EmoSN_anger'))
    print(handler.get_n_twitter_words('fear'))
    print(handler.get_shared_words('EmoSN_anger', 'anger'))

    print(handler.get_all_lexical_resource())

    all_lex_res = handler.le
