from pathlib import Path
import string
from relationaldbhandler import RelationalDbHandler
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt 
from os import path

NUM_WORDS_WC = 50
NUM_EMOJI_WC = 20
NUM_EMOTICON_WC = 20
NUM_HASHTAG_WC = 50

MAP_TOKEN_TYPE = {0: "word", 1: "emoji", 2:"emoticon", 3:"hashtag"}

# OVERKIll
def common_world_removal(list_tokens: list) -> None:
    """

    """
    from collections import Counter

    cnt = Counter()
    for elem in list_tokens:
        cnt[elem] += 1
            
    cnt.most_common(10)

    # Removing the frequent words
    freq = set([w for (w, _) in cnt.most_common(10)])
    # function to remove the frequent words
    def freqwords(text):
        return " ".join([word for word in str(text).split() if word not in freq])
    # Passing the function freqwords
    result = map(freqwords, list_tokens)
    return list(result)

def save_word_cloud (list_token: list, sentiment: str, token_type:int) -> None:
    """
    salva in "Output/Word Clouds" le word clouds relative ai vari parametri.
    :param list_token: [description]
    :param sentiment: [description]
    :param token_type: [description]
    """
    input_wordcloud = ""
    for token, freq in list_token:
        input_wordcloud += (token+" ")*freq
    
    normal_word = r"(?:\w[\w']+)"
    ascii_art = r"(?:[{punctuation}][{punctuation}]+)".format(punctuation=string.punctuation)
    emoji = r"(?:[^\s])(?<![\w{ascii_printable}])".format(ascii_printable=string.printable)
    regexp = fr"{normal_word}|{ascii_art}|{emoji}"


    font_path = path.join("font", "symbola.ttf")
    wordcloud = WordCloud(font_path=font_path, regexp=regexp, collocations=False).generate(input_wordcloud)

    plt.figure(figsize = (4, 4), facecolor = None) 
    plt.imshow(wordcloud) 
    plt.axis("off") 
    plt.tight_layout(pad = 0)

    token_type_str = MAP_TOKEN_TYPE.get(token_type)

    path_output = Path('.') / 'output' / 'wordcloud' /  "{}".format(token_type_str) / 'cloud_{}.png'.format(sentiment)
    plt.savefig(path_output)
    plt.close()


def world_cloud(db_interface: RelationalDbHandler, sentiment: str, token_type: int, limit: int) -> None:
    """
    chiama il salvataggio della word cloud relativa al sentimento `sentiment`
    relativa ai token di tipo `token_type` con `limit` parole al suo interno
    """
    
    tokens = db_interface.token_most_present(token_type, sentiment, limit)
    if token_type == 0:
        tokens = tokens[5:]
    save_word_cloud(tokens, sentiment, token_type)


def print_all_word_clouds(db_interface: RelationalDbHandler) -> None:
    """
    metodo wrapper per il salvataggio delle word clouds.
    :param db_interface: 
    """
    sentiments = db_interface.get_sentiments()

    token_types = [db_interface.WORD_TYPE, db_interface.EMOJI_TYPE, db_interface.EMOTICON_TYPE, db_interface.HASHTAG_TYPE]
    num_word_cloud = [NUM_WORDS_WC, NUM_EMOJI_WC, NUM_EMOTICON_WC, NUM_HASHTAG_WC]
    
    for sentiment in sentiments:
        print(f"Finding first 50 most present tokens for sentiment {sentiment}")
        for i in range(len(token_types)):
            world_cloud(db_interface, sentiment, token_types[i], num_word_cloud[i])


def stats_on_lexical_r(handler, all_sentiments):
    for s in all_sentiments:
        lex_resources = handler.get_all_lex_resources_for_sentiment(s)
        d = defaultdict(list)

        for lr in lex_resources:
            n_lex_words = handler.get_n_lex_words(lr)
            n_twitter_words = handler.get_n_twitter_words(s)
            shared_words = handler.get_shared_words(lr, s)

            perc_presence_lex_res = shared_words / n_lex_words
            perc_presence_twitter = shared_words / n_twitter_words

            print("Statistics for S: {0}, LR: {1}".format(s, lr))
            print("\tn_lex_words: {0}".format(n_lex_words))
            print("\tn_twitter_words: {0}".format(n_twitter_words))
            print("\tshared_words: {0}".format(shared_words))
            print("\tperc_presence_lex_res: {0:.6f}".format(perc_presence_lex_res))
            print("\tperc_presence_twitter: {0:.6f}\n".format(perc_presence_twitter))

            d['sentiment'].append(s)
            d['lex_resource'].append(lr)
            d['n_lex_words'].append(n_lex_words)
            d['n_twitter_words'].append(n_twitter_words)
            d['shared_words'].append(shared_words)
            d['perc_presence_lex_res'].append(perc_presence_lex_res)
            d['perc_presence_twitter'].append(perc_presence_twitter)

        print("Showing plot")
        df = pd.DataFrame(data=d)
        df.plot(title=s.capitalize(),
                x='lex_resource',
                xlabel='Lexical Resource',
                y=['perc_presence_lex_res', 'perc_presence_twitter'],
                ylabel='Percentage',
                kind="bar",
                rot=0)
        #plt.show()
        print("\tSaving plot to disk")
        plt.savefig(f'output/plot/plot_{s}.png')
        print("\tDone")

        print("Creating word cloud")
        print(f"\tFinding first {n_most_presents_token} most present tokens")
        most_present_token = handler.token_most_present(0, s, n_most_presents_token)
        wc = WordCloud(background_color='white', width=400, height=200)
        wc.fit_words(most_present_token)
        wc.to_file(f'output/wordcloud/cloud_{s}.png')

        # path_output = Path('.') / 'output '/ 'wordcloud' / f'cloud_{s}.png'
        print("\tSaving word cloud to disk")
        print("\tDone\n")


def build_new_resource(handler: RelationalDbHandler, resource_path: Path) -> None:
    """
    Creo un nuovo file contenente le nuove parole associate a un sentimento provenienti dai tweet
    Utilizzando pandas DataFrame
    :param handler: il nostro gestore del db
    :type handler: RelationalDbHandler
    :param resource_path: percorso nella cartella
    :type resource_path: Path
    """
    print("Building new resource")
    s_list = handler.get_sentiments()
    new_resources = pd.DataFrame(columns=s_list)

    for sentiment in s_list:
        new_words = handler.new_words(sentiment)
        new_resources[sentiment] =  pd.Series(new_words)
    
    new_resources.to_csv(resource_path)
    print("Done")


if __name__ == '__main__':
    handler = RelationalDbHandler()

    all_sentiments = handler.get_all_sentiments()

    # stats_on_lexical_r(handler, all_sentiments)
    print_all_word_clouds(handler)

    new_res_path = Path('.') / 'output' / 'new_sentiments.csv'
    build_new_resource(handler, new_res_path)
