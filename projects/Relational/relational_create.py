
from pathlib import Path
import time
from relationaldbhandler import RelationalDbHandler

if __name__ == "__main__":
    #data_path = Path('../..') / 'data'
    data_path = Path('.') / 'data'

    db_creator = RelationalDbHandler()

    start = time.time()
    
    print('Creazione del database relazionale.')
    sql_file_path = data_path / 'mariadb.sql'
    db_creator.create(sql_file_path)
    
    print('Inserimento delle risorse lessicali.')
    dataset_dir = data_path / 'lexical-resources' / 'Sentiments'
    db_creator.load_lexical_resources(dataset_dir)

    print('Inserimento emoji.')
    emoji_path = data_path / 'processing' / 'emoji.json'
    db_creator.load_emoticon_or_emoji(token_type=db_creator.EMOJI_TYPE, file_path=emoji_path)

    print('Inserimento emoticon.')
    emoji_path = data_path / 'processing' / 'emoticons.json'
    db_creator.load_emoticon_or_emoji(token_type=db_creator.EMOTICON_TYPE, file_path=emoji_path)

    end = time.time()
    print('Tempo totale create MariaDB: {:.2f} secondi'.format(end - start))