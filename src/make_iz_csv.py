#!/usr/bin/env python3
# Take in artcile files and convert them
# to a csv. Intended for input to STM
import argparse
import os
from article_utils import LoadArticles
from collections import Counter

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--article_glob')
    parser.add_argument('--outfile')
    args = parser.parse_args()

    fp = open(args.outfile, "w")
    headings = ["documents", "date"]
    fp.write(",".join(headings))
    fp.write("\n")
    articles,indices = LoadArticles(args.article_glob)
    for a,i in zip(articles, indices):

        counter = Counter(a.split())

        # Only run on US focused news
        if counter["USA"] < 2:
            continue

        # can probably get better topics with some better preprocessing

        # we're making a csv so we don't want commas in the actual text
        # newlines mess up the R csv reader
        a = a.replace(",", "")
        a = a.replace("\n", " ")

        # we want the year/month
        filename = os.path.basename(i[0])

        # expects filename format to be year_month.txt.tok
        # we're going to call everything the 1st of the month cause R doesn't seem to like
        # dates with just a year/month
        year_month = filename.split('.')[0]
        splits = year_month.split('_')
        fp.write(a + "," + "01/" + splits[1] + "/" + splits[0] + "\n")
    fp.close()

if __name__ == '__main__':
  main()

