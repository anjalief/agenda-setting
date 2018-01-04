#!/usr/bin/env python
# Output counts of external articles, sorted by topic and by combined topics
# Sort by topic will have duplicates (i.e. TechnologyBooks counts as Technology and Books)

import argparse
import glob, os
from article_utils import LoadArticles, LoadVectors, Similarity, GetSimilarArticles

parser = argparse.ArgumentParser()
parser.add_argument('--gold_vectors',
    default="../focused_crawl/external_policy.txt.tok.lda")
parser.add_argument('--per_month_glob')
parser.add_argument('--similarity_threshold', type=float)
parser.add_argument('--log_file',
    default="./summary_")
args = parser.parse_args()

# This should cover all the topics, since these are the topics we kept
# when we filtered the data

all_topics = [ "Arts",
               "RealEstate",
               "Travel",
               "Sports",
               "HomeandGarden",
               "Food",
               "Business",
               "Automobiles",
               "DiningandWine",
               "Movies",
               "Obituaries",
               "JobMarket",
               "World",
               "Theater",
               "DiningWine",
               "Science",
               "Style",
               "YourMoney",
               "Autos",
               "Washington",
               "US",
               "Books",
               "Health",
               "Education",
               "Technology"
               ]

def main():
    gold_vector = LoadVectors(args.gold_vectors)[0]

    dirname_to_count = {}
    topic_to_count = {}
    for t in all_topics:
        topic_to_count[t] = (0,0)

    for filename in glob.iglob(args.per_month_glob):
        dirname = os.path.dirname(filename)
        base_dirname = os.path.basename(dirname)
        vectors = LoadVectors(filename)
        articles, _ = LoadArticles(filename.replace(".50.lda", ""), False)
        similar_articles = GetSimilarArticles(articles, vectors, gold_vector,
                                              args.similarity_threshold)
        count = dirname_to_count.get(base_dirname, (0, 0))
        dirname_to_count[base_dirname] = (count[0] + len(articles),
                                          count[1] + len(similar_articles))
        # probably a better way to do this, but whatever
        for t in all_topics:
            if t in base_dirname:
                count = topic_to_count[t]
                topic_to_count[t] = (count[0] + len(articles),
                                     count[1] + len(similar_articles))

    out_f = open(args.log_file + str(args.similarity_threshold) + ".sub.txt", "w")
    for k in dirname_to_count:
        v = dirname_to_count[k]
        out_f.write(k + " " + str(v[0]) + " " + str(v[1]) + "\n")
    out_f.close()

    out_f = open(args.log_file + str(args.similarity_threshold) + ".all.txt", "w")
    for k in topic_to_count:
        v = topic_to_count[k]
        out_f.write(k + " " + str(v[0]) + " " + str(v[1]) + "\n")
    out_f.close()


if __name__ == '__main__':
  main()
