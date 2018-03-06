# for when we want to merge 2007 and 2009 samples

from article_utils import LoadArticles
from article_utils import NEW_ARTICLE_TOKEN

import argparse
import random
import io
import glob

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file1')
    parser.add_argument('--file2')
    parser.add_argument('--outfile')
    parser.add_argument('--shortestn', type=int)
    args = parser.parse_args()


    articles1, _ = LoadArticles(args.file1)
    labels1 = [l.strip() for l in open(args.file1 + ".labels").readlines()]
    set1 = zip(articles1, labels1)

    articles2, _ = LoadArticles(args.file2)
    labels2 = [l.strip() for l in open(args.file2 + ".labels").readlines()]
    set2 = zip(articles2, labels2)

    # if shortest n, we only want to keep the shortest n articles from each set
    if args.shortestn:
        set1.sort(key=lambda x: len(x[0]))
        set2.sort(key=lambda x: len(x[0]))
        merged_set = set1[:args.shortestn] + set2[:args.shortestn]
    else:
        merged_set = set1 + set2
    random.shuffle(merged_set)

    fp = open(args.outfile, "w")
    fp_labels = open(args.outfile + ".labels", "w")

    for a, i in merged_set:
        fp.write(NEW_ARTICLE_TOKEN + "\n")
        fp.write(a + "\n\n")
        fp_labels.write(i + "\n")

if __name__ == "__main__":
    main()
