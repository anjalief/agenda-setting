#!/usr/bin/env python
# Do some basic preprocessing
# lemmatize all words, remove words that appear
# in < 0.5% of articles or in > 99.5% of documents

from nltk.stem.porter import PorterStemmer
from article_utils import LoadArticles
from collections import Counter
from article_utils import NEW_ARTICLE_TOKEN
import argparse
import os, sys

porter_stemmer = PorterStemmer()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--article_glob')
    parser.add_argument('--output_dir')
    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    articles, article_index = LoadArticles(args.article_glob)
    word_counts = Counter()

    # first pass, we stem everything and collect word counts
    for i in range(0, len(articles)):
        words = articles[i].split()
        new_words = [porter_stemmer.stem(w.decode('utf-8')) for w in words]
        word_counts.update(set(new_words))  # we just want the count of how many articles each word occurs in
        articles[i] = ' '.join(new_words)


    # exclude any words that are too common or too uncommon
    min_thresh = 0.005 * len(articles)  # .5%
    max_thresh = .995 * len(articles)   # 99.5%
    print min_thresh, max_thresh
    exclude = set()
    for c in word_counts:
        if word_counts[c] < min_thresh or word_counts[c] > max_thresh:
            exclude.add(c)

    for e in exclude:
        print e.encode('utf-8')
    # second pass, we eliminate any words that we need to
    # and write articles
    for a,i in zip(articles, article_index):

        # cut exclude words
        words = a.split()
        new_words = [w.encode('utf-8') for w in words if not w in exclude]

        # build path to output file
        dirname = os.path.dirname(i[0])
        filename = os.path.basename(i[0])
        base_dirname = os.path.basename(dirname)

        topic_outdir = args.output_dir + "/" + base_dirname
        if not os.path.exists(topic_outdir):
            os.makedirs(topic_outdir)

        full_path = topic_outdir + "/" + filename

        # write article
        fp = open(full_path, 'a+')
        fp.write(NEW_ARTICLE_TOKEN + "\n")
        fp.write(" ".join(new_words) + "\n\n")
        fp.close()

if __name__ == '__main__':
    main()
