#!/usr/bin/env python3

# Need to run diachronic_word_embeddings to create
# models before using this script

# Input: list of keywords (country names); list of positive words; list of negative words; economic indicator
# For each country, measure correlation of positive/negative words with economic indicators
# Output countries with the strongest correlations
import gensim
import argparse
from gensim.models import KeyedVectors
import os
from datetime import date
from collections import defaultdict

import sys
sys.path.append("..")
from article_utils import get_files_by_time_slice
from econ_utils import load_econ_file
from utils import *

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", default="/usr1/home/anjalief/russian_model_cache")
    parser.add_argument("--keywords", default="/usr1/home/anjalief/corpora/russian/countries.txt")
    parser.add_argument("--econ_file", default="/usr1/home/anjalief/corpora/russian/russian_monthly_gdp.csv")
    parser.add_argument('--timestep', type=str,
                        default='monthly',
                        choices=['monthly', 'quarterly', 'yearly'])
    parser.add_argument("--pos_lexicon", default="/usr1/home/anjalief/corpora/russian/ru.filtered.pos")
    parser.add_argument("--neg_lexicon") #default="/usr1/home/anjalief/corpora/russian/ru.filtered.neg")
    args = parser.parse_args()

    keywords = set(load_file(args.keywords))
    pos_words = []
    neg_words = []

    if args.pos_lexicon:
        pos_words = load_file(args.pos_lexicon)

    if args.neg_lexicon:
        neg_words = load_file(args.neg_lexicon)

    keyword_to_score_sequence = defaultdict(list)

    date_seq, filenames = get_files_by_time_slice(
        args.model_path, args.timestep, suffix= "_" + args.timestep + ".pickle")

    for filename in filenames:
        assert(len(filename) == 1)
        filename = filename[0]
        wv = KeyedVectors.load(filename)

        # flip sign on distance to negative words
        # we're measuring if the keyword is close to positive words and far from negative words
        # Then, a positive correlation with economic indicator means
        # We talk about this country more positively in good economic times
        # We expected to see positive correlations for U.S. and negative correlations for Russia
        # (i.e. as Russia does worse, we talk more about how great Russia is and how bad
        # everywhere else is)
        sign = 1
        to_remove = set()
        for keyword in keywords:
            # We may only have 1 lexicon. In that case, set similarity to 0
            # for other lexicon
            if pos_words:
                pos = get_similarity(keyword, pos_words, wv)
            else:
                pos = 0

            # we're missing this country
            if pos is None:
                to_remove.add(keyword)
                continue

            if neg_words:
                neg = get_similarity(keyword, neg_words, wv)
            else:
                neg = 0

            if neg is None:
                to_remove.add(keyword)
                continue

            keyword_to_score_sequence[keyword].append((pos * sign) - (neg * sign))

        # skip countries that are not in vocab
        for c in to_remove:
            keywords.remove(c)
            assert not c in keyword_to_score_sequence

    for c in keyword_to_score_sequence:
        assert len(keyword_to_score_sequence[c]) == len(date_seq), \
            str(keyword_to_score_sequence[c]) + " " + str(date_seq)

    if args.econ_file:
        econ_seq = load_econ_file(args.econ_file, args.timestep, date_seq)

        corrs = []
        for k in keyword_to_score_sequence:
            corr = get_corr(keyword_to_score_sequence[k], econ_seq)
            corrs.append((corr,k,keyword_to_score_sequence[k]))
            if k in ['USA']:
                print (k, corr)
                for x,y in zip(keyword_to_score_sequence[k], econ_seq):
                    print (x,y)

        corrs.sort(key=lambda x: x[0])

        print ("TOP")
        for t in corrs[:10]:
            print (t)
        print ()
        print ("BOTTOM")
        for t in corrs[-10:]:
            print (t)



if __name__ == "__main__":
    main()
