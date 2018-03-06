#!/usr/bin/env python3
# Take in artcile files and convert them
# to a csv. Intended for input to STM
import argparse
import os
from article_utils import LoadArticles

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--article_glob')
    parser.add_argument('--outfile')
    args = parser.parse_args()

    fp = open(args.outfile, "w")
    headings = ["documents", "date", "outlet"]
    fp.write(",".join(headings))
    fp.write("\n")
    articles,indices = LoadArticles(args.article_glob)
    for a,i in zip(articles, indices):
        # we're making a csv so we don't want commas in the actual text
        # newlines mess up the R csv reader
        a = a.replace(",", "")
        a = a.replace("\n", " ")

        # we want the year/month and the newspaper
        # For russian Need to go one level up, file name is [path]/newspaper/year/file
        # dirname = os.path.dirname(os.path.dirname(i[0]))
        dirname = os.path.dirname(i[0])
        base_dirname = os.path.basename(dirname)
        filename = os.path.basename(i[0])
        # expects filename format to be year_month.txt.tok
        # we're going to call everything the 1st of the month cause R doesn't seem to like
        # dates with just a year/month
        year_month = filename.split('.')[0]
        splits = year_month.split('_')
        fp.write(a + "," + "01/" + splits[1] + "/" + splits[0] + "," + base_dirname + "\n")
    fp.close()

if __name__ == '__main__':
  main()

