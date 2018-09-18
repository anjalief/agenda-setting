#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from collections import defaultdict, Counter
import os
import sys
sys.path.append("..")
from datetime import date
import pickle
from article_utils import *
from econ_utils import *
import glob
import math
import itertools

# Return number of country name words in timestep
# Number of articles that mention 1 country
# Number of articles that mention 2 countries
def count_mentions_in_articles(filenames, keywords):
    keyword_to_count = defaultdict(int)
    total_word_count = 0

    for filename in filenames:
        articles, _ = LoadArticles(filename, verbose=False)
        for article in articles:
            counter = Counter(article.lower().split())

            if counter["usa"] < 2:
                continue

            total_word_count += sum([counter[q] for q in counter])
            for c in keywords:
                keyword_to_count[c] += counter[c]
    return keyword_to_count, total_word_count

def load_country_names(filename):
    names = []
    for line in open(filename).readlines():
        names.append(line.split(",")[0].strip().lower())
    return names

def do_counts(files_grouped_by_date, subs_file):
    keywords = load_country_names(subs_file)

    # number of articles that mention country (normalize by number of articles)
    keyword_to_summary = defaultdict(list)
    for filename in files_grouped_by_date:
        keyword_to_count, total_word_count = count_mentions_in_articles(filename, keywords)
        for k in keyword_to_count:
            keyword_to_summary[k].append(keyword_to_count[k] / total_word_count)
    return keyword_to_summary

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', help="Directory where data files are. Must include trailing backslash", default="../data/Izvestiia_processed/")
    parser.add_argument('--subs_file', help="File containing keywords to count", default="../data/usa.txt")
    parser.add_argument('--timestep', type=str, help="specify what time increment to use for aggregating articles",
                        default='monthly',
                        choices=['monthly', 'quarterly', 'semi', 'yearly'])
    parser.add_argument("--econ_file", help="If you specify this, output will include compute correlation of counts with econ series (does NOT work for yearly)")
    args = parser.parse_args()

    date_seq, filenames = get_files_by_time_slice(args.input_path, args.timestep)
    keyword_to_summary = do_counts(filenames, args.subs_file)

    keyword_to_corr = {}
    econ_seq = load_econ_file(args.econ_file, args.timestep, date_seq)

    for k in keyword_to_summary:
        assert(len(keyword_to_summary[k]) == len(date_seq))

        keyword_to_corr[k] = get_corr(econ_seq, keyword_to_summary[k])

    for k in sorted(keyword_to_corr, key=keyword_to_corr.get):
        print(k, keyword_to_corr[k])

if __name__ == "__main__":
    main()
