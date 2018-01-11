#!/usr/bin/env python3
# Pull a random sample of NUM_SAMPLE articles
# If a label file exitsts, labels are split with the article samples
# If a country file is given, only include articles that contain
# country names

from article_utils import LoadArticles
from article_utils import NEW_ARTICLE_TOKEN
from baseline_country import get_countries, contains_country

import argparse
import random
import io
import glob

NUM_SAMPLE = 100

def write_article(a_fp, l_fp, a, l):
    a_fp.write(NEW_ARTICLE_TOKEN + "\n")
    a_fp.write(a + "\n\n")

    l_fp.write(str(l).strip() + "\n")

def meets_criteria(article):

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--article_glob')
    parser.add_argument('--tune_file_name')
    parser.add_argument('--test_file_name')
    parser.add_argument('--country_list')
    parser.add_argument('--label_file_exists', action='store_true')
    args = parser.parse_args()

    articles, article_index = LoadArticles(args.article_glob)
    # if the articles are already labeled, then we split the labels
    # as we split the articles (i.e. instead of the article number)
    if args.label_file_exists:
        labels = []
        for filename in glob.iglob(args.article_glob):
            l = open(filename + ".labels").readlines()
            labels += l
        article_index = labels

    # if we've given a country list, we only keep articles that have
    # a country name in them
    if args.country_list:
        new_articles = []
        new_article_index = []
        countries = get_countries(args.country_list)
        for a,i in zip(articles, article_index):
            if contains_country(a.split(), countries):
                new_articles.append(a)
                new_article_index.append(i)
        articles = new_articles
        article_index = new_article_index

    print len(articles), len(article_index)

    # choose 100 random articles as tuning and 100 as test
    ran = random.sample(zip(articles, article_index), NUM_SAMPLE * 2)
    tune_a_fp = open(args.tune_file_name, 'w+')
    tune_l_fp = open(args.tune_file_name + ".labels", 'w+')
    test_a_fp = open(args.test_file_name, 'w+')
    test_l_fp = open(args.test_file_name + ".labels", 'w+')

    count = 0
    for i in ran:
        if (count < NUM_SAMPLE):
            write_article(tune_a_fp, tune_l_fp, i[0], i[1])
        else:
           write_article(test_a_fp, test_l_fp, i[0], i[1])
        count += 1

if __name__ == '__main__':
  main()
