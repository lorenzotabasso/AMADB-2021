from wordcloud import WordCloud

from projects.relational.relationaldbhandler import RelationalDbHandler


if __name__ == '__main__':
    handler = RelationalDbHandler()

    all_sentiments = handler.get_all_sentiments()
    n_most_presents_token = 100

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
        wc.to_file(f'output/wc_{s}.png')

        print("\tDone\n")

        # Plotting the word cloud
        # plt.figure(figsize=[450, 250])
        # plt.imshow(wc, interpolation='bilinear')
        # plt.axis("off")
        # plt.show()
