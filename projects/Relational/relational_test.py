import time
from projects.Relational.MariaDBConnector import MariaDBConnector
from pathlib import Path

if __name__ == '__main__':
    sentiments = ['anger', 'anticipation', 'disgust', 'fear', 'joy', 'sadness', 'surprise', 'trust']

    db_creator = MariaDBConnector()

    start = time.time()
    print('Creazione del database relazionale.')
    sql_file_path = Path('../../') / 'data' / 'mariadb.sql'
    db_creator.create(sql_file_path)
    end = time.time()

    print('Relazionale: {}'.format(end - start))
