#!/usr/bin/env python
from article_utils import LoadArticles, LoadVectors
from collections import Counter

all = "/projects/tir1/users/anjalief/nyt_filtered/*/*.tok"


articles,indices = LoadArticles(all, verbose=False)
print "Loading done"

all_counts = Counter()
business_counts = Counter()

for article, index in zip(articles,indices):
    folder = index[0].split("/")
    words = article.split()
    if folder[len(folder) - 2] == "Business":
        business_counts.update(words)
    else:
        all_counts.update(words)


def write_counts(filename, counts):
    fp = open(filename, 'w')
    for c in counts:
        fp.write(c + " " + str(counts[c]) + "\n")
    fp.close()

write_counts("all_counts.txt", all_counts)
write_counts("business_counts.txt", business_counts)
