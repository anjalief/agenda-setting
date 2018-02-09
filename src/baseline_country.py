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

def get_countries(filename, stemmer = None):
    country_glob = open(filename).read()
    countries = set()
    # in country file, each line contains [country],[capital],[language1],[language2]
    for c in country_glob.split("\n"):
        for i in c.split(","):
            item = i.strip()
            if stemmer:
                item = stemmer.stem(item)
            countries.add(item)
    return countries

def contains_country(words, countries, stemmer = None):
    count_this_article = 0
    l = []

    # figure out if this article mentions another country
    for w in words:
        if stemmer:
            w = stemmer.stem(w)
        if w in countries:
            count_this_article += 1
            l.append(w)

    return count_this_article, l

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
        dirname_to_count = {}
        topic_to_count = {}
        for t in all_topics:
            topic_to_count[t] = (0,0)

        articles, article_index = LoadArticles(args.article_glob)

        for a,i in zip(articles, article_index):
            words = a.split()
            count_this_article = contains_country(words, countries, stemmer)

            dirname = os.path.dirname(i[0])
            base_dirname = os.path.basename(dirname)

            count = dirname_to_count.get(base_dirname, (0, 0))
            dirname_to_count[base_dirname] = (count[0] + count_this_article,
                                              count[1] + 1)

            for t in all_topics:
                if t in base_dirname:
                    count = topic_to_count[t]
                    topic_to_count[t] = (count[0] + count_this_article,
                                         count[1] + 1)

        fp = open("topics_to_count.txt", 'w')
        for t in topic_to_count:
            fp.write(t + " " + str(topic_to_count[t][0]) + " "  + str(topic_to_count[t][1]) + "\n")
        fp.close()

        fp = open("subtopics_to_count.txt", 'w')
        for t in dirname_to_count:
            fp.write(t + " " + str(dirname_to_count[t][0]) + " "  + str(dirname_to_count[t][1]) + "\n")
        fp.close()

    if args.labeled_data:
        tracker = TrackCorrect()
        articles, _ = LoadArticles(args.labeled_data)
        labels = LoadGold(args.labeled_data + ".labels")
        internal_country_count = []
        external_country_count = []
        for a,l in zip(articles, labels):
            i, cl = contains_country(a.split(), countries, stemmer)
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

        precision, recall, accuracy, gold_external, count = tracker.get_stats()
        print precision, recall, accuracy, gold_external, count
        print "EXTERNAL"
        for i in external_country_count:
            print i

        print "INTERNAL"
        for i in internal_country_count:
            print i



if __name__ == '__main__':
  main()
