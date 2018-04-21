#!/usr/bin/env python3

# Need to run diachronic_word_embeddings to create
# models before using this script

# Input: list of keywords (country names)
# Use EM algorithm to learn a set of countries and a set of words for which
# the similarity of country->word correlates with economic indicator
# For each country, measure correlation of positive/negative words with economic indicators
# Output learned country set and lexicon
import gensim
import argparse
from gensim.models import KeyedVectors
from diachronic_word_embeddings import YEARS, MONTHS, get_model_filename
import os
from datetime import date
from econ_utils import load_monthly_gdp, load_rtsi
from utils import *

from collections import defaultdict


# Helper function to compute correlation between two sets and economic data
def step_helper(model_path, known_set, test_set, econ_seq):
    test_to_similarity = defaultdict(list)

    for year in YEARS:
        for month in MONTHS:
            model_name = get_model_filename(model_path, year, month)
            wv = KeyedVectors.load(model_name)

            # get total similarity between this word and other set
            # shouldn't need to normalize by size of known set because it's
            # the same for all words
            for w in test_set:
                test_to_similarity[w].append(get_similarity(w, known_set, wv))

    words_and_corrs = []
    for w in test_to_similarity:
        corr = get_corr(test_to_similarity[w], econ_seq)
        words_and_corrs.append((w, corr))

    return words_and_corrs

# Assume we know the set of countries
# for each country, calculate distances from every word. Choose the words for which
# distance from countries has the highest correlation with econ_seq

# Sign allows us to look for words with negative correlations or positive correlations
# Words with positive correlation, means as economy gets better, these words get more
# similar to country names (expected for Russia and positive terms?)
# Negative correlation -- U.S. should get closer to bad words as economy does worse

# Return: set lexicon_size words with the highest correlations
def e_step(model_path, countries, vocab, lexicon_size, econ_seq, sign = 1):
    words_and_corrs = step_helper(model_path, known_set=countries, test_set=vocab, econ_seq=econ_seq)
    words_and_corrs.sort(key=lambda x: x[1], reverse=True)

    # return the words with the highest correlation
    # TODO: (or lowest correlation if we've flipped the sign)
    return [w for w in words_and_corrs[:lexicon_size]]

# Assume we know the lexicon of meaningful words. For every country, calculate
# similarity correlation with lexicon. Return all countries with a positive
# correlation (or negative if we're flipping the sign)
def m_step(model_path, lexicon, all_countries, econ_seq, sign = 1):
    words_and_corrs = step_helper(model_path, known_set=lexicon, test_set=all_countries, econ_seq=econ_seq)

    words_and_corrs.sort(key=lambda x: x[1], reverse=True)

    # return the words with positive correlation
    # TODO: (or negative correlation if we've flipped the sign)
    return [w[0] for w in words_and_corrs if w[1] > 0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", default="/usr1/home/anjalief/russian_model_cache")
    parser.add_argument("--keywords", default="/usr1/home/anjalief/corpora/russian/countries.txt")
    parser.add_argument("--gdp_file", default="/usr1/home/anjalief/corpora/russian/russian_monthly_gdp.csv")
    parser.add_argument("--lexicon_size", type=int, default=100)
    args = parser.parse_args()

    # FIRST: Gather inputs. Start with keywords, datelist, and vocab words from model
    keywords = set(load_file(args.keywords))

    # only pull vocab words that appear in first model. They (and only they) should appear in all models
    model_name1 = get_model_filename(args.model_path, YEARS[0], MONTHS[0])
    vocab = KeyedVectors.load(model_name1).index2entity

    # skip countries that are not in vocab
    for k in keywords:
        if not k in vocab:
            print ("MISSING COUNTRY", k)
    keywords = [k for k in keywords if k in vocab]

    date_seq = []
    for year in YEARS:
        for month in MONTHS:
            date_seq.append(date(int(year), int(month), 1))

    date_to_gdp = load_monthly_gdp(args.gdp_file)
    gdp_seq = [date_to_gdp[d] for d in date_seq]

    print ("DONE DATA LOADING")


    lexicon = e_step(args.model_path, keywords, vocab, args.lexicon_size, gdp_seq, sign = -1)
    for x in lexicon:
        print (x[0], x[1])

if __name__ == "__main__":
    main()
