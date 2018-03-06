#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Script to count the number of "external" articles
#  in a set of files, where external articles are
# defined using the baseline: 2 mentions of a country
# Intended for russia data set
from article_utils import LoadArticles, all_topics
import argparse
import os
from russian_stemmer import country_russian_stemmer, country_english_stemmer
from baseline_country import get_countries, contains_country
import glob
from collections import defaultdict
from nltk.stem.snowball import RussianStemmer, EnglishStemmer

def pretty_format(outfile):
    newspaper_to_articles = {}
    lines = open(outfile).readlines()
    for line in lines:
        parts = line.split()
        dir = parts[0].split("/")
        newspaper = dir[6]

        # find monthly
        if "_" in dir[8]:
            dates = dir[8].split("_")
            date = dates[0] + "/" + dates[1].split('.')[0]
            key = newspaper + "_monthly"
            l = newspaper_to_articles.get(key, [])
            l.append(date + " " + parts[1] + " " + parts[2])
            newspaper_to_articles[key] = l
        else:
            date = dir[7]
            key = newspaper + "_yearly"
            l = newspaper_to_articles.get(key, [])
            l.append(date + " " + parts[1] + " " + parts[2])
            newspaper_to_articles[key] = l

        for key in newspaper_to_articles:
            fp = open(key + ".txt", "w")
            for a in newspaper_to_articles[key]:
                fp.write(a + "\n")
            fp.close()

def do_russian(args):
    # stemmer = country_russian_stemmer() # TO UNDO
    stemmer = country_russian_stemmer()

    # count number of external articles in each file
    if args.article_glob:
        fp = open(args.outfile, "w")
        countries = get_countries(args.country_list, stemmer)
        for filename in glob.iglob(args.article_glob):
            external_count = 0
            articles, _ = LoadArticles(filename)
            word_count = 0
            for a in articles:
                s = a.split()
                i, _ = contains_country(s, countries, stemmer)
                # NOTE NEED TO UNDO THIS LATER. RIGHT NOW DOING THIS TO COUNT SENTIMENT
#                if i >= 2:
#                    external_count += 1
                external_count += i
                word_count += len(s)
                # TO UNDO, SHOULD BE LEN(ARTICLES) INSTEAD OF WORD_COUNT
            fp.write("%s %d %d\n" % (filename, external_count, word_count))
        fp.close()
    if args.reformat:
        pretty_format(args.outfile)

def do_english(args):
    stemmer = country_english_stemmer()

    # count number of external articles in each file
    if args.article_glob:
        countries = get_countries(args.country_list, stemmer)
        print countries
        month_year_to_count = defaultdict(int)
        month_year_to_external = defaultdict(int)
        for filename in glob.iglob(args.article_glob):
            if "Correction" in filename:
                continue
            basename = os.path.basename(filename).split('.')[0]
            articles, _ = LoadArticles(filename)
            for a in articles:
                i, _ = contains_country(a.split(), countries)
                if i >= 2:
                    month_year_to_external[basename] += 1
                month_year_to_count[basename] += 1
        fp = open(args.outfile, "w")
        print month_year_to_count
        for v in month_year_to_count:
            fp.write("%s %d %d\n" % (v, month_year_to_external[v], month_year_to_count[v]))
        fp.close()
    if args.reformat:
        pretty_format(args.outfile)


def main():
    print "START"
    parser = argparse.ArgumentParser()
    parser.add_argument('--article_glob')
    parser.add_argument('--country_list')
    parser.add_argument('--outfile')
    parser.add_argument('--reformat', action='store_true')
    args = parser.parse_args()

# it's easier to just flip these as needed
    do_russian(args)
#    do_english(args)

if __name__ == '__main__':
    main()
