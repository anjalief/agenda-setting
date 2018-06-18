import sys
sys.path.append("..")

from article_utils import *
from get_dates import *
from collections import defaultdict, Counter
import argparse
import pickle
import math

from frame_salience import CountFrameFrequency
from basic_log_odds import USAvsNone

# import nltk
# tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

import re

def ComputeSentPMI(frame_to_lex, articles):
    frame_to_sent_count = defaultdict(int)
    frame_to_sent_and_usa_count = defaultdict(int)
    usa_sent_count = 0
    total_sent_count = 0

    for article in articles:
        is_USA = Counter(article.split())["USA"] >= 2

#        for s in tokenizer.tokenize(article):
        for s in re.split('\?|\.|\! ',article):
            total_sent_count += 1
            if is_USA:
                usa_sent_count += 1

            sentence_counter = Counter(s.split())

            for f in frame_to_lex:
                lex = frame_to_lex[f]
                count_frame_words = sum([sentence_counter[w] for w in lex])
                if count_frame_words >= 1:
                    frame_to_sent_count[f] += 1
                    if is_USA:
                        frame_to_sent_and_usa_count[f] += 1

    frame_to_pmi = {}
    total_sent_count = float(total_sent_count)
    for f in frame_to_lex:
        num = (frame_to_sent_and_usa_count[f] / total_sent_count)
        denom = (frame_to_sent_count[f] / total_sent_count) * (usa_sent_count / total_sent_count)
        if (denom == 0):
            frame_to_pmi[f] = 0
            continue
        frame_to_pmi[f] = math.log(num / denom, 2) / -math.log(num, 2)
    return frame_to_pmi

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--percent_change", default="/usr1/home/anjalief/corpora/russian/percent_change/russian_rtsi_rub.csv")
    parser.add_argument("--input_path", default="/usr1/home/anjalief/corpora/russian/yearly_mod_subs/iz_lower/init_files/")
    args = parser.parse_args()

    good_dates, bad_dates = get_month_prev(args.percent_change)

    frame_to_lex = pickle.load(open("frame_to_lex.pickle", "rb"))

    good_file_names = [os.path.join(args.input_path,
                                    str(d.year) + "_" + str(d.month) + ".txt.tok")
                       for d in good_dates]
    print (good_file_names)

    good_articles = []
    for f in good_file_names:
        good_articles += LoadArticles(f, verbose=False)[0]
    good_pmi = ComputeSentPMI(frame_to_lex, good_articles)
    for f in good_pmi:
        print(f, good_pmi[f])

    bad_file_names = [os.path.join(args.input_path,
                                   str(d.year) + "_" + str(d.month) + ".txt.tok")
                      for d in bad_dates]

    bad_articles = []

    print (bad_file_names)

    for f in bad_file_names:
        bad_articles += LoadArticles(f, verbose=False)[0]

    bad_pmi = ComputeSentPMI(frame_to_lex, bad_articles)
    for f in bad_pmi:
        print(f, bad_pmi[f])


def new_main():
    import glob
    input_path = "/usr1/home/anjalief/corpora/russian/yearly_mod_subs/iz_lower/init_files/*_*"
    all_articles = []
    for filename in glob.iglob(input_path):
        all_articles += LoadArticles(filename)[0]

    frame_to_lex = pickle.load(open("frame_to_lex_final.pickle", "rb"))

    bad_pmi = ComputeSentPMI(frame_to_lex, all_articles)
    for f in bad_pmi:
        print(f, bad_pmi[f])


if __name__ == "__main__":
    new_main()
