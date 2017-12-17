#!/usr/bin/env python

import argparse
import collections
import os
import glob
from article_utils import ArticleIter, LoadArticles, LoadVectors, Similarity

parser = argparse.ArgumentParser()
parser.add_argument('--gold_vectors',
    default="../focused_crawl/external_policy.txt.tok.lda")
parser.add_argument('--per_month_glob',
    default="../news/russian/Izvestiia/*/*.txt.tok.lda")
parser.add_argument('--similarity_threshold',
    type=float, default=0.4)
parser.add_argument('--log_file',
    default="../work/topic_stats.lda")
args = parser.parse_args()

def GetSimilarArticles(articles, vectors, gold_vector, threshold):
  similar = []
  for article, vector in zip(articles, vectors):
    if Similarity(vector, gold_vector) < threshold:
      similar.append(article)
  return similar

def main():
  out_f = open(args.log_file, "a")
  gold_vector = LoadVectors(args.gold_vectors)[0]
  out_f.write(args.per_month_glob)
  out_f.write("\n")
  for filename in sorted(glob.iglob(args.per_month_glob)):
    dirname = os.path.dirname(filename)
    year_month = os.path.basename(filename.replace(".txt.tok.lda", ""))
    vectors = LoadVectors(filename)
    articles, _ = LoadArticles(filename.replace(".lda", ""))
    similar_articles = GetSimilarArticles(articles, vectors, gold_vector,
        args.similarity_threshold)
    out_f.write("{}\t{}\t{}\n".format(year_month, len(similar_articles), len(vectors)))

if __name__ == '__main__':
  main()
