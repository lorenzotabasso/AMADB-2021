
import time
from nosqldbhandler import NoSqlDbHandler, Common_words


def fill_common_words(lexical_resource: list, tweets: list, c_words: list) -> list:
    """
    Ritorna il numero di parole in comune tra le risorse lessicali e tweets che hanno lo stesso sentimento,
    in particolare solo quelle non già presenti!
    :param lexical_resource: [description]
    :param tweets: [description]
    :param common_words: [description]
    """
    count = 0
    for tweet in tweets:
        count += 1
        sentiment = tweet[0]
        for word in tweet[1]:
            for i in range(len(lexical_resource)):
                # se trattano lo stesso sentimento
                if lexical_resource[i][1] == sentiment:
                    if word in lexical_resource[i][2] and word not in c_words[i][2]:
                        # la parola `word` è contenuta nella risorsa lessicale `i` esima
                        # e non è ancora contenuta tra le common words `i` esime
                        c_words[i][2].append(word)

    return c_words


if __name__ == "__main__":
    handler = NoSqlDbHandler()

    handler.drop_common_words()

    start = time.time()

    lexical_resource = handler.get_lexical_resources()
    tweets = handler.get_tweets()

    # calcolo delle parole comuni tra le risorse lessicali e quelle presenti nei tweets
    common_words = [(lr[0], lr[1], []) for lr in lexical_resource]
    common_w = fill_common_words(lexical_resource, tweets, common_words)

    # convertimento nelle classi Common_words per effettuare il caricamento nel db
    common_words_class = list(
        map(lambda x: Common_words(x[0], x[1], x[2]), common_w))

    # caricamento delle common words nel db
    handler.load_common_words(common_words_class)

    end = time.time()

    print('Tempo totale creazione common_words: {:.2f} secondi'.format(
        end - start))
