#!/usr/bin/env python

# Pull a random sample of NUM_SAMPLE articles
# If a label file exists, labels are split with the article samples
# If a country file is given, only include articles that contain
# country names

from article_utils import LoadArticles
from article_utils import NEW_ARTICLE_TOKEN
from baseline_country import get_countries, contains_country
from russian_stemmer import country_russian_stemmer

import argparse
import random
import io
import glob

def write_article(a_fp, l_fp, a, l, merge_labels):
    if merge_labels:
        a_fp.write(str(l).strip() + "\n")
    a_fp.write(NEW_ARTICLE_TOKEN + "\n")
    a_fp.write(a + "\n")
    a_fp.write("COUNTRIES IDENTIFIED: " + l[2] + "\n\n")

    if not merge_labels:
        l_fp.write(",".join(l[0:2]) + "\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--article_glob')
    parser.add_argument('--file_name')
    parser.add_argument('--num_samples')
    parser.add_argument('--sample_size')
    parser.add_argument('--country_list')
    parser.add_argument('--label_file_exists', action='store_true')
    parser.add_argument('--merge_labels', action='store_true')
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
        stemmer = country_russian_stemmer()
        countries = get_countries(args.country_list, stemmer)
        for a,i in zip(articles, article_index):
            contains, country_list = contains_country(a.split(), countries, stemmer)
            if contains >= 2:
                new_articles.append(a)
                text = " ".join(set(country_list))
                new_article_index.append((str(i[0]), str(i[1]), text))
        articles = new_articles
        article_index = new_article_index

    print len(articles), len(article_index)

    # choose 100 random articles as tuning and 100 as test
    ran = random.sample(zip(articles, article_index), int(args.sample_size) * int(args.num_samples))
    index = 0
    for i in range(0, int(args.num_samples)):
        articles_fp = open(args.file_name + str(i), 'w+')
        labels_fp = open(args.file_name + str(i) + ".labels", 'w+')

        for i in range(0, int(args.sample_size)):
            write_article(articles_fp, labels_fp, ran[index][0], ran[index][1], args.merge_labels)
            index += 1
        articles_fp.close()
        labels_fp.close()

if __name__ == '__main__':
  main()
