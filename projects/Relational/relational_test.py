import time
from relationaldbhandler import RelationalDbHandler
from pathlib import Path

if __name__ == '__main__':
    sentiments = ['anger', 'anticipation', 'disgust', 'fear', 'joy', 'sadness', 'surprise', 'trust']

    data_path = Path('.') / 'data'

    db_creator = RelationalDbHandler()

    start = time.time()
    
    print('Inserimento dei twitter messages.')
    twitter_messages_dir = data_path / 'twitter-messagges'
    
    print('Inserimento emoji.')
    emoji_path = data_path / 'processing' / 'emoji.json'
    db_creator.load_emoticon_or_emoij(token_type=db_creator.EMOJI_TYPE, file_path=emoji_path)

    print('Inserimento emoticon.')
    emoji_path = data_path / 'processing' / 'emoticons.json'
    db_creator.load_emoticon_or_emoij(token_type=db_creator.EMOTICON_TYPE, file_path=emoji_path)
    # TODO ci sto lavorando
    # db_creator.load_twitter_messages(twitter_messages_dir)
    
    end = time.time()
    print('Inserimento in MariaDB: {:.2f} secondi'.format(end - start))

