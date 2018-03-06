#!/usr/bin/env python

import argparse
import csv
import itertools
# from article_utils import NEW_ARTICLE_TOKEN
NEW_ARTICLE_TOKEN="NEW - ARTICLE - TOKEN"

# Hard code indices
ExternalEvents=0
RussianEconomy=1
ExternalEconomy=2
ActiveBlaming=3
Globalizing=4
Mitigating=5
OtherComments=6
NCOL=6

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv1')
    parser.add_argument('--csv2')
    args = parser.parse_args()


    fp1 = open(args.csv1)
    reader1 = csv.reader(fp1, delimiter=',')
    fp2 = open(args.csv2)
    reader2 = csv.reader(fp2, delimiter=',')

    # Number of each annotation
    count1 = 0
    count2 = 0
    raw_count1 = [0] * NCOL
    raw_count2 = [0] * NCOL

    # Percent of exact matches between annotators
    exact_match = [0] * NCOL

    # Percent where both marked same way (ignoring sentiment)
    both_marked = [0] * NCOL

    # Percent where both marked relevant (ignoring sentiment)
    both_marked_relevant = [0] * NCOL

    # Where both marked, percent where sentiment matches for external
    # for russian economy
    # for external economy
    matched_sentiment = [0] * NCOL



    for row1,row2 in itertools.izip_longest(reader1, reader2):
        if row1 and row1[7] == NEW_ARTICLE_TOKEN:
            count1 += 1
            for i in range(0,NCOL):
                raw_count1[i] += bool(row1[i])
        if row2 and row2[7] == NEW_ARTICLE_TOKEN:
            count2 += 1
            for i in range(0,NCOL):
                raw_count2[i] += bool(row2[i])
#        if row1[7] == NEW_ARTICLE_TOKEN and row2:
#        print row1, row2
#            print row1[0], row2[0], row1[0] == row2[0]

        if row1 and row2 and row1[7] == NEW_ARTICLE_TOKEN:
            assert(row2[7] == NEW_ARTICLE_TOKEN), row2[7]
            for i in range(0,NCOL):
                exact_match[i] += (row1[i] == row2[i])
                both_marked[i] += (bool(row1[i]) == bool(row2[i]))
                both_marked_relevant[i] += bool(row1[i] and row2[i])
                if row1[i] and row2[i]:
                    matched_sentiment[i] += (row1[i] == row2[i])

    def pretty_print(row):
        # make columns of with 10
        for i in row:
            print "%3.3f          " % i,
        print ""
    print "NUMBER ANNOTATED", count1, count2
    pretty_print(raw_count1)
    pretty_print(raw_count2)
    pretty_print(exact_match)
    pretty_print(both_marked)
    pretty_print(both_marked_relevant)
    pretty_print(matched_sentiment)
    print reader1.line_num, reader2.line_num
#    for row in reader


if __name__ == '__main__':
    main()
