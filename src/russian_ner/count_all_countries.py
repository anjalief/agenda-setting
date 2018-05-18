
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
from utils import get_corr
import glob
import math
import itertools

# Return number of country name words in timestpe
# Number of articles that mention 1 country
# Number of articles that mention 2 countries
def count_mentions_in_articles(filenames, country_names):
    country_word_count = 0
    total_word_count = 0

    country_article_count = 0
    country_twice_count = 0
    country_thrice_count = 0
    total_article_count = 0
    articles_weighted_by_words = 0
    for filename in filenames:
        articles, _ = LoadArticles(filename)
        total_article_count += len(articles)
        for article in articles:
            countries_in_article = 0

            for w in article.split():
                total_word_count += 1
                if w in country_names:
                    countries_in_article += 1
                    country_word_count += 1
            if countries_in_article > 0:
                country_article_count += 1
            if countries_in_article > 1:
                country_twice_count += 1
                articles_weighted_by_words += len(article.split())
            if countries_in_article > 2:
                country_thrice_count += 1

    return country_article_count, country_twice_count, country_thrice_count, total_article_count, country_word_count, articles_weighted_by_words, total_word_count

def load_country_names(filename):
    names = []
    for line in open(filename).readlines():
        names.append(line.split(",")[0].strip())
    return names

def do_counts(files_grouped_by_date, subs_file):
    country_names = load_country_names(subs_file)

    # number of articles that mention country (normalize by number of articles)
    output_summary = []
    for filename in files_grouped_by_date:
        output_summary.append(count_mentions_in_articles(filename, country_names))
    return output_summary

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', help="this guy needs a trailing backslash")
    parser.add_argument('--subs_file', default="./external.txt")
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
    output = do_counts(filenames, args.subs_file)

    assert(len(output) == len(date_seq))
    for d,o in zip(date_seq, output):
        # print (d,o[0], o[1], o[2], o[3], o[4], o[5], o[6])
        print (o[5], o[6])

if __name__ == "__main__":
    main()
