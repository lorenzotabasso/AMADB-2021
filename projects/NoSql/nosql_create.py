import os
import time
from pathlib import Path
from noslq_preproccesing import Preprocessor_NoSql
from nosqldbhandler import NoSqlDbHandler

if __name__ == "__main__":
    data_path = Path('.') / 'data'

    no_sql_handler = NoSqlDbHandler()
    prep = Preprocessor_NoSql()

    # Risorse lessicali

    start = time.time()

    dataset_dir = data_path / 'lexical-resources' / 'Sentiments'
    no_sql_handler.load_lexical_resources(dataset_dir)

    end = time.time()
    total_time = end - start
    print('Caricamento risorse compiuto in: {:.2f} secondi'.format(total_time))

    # Tweets
    dataset_dir = data_path / 'twitter-messages'

    for file_name in os.listdir(dataset_dir):
        file_path = dataset_dir / file_name

        start = time.time()
        print(f'Sto lavorando sul file: {file_name}')

        for sentiment in no_sql_handler.get_sentiments():
            if(sentiment in file_name):
                current_sentiment_name = sentiment
                break

        print('Prepocessing delle frasi del sentimento {}'.format(
            current_sentiment_name))

        with open(file_path, 'r', encoding='utf8') as file:
            tweets = []
            count = 1

            for line in file.readlines():
                # print('{}:\t{}'.format(count, line))
                count += 1
                tweets.append(prep.preprocess(line, current_sentiment_name))
                # if count == 1000:
                # break

            print('Scrittura su database.')
            no_sql_handler.load_tweets(tweets)

        end = time.time()
        print('Processamento del file {} compiuto in {:.2f} secondi'.format(
            file_name, end - start))

        total_time += end - start

    print('Tempo totale create MongoDB: {:.2f} secondi'.format(total_time))
