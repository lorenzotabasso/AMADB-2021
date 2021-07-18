from pathlib import Path
import time
from nosqldbhandler import NoSqlDbHandler

if __name__ == "__main__":
    data_path = Path('.') / 'data'

    no_sql_handler = NoSqlDbHandler()

    start = time.time()

    dataset_dir = data_path / 'lexical-resources' / 'Sentiments'
    no_sql_handler.load_lexical_resources(dataset_dir)

    end = time.time()
    print('Tempo totale create MongoDB: {:.2f} secondi'.format(end - start))