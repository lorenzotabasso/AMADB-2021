
import time
from collections import defaultdict

import pandas as pd

from nosqldbhandler import NoSqlDbHandler, Common_words


def fill_common_words(lexical_resource: list, tweets: list, c_words: list) -> list:
    """
    Ritorna il numero di parole in comune tra le risorse lessicali e tweets che hanno lo stesso sentimento,
    in particolare solo quelle non già presenti!
    :param lexical_resource: una lista di tuple, una per risorsa lessicale.
    :param tweets: una lista di tuple, una tupla per ogni tweet.
    :param common_words: una lista inizialmente vuota, che verrà riempita dall'algoritmo.
    """
    count = 0
    for tweet in tweets:
        count += 1
        sentiment = tweet[0]
        for word in tweet[1]:
            # Scorriamo tutte le lexical resource
            for i in range(len(lexical_resource)):
                # Se trattano lo stesso sentimento
                if lexical_resource[i][1] == sentiment:
                    # Se la parola `word` è contenuta nella risorsa lessicale `i` esima,
                    # ma non è ancora contenuta tra le common words `i` esime,
                    # allora la aggiungiamo
                    if word in lexical_resource[i][2] and word not in c_words[i][2]:
                        c_words[i][2].append(word)

    return c_words


if __name__ == "__main__":
    handler = NoSqlDbHandler()

    print("Drop della collezione Common Words dal DB")
    handler.drop_common_words()

    start = time.time()

    print("Ottengo le risorse lessicali dal DB")
    lexical_resource = handler.get_lexical_resources()
    print("Ottengo i tweets dal DB")
    tweets = handler.get_tweets()

    # Nota: lexical resource è già una lista di tuple, del tipo
    # ('NRC_fear', 'fear', ['dementia', 'barbarian', 'bane', ... ])
    #
    # Ma noi la ricreiamo perché vogliamo che fill_common_words ci calcoli
    # le common words tra la risorsa lessicale e i tweet. Per questo,
    # la ricreiamo con la lista delle parole della risorsa vuota.
    empty_common_words = [(lr[0], lr[1], []) for lr in lexical_resource]

    # Calcolo delle common words tra le risorse lessicali e i tweets
    print("Calcolo le common words")
    common_w = fill_common_words(lexical_resource, tweets, empty_common_words)

    # Conversione nelle classe Common_words per effettuare il caricamento nel DB
    common_words_class = list(
        map(lambda x: Common_words(x[0], x[1], x[2]), common_w))

    # Caricamento delle common words nel db
    print("Carico le common words nel DB")
    handler.load_common_words(common_words_class)

    end = time.time()

    print('Tempo totale di creazione delle common words: {:.2f} secondi'.format(end - start))
