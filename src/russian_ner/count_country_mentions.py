
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from replace_country_mentions import parse_subs_file
from collections import defaultdict
import os
import sys
from datetime import date
import pickle
sys.path.append("..")
sys.path.append("../diachronic_embeddings")
from article_utils import *
from econ_utils import *

import glob
import math
import itertools

def count_mentions_in_articles(filenames, country_names):
    country_to_count = {}
    country_to_article_count = {}
    for c in country_names:
        country_to_count[c] = 0
        country_to_article_count[c] = 0

    total_word_count = 0
    total_article_count = 0
    for filename in filenames:
        articles, _ = LoadArticles(filename)
        total_article_count += len(articles)
        for article in articles:
            countries_in_article = set()

            for w in article.split():
                total_word_count += 1
                if w in country_to_count:
                    country_to_count[w] += 1
                    countries_in_article.add(w)

            for c in countries_in_article:
                country_to_article_count[c] += 1

    return country_to_count, country_to_article_count, total_word_count, total_article_count

def load_country_names(filename):
    names = []
    for line in open(filename).readlines():
        names.append(line.split(",")[0].strip())
    return names

def do_counts(files_grouped_by_date, subs_file):
    country_names = load_country_names(subs_file)

    # number of articles that mention country (normalize by number of articles)
    country_to_article_sequence = defaultdict(list)

    # number of country mentions (normalize by word count)
    country_to_word_sequence = defaultdict(list)

    for filename in files_grouped_by_date:
        country_to_count, country_to_article_count, word_count, article_count = count_mentions_in_articles(filename, country_names)

        for c in country_names:
            country_to_article_sequence[c].append((country_to_article_count[c], float(article_count)))
            country_to_word_sequence[c].append((country_to_count[c], float(word_count)))

    return country_to_article_sequence, country_to_word_sequence


def get_corr_for_list(country_list, country_to_word_sequence, econ_seq, verbose=False):
    summed_seq = []
    for country in country_list:
        country_frequencies = country_to_word_sequence[country]
        if summed_seq == []:
            summed_seq = country_frequencies
        else:
            new_seq = []
            for x,y in zip(country_frequencies, summed_seq):
                new_seq.append(x + y)
            summed_seq = new_seq
    # summed_seq = average_interval(summed_seq)
    # econ_seq = average_interval(econ_seq)
    if verbose:
        for x,y in zip(econ_seq, summed_seq):
            print (x, y)
    return get_corr(summed_seq, econ_seq)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', help="this guy needs a trailing backslash")
    parser.add_argument('--subs_file', default="./cleaned.txt")
    # if we specify this, we just compute correlations for all countries in the list
    parser.add_argument('--country_list_file')
    parser.add_argument('--timestep', type=str,
                        default='monthly',
                        choices=['monthly', 'quarterly', 'yearly'])
    parser.add_argument('--refresh', action='store_true')
    parser.add_argument("--econ_file", default="/usr1/home/anjalief/corpora/russian/russian_monthly_gdp.csv")
#    parser.add_argument("--rtsi_file", default="/usr1/home/anjalief/corpora/russian/russian_rtsi_rub.csv")
    args = parser.parse_args()

    date_seq, filenames = get_files_by_time_slice(args.input_path, args.timestep)

    # econ_seq = load_econ_file(args.econ_file, args.timestep, date_seq)
    # for d,e in zip(date_seq, econ_seq):
    #     print(d, e)
    # return

    tag = os.path.basename(os.path.dirname(args.input_path)).replace("*", "m") + "_"

    cache_filename1 = os.path.join("cache", tag + args.timestep +  "_article.pickle")
    cache_filename2 = os.path.join("cache", tag + args.timestep + "_word.pickle")

    # if one exists they should both exist
    if os.path.isfile(cache_filename1) and not args.refresh:
        country_to_article_sequence = pickle.load(open(cache_filename1, "rb"))
        country_to_word_sequence = pickle.load(open(cache_filename2, "rb"))
    else:
        country_to_article_sequence, country_to_word_sequence = do_counts(filenames, args.subs_file)
        pickle.dump(country_to_article_sequence, open(cache_filename1, "wb"))
        pickle.dump(country_to_word_sequence, open(cache_filename2, "wb"))


    if not args.timestep in args.econ_file:
        print ("WARNING TIMESTEP DOES NOT MATCH ECON FILE")

#    econ_seq = load_econ_file(args.econ_file, args.timestep, date_seq)
    # assert (len(econ_seq) == len(date_seq)), str(len(econ_seq)) + " " + str(len(date_seq))


    if args.country_list_file:
        countries = [c.strip() for c in open(args.country_list_file).readlines()]
        corr = get_corr_for_list(countries, country_to_word_sequence, econ_seq, True)
        print(corr)
        return

        for list_size in [10, 20, 50, 100]:
            min_corr = 0
            best_set = None
            for country_set in itertools.combinations(countries, list_size):
                print (country_set)
                corr = get_corr_for_list(country_set, country_to_word_sequence, econ_seq, False)
                if corr < min_corr:
                    min_corr = corr
                    best_set = country_set
            print (list_size, min_corr)
            for c in best_set:
                print (c)
            get_corr_for_list(best_set, country_to_word_sequence, econ_seq, True)
            print("***********************************************************")
        return

    # country_to_sum = []
    # for k in country_to_article_sequence:
    #     country_to_sum.append((k, sum(country_to_article_sequence[k])))
    # country_to_sum.sort(key=lambda x: x[1], reverse=True)
    # for x in country_to_sum:
    #     print (x)
    # return

    # FLIP HERE
#    USA_seq = country_to_word_sequence["USA"]
    USA_seq = country_to_article_sequence["USA"]


#    print (len(date_seq), len(USA_seq), len(econ_seq))

    # USA_seq = difference(USA_seq)
    # econ_seq = difference(econ_seq)

#    print (len(USA_seq), len(econ_seq))
    for d,y in zip(date_seq, country_to_article_sequence["USA"]):
       print (d, y)

    print("**************************")

    for d,y in zip(date_seq, country_to_word_sequence["USA"]):
       print (d, y)
    # print ("**************************************************************************")
    # print ("**************************************************************************")
    # for d,y in zip(date_seq, country_to_word_sequence["USA"]):
    #    print (d, y[0], y[1])
    # print("")
#    print (get_corr(USA_seq, econ_seq))
    # print("")

    # corrs = []
    # for k in country_to_article_sequence:
    #     corr = get_corr(country_to_article_sequence[k], econ_seq)
    #     corrs.append((corr,k))

    # # NANs screw up sorting
    # new_corrs = []
    # for x in corrs:
    #     if math.isnan(x[0]):
    #         print ("NAN error on ", x)
    #     else:
    #         new_corrs.append(x)
    # corrs = new_corrs

    # corrs.sort(key=lambda x: x[0])

    # print ("TOP")
    # for t in corrs[:10]:
    #     print (t)
    # print ()
    # print ("BOTTOM")
    # for t in corrs[-10:]:
    #     print (t)


if __name__ == "__main__":
    main()
