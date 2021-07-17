from pathlib import Path
from relationaldbhandler import RelationalDbHandler
from wordcloud import WordCloud
import pandas as pd


def print_and_save_wc(handler, all_sentiments, n_most_presents_token):
    for s in all_sentiments:
        lex_resources = handler.get_all_lex_resources_for_sentiment(s)
        for lr in lex_resources:
            n_lex_words = handler.get_n_lex_words(lr)
            n_twitter_words = handler.get_n_twitter_words(s)
            shared_words = handler.get_shared_words(lr, s)

            perc_presence_lex_res = shared_words / n_lex_words
            perc_presence_twitter = shared_words / n_twitter_words

            print("S: {0}, LR: {1}".format(s, lr))
            print("\tn_lex_words: {0}".format(n_lex_words))
            print("\tn_twitter_words: {0}".format(n_twitter_words))
            print("\tshared_words: {0}".format(shared_words))
            print("\tperc_presence_lex_res: {0:.6f}".format(perc_presence_lex_res))
            print("\tperc_presence_twitter: {0:.6f}\n".format(perc_presence_twitter))

            print(f"Finding first {n_most_presents_token} most present tokens")
            most_present_token = handler.token_most_present(0, s, n_most_presents_token)
            
            wc = WordCloud(background_color='white', width=400, height=200)
            wc.fit_words(most_present_token)
            wc.to_file(f'output/wordcloud/cloud_{s}.png')

            # path_output = Path('.') / 'output '/ 'wordcloud' / f'cloud_{s}.png'

def build_new_resource(handler: RelationalDbHandler, resource_path: Path) -> None:
    """
    Creo un nuovo file contenente le nuove parole associate a un sentimento provenienti dai tweet
    Utilizzando pandas DataFrame
    :param handler: il nostro gestore del db
    :type handler: RelationalDbHandler
    :param resource_path: percorso nella cartella
    :type resource_path: Path
    """
    s_list = handler.get_sentiments()
    new_resources = pd.DataFrame(columns=s_list)

    for sentiment in s_list:
        new_words = handler.new_words(sentiment)
        new_resources[sentiment] =  pd.Series(new_words)
    
    new_resources.to_csv(resource_path)

if __name__ == '__main__':
    handler = RelationalDbHandler()

    all_sentiments = handler.get_all_sentiments()
    n_most_presents_token = 100

    print_and_save_wc(handler, all_sentiments, n_most_presents_token)

    new_res_path = Path('.') / 'output' / 'new_sentiments.csv'
    build_new_resource(handler, new_res_path)


