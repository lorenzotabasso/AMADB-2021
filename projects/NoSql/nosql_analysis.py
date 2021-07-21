import os
from collections import defaultdict, namedtuple
from pathlib import Path

import pandas as pd
from matplotlib import pyplot as plt

from projects.NoSql.nosqldbhandler import NoSqlDbHandler

if __name__ == '__main__':
    handler = NoSqlDbHandler()

    # Dizionario di supporto per la creazione del Pandas DataFrame
    d = defaultdict(list)

    lexical_resource = handler.get_lexical_resources()
    tweets = handler.get_tweets()
    shared_words = handler.get_common_words()

    # Calcoliamo prima il numero totale di tweet per ogni sentimento,
    # ci servirà dopo
    print("Calcolo il numero di parole di ogni dataset di tweet relativo a un sentimento")
    tweets_for_sentiment = {}
    for i in range(len(tweets)):
        # tweets fotmat:
        # ('fear', ['taylor', 'kept', 'throwing', 'ball', 'gutter', 'get', 'strike', 'whatt'])

        sentiment = tweets[i][0]
        if sentiment not in tweets_for_sentiment:
            tweets_for_sentiment[sentiment] = len(tweets[i][1])
        else:
            tweets_for_sentiment[sentiment] += len(tweets[i][1])

    print("\nCalcolo le statistiche sulle risorse")
    for lr in lexical_resource:
        # Ricordiamo che il formato di lr è:
        # ('NRC_fear', 'fear', ['dementia', 'barbarian', 'bane', ...])
        DatasetStatistic = namedtuple('DatasetStatistic',
                                      'sentiment lex_resource n_lex_words n_twitter_words common_words '
                                      'perc_presence_lex_res perc_presence_twitter')
        sentiment = lr[1]
        lex_resource = lr[0]
        n_lex_words = len(lr[2])
        n_twitter_words = tweets_for_sentiment[sentiment]

        common_words = 0
        perc_presence_lex_res = 0
        perc_presence_twitter = 0
        for sw in shared_words:
            # Formato di sw: [sentiment, lexical_resource, [common words]]
            if sw[1] == sentiment:
                if sw[0] == lex_resource:
                    common_words = len(sw[2])
                    perc_presence_lex_res = common_words / n_lex_words
                    perc_presence_twitter = common_words / n_twitter_words

        # Componiamo la tupla da inserire nel dizionario di supporto
        row = DatasetStatistic(sentiment,
                               lex_resource,
                               n_lex_words,
                               n_twitter_words,
                               common_words,
                               perc_presence_lex_res,
                               perc_presence_twitter)

        # Inseriamo la tupla appena creata nel dizionario di supporto
        d['sentiment'].append(row.sentiment)
        d['lex_resource'].append(row.lex_resource)
        d['n_lex_words'].append(row.n_lex_words)
        d['n_twitter_words'].append(row.n_twitter_words)
        d['shared_words'].append(row.common_words)
        d['perc_presence_lex_res'].append(row.perc_presence_lex_res)
        d['perc_presence_twitter'].append(row.perc_presence_twitter)

    # Creiamo il Pandas DataFrame che conterrà i dati
    df = pd.DataFrame(data=d).round(6)

    # Per ogni sentimento e le risorse lessicali ad esso associate,
    # salviamo su disco un istogramma.
    for s in tweets_for_sentiment:
        # Filtriamo il singolo sentimento usando Pandas
        local_df = df.loc[df['sentiment'] == s]

        # Per ogni sentimento, componiamo e salviamo l'istogramma
        ax = local_df.plot(title=f'Nosql - {s.capitalize()}',
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

        print(f"\tSalvo il plot del sentimento {s}")
        path_output = Path('.') / 'output' / 'histogram' / f'nosql_histogram_{s}.png'
        plt.savefig(path_output)

    # Preparazione del DataFrame per essere scritto sull'excel.
    # Facciamo una copia per sicurezza.
    df2 = pd.DataFrame(data=d).round(6)
    df2.sort_values(by=['sentiment', 'lex_resource'], inplace=True)

    print('\nScrivo il file statistics.xlsx')
    excel_output = 'output/statistics.xlsx'
    if os.path.isfile(excel_output):
        # Se il file è stato creato in precedenza, ci appendiamo e aggiorniamo il foglio
        with pd.ExcelWriter(excel_output, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df2.to_excel(writer, sheet_name='nosql')
    else:
        # Se il file non è stato creato in precedenza, lo creiamo noi
        with pd.ExcelWriter(excel_output, mode='w') as writer:
            df2.to_excel(writer, sheet_name='nosql')
