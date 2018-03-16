#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Baseline metric, count an article as external if it contains a
# word from a list of countries
# create two output files, one that's generic topic -> article counts,
# other is exact topic -> article counts (# external, total number)
from article_utils import LoadArticles, all_topics
import argparse
import os
from eval_utils import TrackCorrect, LoadGold
from russian_stemmer import country_russian_stemmer
from russian_stemmer import country_english_stemmer
from country_utils import get_countries, contains_country
from russian_ner import texterra_count_countries

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--article_glob')
    parser.add_argument('--country_list')
    parser.add_argument('--labeled_data')
    parser.add_argument('--lemmatize_russian', action='store_true')
    args = parser.parse_args()

    stemmer = None
    if args.lemmatize_russian:
        stemmer = country_russian_stemmer()
    countries = get_countries(args.country_list, stemmer)

    if args.article_glob:
        article_to_count = {}

        articles, article_index = LoadArticles(args.article_glob)

        for a,i in zip(articles, article_index):
            words = a.split()
            count_this_article, _ = contains_country(words, countries, stemmer)
            count = 0
            if count_this_article >= 2:
                count = 1

            tup = article_to_count.get(i[0], (0,0))
            article_to_count[i[0]] = (tup[0] + count, tup[1] + 1)

        fp = open("article_to_count.txt", 'w')
        for t in article_to_count:
            fp.write(t + " " + str(article_to_count[t][0]) + " "  + str(article_to_count[t][1]) + "\n")
        fp.close()

    if args.labeled_data:
        tracker = TrackCorrect()
        articles, _ = LoadArticles(args.labeled_data)
        labels = LoadGold(args.labeled_data + ".labels")
        internal_country_count = []
        external_country_count = []
        for a,l in zip(articles, labels):
            i, cl = texterra_count_countries(a)
            tracker.update(l.is_external, i >= 2)

            # count number of countries per article
            if l.is_external:
                external_country_count.append(i)
            else:
                internal_country_count.append(i)
            if not i and l.is_external:
                fp = open("false_negatives.txt", 'a+')
                fp.write(a)
                fp.write("\n******************* ")
                for c in cl:
                    fp.write(c + " ")
                fp.write("\n\n")
                fp.close()
            elif i >= 2 and not l.is_external:
                print (a, "\n")
                print (cl, "\n\n\n")

        precision, recall, accuracy, gold_external, count = tracker.get_stats()
        print (precision, recall, accuracy, gold_external, count)
        print ("EXTERNAL")
        for i in external_country_count:
            print (i)

        print ("INTERNAL")
        for i in internal_country_count:
            print (i)



if __name__ == '__main__':
  main()
