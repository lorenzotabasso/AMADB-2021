import time
from relationaldbhandler import RelationalDbHandler
from pathlib import Path

if __name__ == '__main__':
    sentiments = ['anger', 'anticipation', 'disgust', 'fear', 'joy', 'sadness', 'surprise', 'trust']

    data_path = Path('.') / 'data'

    db_creator = RelationalDbHandler()

    start = time.time()
    
    print('Inserimento dei twitter messages.')
    twitter_messages_dir = data_path / 'twitter-messages'
    
    # TODO ci sto lavorando
    # db_creator.load_twitter_messages(twitter_messages_dir)
    
    end = time.time()
    print('Inserimento in MariaDB: {:.2f} secondi'.format(end - start))

