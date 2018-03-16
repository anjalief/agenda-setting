#!/usr/bin/env python

# Pull a random sample of NUM_SAMPLE articles
# If a label file exists, labels are split with the article samples
# If a country file is given, only include articles that contain
# country names

from article_utils import LoadArticles
from article_utils import NEW_ARTICLE_TOKEN
from baseline_country import get_countries, contains_country
from russian_stemmer import country_russian_stemmer
from russian_ner import texterra_count_countries

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

# "include" is the filter function. It must return a count and set
# the count is # of country mentions in article, the set
# is extra text to attach to the labels (i.e. country list)
def filter_articles(articles, article_index, include_article):
    new_articles = []
    new_article_index = []
    for a,i in zip(articles, article_index):
        include, countries = include_article(a)
        if include >= 2:
            new_articles.append(a)
            text = " ".join(set(countries))
            new_article_index.append((str(i[0]), str(i[1]), text))
    return new_articles, new_article_index

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--article_glob')
    parser.add_argument('--file_name')
    parser.add_argument('--num_samples', type=int)
    parser.add_argument('--sample_size', type=int)
    # if we're filtering, it can take forever. Instead, we downsample to
    # some multiple of how many articles we actually need, then filter those,
    # then sample again from the filtered set. This saves us from
    # running the filtering on tons of articles
    parser.add_argument('--downsample', type=int)
    parser.add_argument('--country_list')
    parser.add_argument('--russian_ner', action='store_true')
    parser.add_argument('--label_file_exists', action='store_true')
    parser.add_argument('--merge_labels', action='store_true')
    args = parser.parse_args()

    articles, article_index = LoadArticles(args.article_glob)

    # see above note on pre-sampling
    if args.downsample:
        # we zip, downsample, and unzip
        articles, article_index = zip(*random.sample(list(zip(articles, article_index)),
                                                     args.sample_size * args.num_samples * args.downsample))
        print ("DOWNSAMPLE", len(articles), len(article_index))

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
        stemmer = country_russian_stemmer()
        countries = get_countries(args.country_list, stemmer)
        # We need this wrappers because the filter functions take different arguments
        def include_by_country(a):
            return contains_country(a.split(), countries, stemmer)
        articles, article_index = filter_articles(articles, article_index, include_by_country)

    # probably not going to ever filter by both things so we can do a second pass
    if args.russian_ner:
        articles, article_index = filter_articles(articles, article_index, texterra_count_countries)


    # choose sample_size random articles
    print ("POST FILTER", len(articles), len(article_index))
    ran = random.sample(list(zip(articles, article_index)), args.sample_size * args.num_samples)
    index = 0
    for i in range(0, args.num_samples):
        articles_fp = open(args.file_name + str(i), 'w+')
        labels_fp = open(args.file_name + str(i) + ".labels", 'w+')

        for i in range(0, args.sample_size):
            write_article(articles_fp, labels_fp, ran[index][0], ran[index][1], args.merge_labels)
            index += 1
        articles_fp.close()
        labels_fp.close()
    print ("DONE", args.article_glob)

if __name__ == '__main__':
  main()
