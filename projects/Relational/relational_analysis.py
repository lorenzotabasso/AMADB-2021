import os
from os import path
from pathlib import Path
import string
from collections import defaultdict

import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud

from relationaldbhandler import RelationalDbHandler


NUM_WORDS_WC = 50
NUM_EMOJI_WC = 20
NUM_EMOTICON_WC = 20
NUM_HASHTAG_WC = 50

MAP_TOKEN_TYPE = {0: "word", 1: "emoji", 2: "emoticon", 3: "hashtag"}


# OVERKIll
def common_world_removal(list_tokens: list) -> None:
    """
    OVERKILL, usare solo se necessario.
    Fa post-process eliminando le parole comuni in una lista di token.
    :param list_tokens: una lista di token da cui rimuovere le common words
    :return:
    """
    from collections import Counter

    cnt = Counter()
    for elem in list_tokens:
        cnt[elem] += 1

    cnt.most_common(10)

    # Removing the frequent words
    freq = set([w for (w, _) in cnt.most_common(10)])

    # function to remove the frequent words
    def freqwords(text):
        return " ".join([word for word in str(text).split() if word not in freq])
    # Passing the function freqwords
    result = map(freqwords, list_tokens)
    return list(result)


def save_word_cloud(list_token: list, sentiment: str, token_type: int) -> None:
    """
    salva in "Output/Word Clouds" le word clouds relative ai vari parametri.
    :param list_token: [description]
    :param sentiment: [description]
    :param token_type: [description]
    """
    input_wordcloud = ""
    for token, freq in list_token:
        input_wordcloud += (token+" ")*freq

    normal_word = r"(?:\w[\w']+)"
    ascii_art = r"(?:[{punctuation}][{punctuation}]+)".format(
        punctuation=string.punctuation)
    emoji = r"(?:[^\s])(?<![\w{ascii_printable}])".format(
        ascii_printable=string.printable)
    regexp = fr"{normal_word}|{ascii_art}|{emoji}"

    font_path = path.join("font", "symbola.ttf")
    wordcloud = WordCloud(font_path=font_path, regexp=regexp,
                          collocations=False).generate(input_wordcloud)

    plt.figure(facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)

    token_type_str = MAP_TOKEN_TYPE.get(token_type)

    path_output = Path('.') / 'output' / 'wordcloud' / "{}".format(
        token_type_str) / 'cloud_{}_{}.png'.format(sentiment, token_type_str)
    plt.savefig(path_output)
    plt.close()


def world_cloud(db_interface: RelationalDbHandler, sentiment: str, token_type: int, limit: int) -> None:
    """
    chiama il salvataggio della word cloud relativa al sentimento `sentiment`
    relativa ai token di tipo `token_type` con `limit` parole al suo interno
    """

    tokens = db_interface.token_most_present(token_type, sentiment, limit)
    if token_type == 0:
        tokens = tokens[5:]
    save_word_cloud(tokens, sentiment, token_type)
    print(f"\tSalvo la word cloud per il sentimento {sentiment}: {MAP_TOKEN_TYPE[token_type]}")


def print_all_word_clouds(db_interface: RelationalDbHandler) -> None:
    """
    metodo wrapper per il salvataggio delle word clouds.
    :param db_interface: 
    """
    sentiments = db_interface.get_sentiments()

    token_types = [db_interface.WORD_TYPE,
                   db_interface.EMOJI_TYPE,
                   db_interface.EMOTICON_TYPE,
                   db_interface.HASHTAG_TYPE]
    num_word_cloud = [NUM_WORDS_WC,
                      NUM_EMOJI_WC,
                      NUM_EMOTICON_WC,
                      NUM_HASHTAG_WC]

    for sentiment in sentiments:
        print(f"\nCerco i 50 token più presenti per il sentimento {sentiment}")
        for i in range(len(token_types)):
            world_cloud(db_interface, sentiment,
                        token_types[i], num_word_cloud[i])


def stats_on_lexical_r(handler):
    d = defaultdict(list)

    shared_words_for_lr = handler.get_shared_words()
    # formato [ ('anger', 'EmoSN_anger', 201) ...]

    # Ci servirà dopo
    all_sentiments = []
    for row in shared_words_for_lr:
        # row[0] = sentiment
        if row[0] not in all_sentiments:
            all_sentiments.append(row[0])

    for i in range(len(shared_words_for_lr)):
        s = shared_words_for_lr[i][0]
        lr = shared_words_for_lr[i][1]
        sw = shared_words_for_lr[i][2]

        print(f"\tSentimento: {s} - Risorsa lessicale: {lr}")
        n_lex_words = handler.get_n_lex_words(lr)
        n_twitter_words = handler.get_n_twitter_words(s)
        print(f"\t\tCalcolate n_lex_words e n_twitter_words")

        perc_presence_lex_res = sw / n_lex_words
        perc_presence_twitter = sw / n_twitter_words

        d['sentiment'].append(s)
        d['lex_resource'].append(lr)
        d['n_lex_words'].append(n_lex_words)
        d['n_twitter_words'].append(n_twitter_words)
        d['shared_words'].append(sw)
        d['perc_presence_lex_res'].append(perc_presence_lex_res)
        d['perc_presence_twitter'].append(perc_presence_twitter)

    # Creiamo il Pandas DataFrame che conterrà i dati
    df = pd.DataFrame(data=d).round(6)

    print("\tSalvo il plot su disco")
    for s in all_sentiments:
        # Filtriamo il singolo sentimento usando Pandas
        local_df = df.loc[df['sentiment'] == s]

        # Per ogni sentimento, componiamo e salviamo l'istogramma
        ax = local_df.plot(title=f'Relational - {s.capitalize()}',
                x='lex_resource',
                xlabel='Lexical Resource',
                y=['perc_presence_lex_res', 'perc_presence_twitter'],
                ylabel='Percentage',
                kind="bar",
                rot=0,
                figsize=(8, 6),
                legend=False
                )
        plt.legend(loc='upper left', bbox_to_anchor=(0.65, 1.15),
                   fancybox=True, shadow=True)

        # Poniamo come label sulle barre dell'istogramma il valore della
        # percentuale di perc_presence_lex_res e perc_presence_twitter
        for p in ax.patches:
            percentage_value = str(p.get_height())
            ax.annotate(percentage_value, (p.get_x() * 1.005, p.get_height() * 1.005))

        print(f"\t\tSalvo il plot per il sentimento {s}")
        path_output = Path('.') / 'output' / 'histogram' / f'relational_histogram_{s}.png'
        plt.savefig(path_output)

    # Preparazione del DataFrame per essere scritto sull'excel.
    # Facciamo una copia per sicurezza.
    df2 = pd.DataFrame(data=d).round(6)
    df2.sort_values(by=['sentiment', 'lex_resource'], inplace=True)

    print('\tScrivo il file statistics.xlsx')
    excel_output = 'output/statistics.xlsx'
    if os.path.isfile(excel_output):
        with pd.ExcelWriter(excel_output, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df2.to_excel(writer, sheet_name='relational')
    else:
        with pd.ExcelWriter(excel_output, mode='w') as writer:
            df2.to_excel(writer, sheet_name='relational')


def build_new_resource(handler: RelationalDbHandler, resource_path: Path) -> None:
    """
    Creo un nuovo file contenente le nuove parole associate a un sentimento provenienti dai tweet
    Utilizzando pandas DataFrame
    :param handler: il nostro gestore del db
    :type handler: RelationalDbHandler
    :param resource_path: percorso nella cartella
    :type resource_path: Path
    """
    print("Costruisco la risorsa che conterrà i nuovi sentimenti")
    s_list = handler.get_sentiments()
    new_resources = pd.DataFrame(columns=s_list)

    for sentiment in s_list:
        new_words = handler.new_words(sentiment)
        new_resources[sentiment] = pd.Series(new_words)

    print("Salvo il file new_sentiments.csv")
    new_resources.to_csv(resource_path)


if __name__ == '__main__':
    handler = RelationalDbHandler()

    #all_sentiments = handler.get_all_sentiments()

    print("Calcolo le statistiche sulle risorse")
    stats_on_lexical_r(handler) # all_sentiments

    print("\nCreazione di una word cloud per ogni sentimento")
    #print_all_word_clouds(handler)

    print("\nSalvo i nuovi sentimenti")
    #new_res_path = Path('.') / 'output' / 'new_sentiments.csv'
    #build_new_resource(handler, new_res_path)
