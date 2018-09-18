# Pull articles from interesting dates for analysis
# Use the same articles we use to build STM so that we can also look at their topic distributions

import argparse
import pandas
import pickle
from datetime import datetime
from nltk import tokenize
from collections import Counter
import operator

import sys
sys.path.append("..")
from get_dates import get_month_prev, get_good_month_prev
from params import Params

params = Params()

# For the given date range, we want:
# 1-2 articles for each primary frame
#       Words that signify primary frame
#       Other frames in those articles + words that signify each frame
#       Topic distributions for each article
def get_article_sample(date_range, all_data, code_to_lex):
    print(date_range)
    frame_to_article = {}

    # take a random sample accross all dates? Or for a specific date?
    # Let's start with one article per primary frame
    for idx,row in all_data.iterrows():

        if not row.loc["date"] in date_range:
            continue

        text = tokenize.word_tokenize(row.loc["documents"])
        topics = row.iloc[3:]
        text_counter = Counter(text)

        frame_to_words = {}
        sums = []
        for f in code_to_lex:
            sums.append((f, sum([text_counter[w] for w in code_to_lex[f]])))
            frame_words = [(w,text_counter[w]) for w in code_to_lex[f] if text_counter[w] > 0]
            if sum([i[1] for i in frame_words]) >= params.LEX_COUNT:
                frame_to_words[f] = frame_words

        frame, word_count = max(sums, key=operator.itemgetter(1))

        # We would call this "Other"
        if word_count < params.LEX_COUNT:
            continue

        if frame in frame_to_article:
            continue

        frame_to_article[frame] = frame, word_count, frame_to_words, row.loc["documents"], row.loc["date"], topics
        if len(frame_to_article) == len(code_to_lex):
            break

    for frame in frame_to_article:
        print(frame, frame_to_article[frame])



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--percent_change", default="/usr1/home/anjalief/corpora/russian/percent_change/russian_rtsi_rub.csv")
    parser.add_argument("--article_csv", default="/usr1/home/anjalief/stm/russian/data/monthly_usa_izvestiia.csv")
    parser.add_argument("--topic_weights", default="./stm20.csv")
    parser.add_argument("--frame_lex", default="./cache/frame_to_lex_v2_200.pickle")
    args = parser.parse_args()


    frame_to_lex = pickle.load(open(args.frame_lex, "rb"))

    text_data = pandas.read_csv(args.article_csv)
    topics = pandas.read_csv(args.topic_weights)
    all_data = pandas.concat([text_data, topics], axis=1)

    all_data['date'] = all_data['date'].apply(lambda d:datetime.date(datetime.strptime(d, '%d/%m/%Y')))

    all_data = all_data.sample(frac=1, random_state=1).reset_index(drop=True)

    assert len(text_data) == len(topics), "Error: STM output does not equal STM input"

    # take month just after a downturn as bad dates, and months of the downturn as good dates
    good_dates, bad_dates = get_month_prev(args.percent_change, percent=10)
#    get_article_sample(good_dates, all_data, frame_to_lex)

    # take month just after an upturn as good dates, and months of the upturn as good dates
#    good_dates, bad_dates = get_good_month_prev(args.percent_change, percent=10)
    get_article_sample(bad_dates, all_data, frame_to_lex)




if __name__ == "__main__":
    main()
