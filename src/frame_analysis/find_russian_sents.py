# Pull articles from interesting dates for analysis
# Use the same articles we use to build STM so that we can also look at their topic distributions

import argparse
import pickle
from datetime import datetime
from collections import Counter, defaultdict
import operator

import sys, os
sys.path.append("..")
from get_dates import get_month_prev, get_good_month_prev
from article_utils import LoadArticles
from params import Params
import random

from nltk import data
sentence_tokenizer = data.load('tokenizers/punkt/english.pickle')

params = Params()

# For the given date range, pull 50 random sentences that use frame
def get_sentence_sample(filenames, code_to_lex, second_filter=None, sample_size=20):
    frame_to_sentences = defaultdict(list)
    num_articles = 0
    total_articles = 0

    # take a random sample across all dates
    for filename in filenames:
        articles, _ = LoadArticles(filename, verbose=False)
        for article in articles:

            article_counter = Counter(article.split())
            if article_counter["USA"] < 2:
                continue

            total_articles += 1
            if second_filter:
                if sum([article_counter[w] for w in second_filter]) < 2:
                    continue

            num_articles += 1

            for frame in code_to_lex:
                if sum([article_counter[w] for w in code_to_lex[frame]]) >= params.LEX_COUNT:
                    frame_words = [w for w in code_to_lex[frame] if article_counter[w]>0]
                    frame_to_sentences[frame].append((article, frame_words))

            # sentences = sentence_tokenizer.tokenize(article)

            # for sentence in sentences:
            #     sent_counter = Counter(sentence.lower().split())
            #     for frame in code_to_lex:

            #         # filter relevant articles
            #         if sum([article_counter[w] for w in code_to_lex[frame]]) < params.LEX_COUNT:
            #             continue

            #         if sum([sent_counter[w] for w in code_to_lex[frame]]) > 1:
            #             frame_words = [w for w in code_to_lex[frame] if sent_counter[w] > 0]
            #             frame_to_sentences[frame].append((sentence, frame_words))

    print(num_articles / total_articles)
    for frame in code_to_lex:
        frame_to_sentences[frame] = random.sample(frame_to_sentences[frame], sample_size)
    return frame_to_sentences


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--percent_change", default="/usr1/home/anjalief/corpora/russian/percent_change/russian_rtsi_rub.csv")
    parser.add_argument("--input_path", default="/usr1/home/anjalief/corpora/russian/yearly_mod_subs/iz_lower/init_files/")
    parser.add_argument("--frame_lex", default="./cache/russian_params.pickle")
    parser.add_argument("--second_filter", default="./lex_by_frame/bad_security_lex_filtered.txt")
    args = parser.parse_args()

    frame_to_lex = pickle.load(open(args.frame_lex, "rb"))
    new_frame_to_lex = {"Morality": frame_to_lex["Morality"]}
    frame_to_lex = new_frame_to_lex

    second_filter = [x.strip() for x in open(args.second_filter).readlines()]

    # take month just after a downturn as bad dates, and months of the downturn as good dates
    good_dates, bad_dates = get_month_prev(args.percent_change, percent=10)

    # good_dates1, bad_dates1 = get_good_month_prev(args.percent_change, percent=10)

    # print(good_dates)
    # print(bad_dates)
    # print()
    # print(good_dates1)
    # print(bad_dates1)



    # good_dates = good_dates + good_dates1
    # bad_dates = bad_dates + bad_dates1

    filenames = [os.path.join(args.input_path, str(d.year) + "_" + str(d.month) + ".txt.tok") for d in bad_dates]

    bad_sample = get_sentence_sample(filenames, frame_to_lex, second_filter)
    for frame in bad_sample:
        print(frame)
        for sent in bad_sample[frame]:
            print(sent)
        print()
    # print("*************************************************************************************************************************")

    # # take month just after an upturn as good dates, and months of the upturn as bad dates


    # good_filenames = [os.path.join(args.input_path, str(d.year) + "_" + str(d.month) + ".txt.tok") for d in good_dates]
    # good_sample = get_sentence_sample(good_filenames, frame_to_lex, second_filter)
    # for frame in good_sample:
    #     print(frame)
    #     for sent in good_sample[frame]:
    #         print(sent)
    #     print()
    # print()




if __name__ == "__main__":
    main()
