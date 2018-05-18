
#!/usr/bin/env python3

# Need to run diachronic_word_embeddings to create
# models before using this script

# Input: list of keywords (country names), # of clusters for knn
# Learn a set of words for which
# the similarity of country->word correlates with economic indicator
# Use KNN to generate possible lexicons, then compute similarity
# between lexicons and keywords
# output lexicon whose similarity to country name has strongest correlation
# with economic indicator
import gensim
import argparse
from gensim.models import KeyedVectors, Word2Vec
import os
from datetime import date
from utils import *
import sys
sys.path.append("..")
from article_utils import get_files_by_time_slice
from econ_utils import load_econ_file, difference

from collections import defaultdict


# Helper function to compute correlation between two sets and economic data
def step_helper(filenames, known_set, test_set, econ_seq = None):
    test_to_similarity = defaultdict(list)

    for model_name in filenames:
        assert (len(model_name) == 1)
        wv = KeyedVectors.load(model_name[0])

        # get total similarity between this word and other set
        # shouldn't need to normalize by size of known set because it's
        # the same for all words
        for w in test_set:
            test_to_similarity[w].append(get_similarity(w, known_set, wv))

    if not econ_seq:
        return test_to_similarity
    words_and_corrs = []
    for w in test_to_similarity:
        corr = get_corr(difference(test_to_similarity[w]), econ_seq)
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
def e_step(filenames, countries, vocab, lexicon_size, econ_seq):
    words_and_corrs = step_helper(filenames, known_set=countries, test_set=vocab, econ_seq=econ_seq)
    words_and_corrs.sort(key=lambda x: x[1], reverse=True)

    # return the words with the highest correlation
    # TODO: (or lowest correlation if we've flipped the sign)
#    return [w for w in words_and_corrs[:lexicon_size]]
    return [w for w in words_and_corrs[-lexicon_size:]], [w for w in words_and_corrs[:lexicon_size]]

# Assume we know the lexicon of meaningful words. For every country, calculate
# similarity correlation with lexicon. Return all countries with a positive
# correlation (or negative if we're flipping the sign)
def m_step(model_path, lexicon, all_countries, econ_seq, sign = 1):
    words_and_corrs = step_helper(model_path, known_set=lexicon, test_set=all_countries, econ_seq=econ_seq)

    words_and_corrs.sort(key=lambda x: x[1], reverse=True)

    # return the words with positive correlation
    # TODO: (or negative correlation if we've flipped the sign)
    return [w[0] for w in words_and_corrs if w[1] > 0]


country_set = None
def is_not_country_name(keyword):
    global country_set
    if not country_set:
        lines = open("../russian_ner/cleaned.txt").readlines()
        country_set = set([l.split(",")[0].strip() for l in lines])
    return keyword not in country_set

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", default="/usr1/home/anjalief/russian_model_cache")
    parser.add_argument("--keywords", default="/usr1/home/anjalief/corpora/russian/us_countries.txt")
    parser.add_argument("--econ_file", default="/usr1/home/anjalief/corpora/russian/russian_monthly_gdp.csv")
    parser.add_argument('--timestep', type=str,
                        default='monthly',
                        choices=['monthly', 'quarterly', 'yearly'])
    parser.add_argument("--lexicon_size", type=int, default=100)
    args = parser.parse_args()

    # FIRST: Gather inputs. Start with keywords, datelist, and vocab words from model
    keywords = set(load_file(args.keywords))

    # only pull vocab words that appear in first model. They (and only they) should appear in all models
    model_name1 = get_model_filename(args.model_path, YEARS[0], MONTHS[0], args.timestep)
    vocab = KeyedVectors.load(model_name1).index2entity
    print(len(vocab))

    # skip countries that are not in vocab
    # for k in keywords:
    #     if not k in vocab:
    #         print ("MISSING COUNTRY", k)
    # keywords = [k for k in keywords if k in vocab]


    # Shrink vocab to only adjectives
#    vocab = list(filter(is_adjective, vocab))

    base_model = KeyedVectors.load("/usr1/home/anjalief/word_embed_cache/ner_model_cache/izvestia_yearly/2003_1_yearly.pickle")
    vocab = [x[0] for x in base_model.most_similar(positive=keywords, topn=10000)]
    vocab = list(filter(is_not_country_name, vocab))
#    vocab = list(filter(is_adjective, vocab))

    print(len(vocab))

    date_seq, filenames = get_files_by_time_slice(
        args.model_path, args.timestep, suffix= "_" + args.timestep + ".pickle")
    econ_seq = load_econ_file(args.econ_file, args.timestep, date_seq)
    econ_seq = difference(econ_seq)


    print ("DONE DATA LOADING")

    lexicon1,lexicon2 = e_step(filenames, keywords, vocab, args.lexicon_size, econ_seq)
    # fp = open("adj_lex.out", "w")

    for x in lexicon1:
        print (x[0] + " " + str(x[1]))
    print("\n****************************************************************************************\n")

    for x in lexicon2:
        print (x[0] + " " + str(x[1]))

if __name__ == "__main__":
    main()
