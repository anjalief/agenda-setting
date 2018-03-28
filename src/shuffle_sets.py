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
    parser.add_argument('--filenum', type=int, default=1)
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

    # split the samples into specified number of files
    num_per_file = len(merged_set) / args.filenum
    for i in range(1, args.filenum + 1):
        filename = args.outfile + "_part_" + str(i)
        fp = open(filename, "w")
        fp_labels = open(filename + ".labels", "w")
        for j in range((i - 1) * num_per_file, i * num_per_file):
            fp.write(NEW_ARTICLE_TOKEN + "\n")
            fp.write(merged_set[j][0] + "\n\n")
            fp_labels.write(merged_set[j][1] + "\n")
        fp.close()

if __name__ == "__main__":
    main()
