
from pathlib import Path
import time
from relationaldbhandler import RelationalDbHandler

if __name__ == "__main__":
    data_path = Path('.') / 'data'
    
    db_creator = RelationalDbHandler()

    start = time.time()
    
    print('Creazione del database relazionale.')
    sql_file_path = data_path / 'mariadb.sql'
    db_creator.create(sql_file_path)
    
    print('Inserimento delle risorse lessicali.')
    dataset_dir = data_path / 'lexical-resources' / 'Sentiments'
    db_creator.load_lexical_resources(dataset_dir)

    print('Inserimento emoticon.')
    # TODO
    print('Inserimento emoji.')
    # TODO

    end = time.time()
    print('Tempo totale create MariaDB: {:.2f} secondi'.format(end - start))