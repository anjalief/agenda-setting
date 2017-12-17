#!/usr/bin/env python3

from article_utils import LoadArticles
from article_utils import NEW_ARTICLE_TOKEN

import argparse
import random
import io

NUM_SAMPLE = 100

def write_article(a_fp, l_fp, a, l):
    a_fp.write(NEW_ARTICLE_TOKEN + "\n")
    a_fp.write(a + "\n\n")

    l_fp.write(str(l) + "\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--article_glob')
    parser.add_argument('--tune_file_name')
    parser.add_argument('--test_file_name')
    args = parser.parse_args()

    articles, article_index = LoadArticles(args.article_glob)

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
