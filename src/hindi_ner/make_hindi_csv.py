#!/usr/bin/env python3
# Take in artcile files and convert them
# to a csv. Intended for input to STM
# nohup python make_hindi_csv.py --outfile="hindi_downsample3.csv" --article_glob "/usr1/home/anjalief/corpora/hindi/*/*/*" --downsample .25 >> err2.out &
# nohup python make_hindi_csv.py --outfile="hindi_downsample2.csv" --article_glob "/usr1/home/anjalief/corpora/hindi/*/*/*" --downsample .5 >> err2.out &

import argparse
import os, sys
from hindi_article_utils import ArticleIter
import random
import nltk

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--article_glob')
    parser.add_argument('--outfile')
    # percentage of the data that we want to keep
    parser.add_argument('--downsample', type=float)
    args = parser.parse_args()

    fp = open(args.outfile, "w")
    headings = ["documents", "date", "outlet"]
    fp.write(",".join(headings))
    fp.write("\n")

    for date, outlet, articles in ArticleIter(args.article_glob):
        # We actually just need to pull all articles because we're going to downsample
        if args.downsample:
            texts = []
            for a in articles:
                # skip bad stuff, need to add this in for non-downsampled too
                if a['body'].startswith("ERR-RTFGet latest news & live updates"):
                    continue
                texts.append(a)
            # it's annoying but I think it's probably faster to
            # iterate through all documents twice than to tokenize before
            # we downsample
            num_keep = int(args.downsample * len(texts))
            articles = random.sample(texts, num_keep)

        # eventually we probably want to cache tokenized versions of all articles
        for a in articles:
            text = nltk.tokenize.word_tokenize(a['body'])

            # we're making a csv so we don't want commas in the actual text
            # newlines mess up the R csv reader
            text = [t.replace(",","").replace("\n","").replace("\r", "") for t in text]
            fp.write(" ".join(text).encode('utf-8') + "," + date.strftime('%m/%d/%Y') + "," + outlet + "\n")

    fp.close()

if __name__ == '__main__':
  main()

