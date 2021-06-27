import time
from projects.Relational.relationaldbhandler import RelationalDbHandler
from pathlib import Path

if __name__ == '__main__':
    sentiments = ['anger', 'anticipation', 'disgust', 'fear', 'joy', 'sadness', 'surprise', 'trust']

    data_path = Path('../..') / 'data'

    db_creator = RelationalDbHandler()

    start = time.time()

    print('Creazione del database relazionale.')
    sql_file_path = data_path / 'mariadb.sql'
    db_creator.create(sql_file_path)

    print('Inserimento delle risorse lessicali.')
    dataset_dir = data_path / 'lexical-resources' / 'Sentiments'
    db_creator.load_lexical_resources(dataset_dir)

    end = time.time()

    print('Relazionale: {}'.format(end - start))
