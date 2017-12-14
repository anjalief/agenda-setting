#!/usr/bin/env python3

import argparse
import collections
import os
import glob
import itertools

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.externals import joblib

NEW_ARTICLE_TOKEN="NEW - ARTICLE - TOKEN"

def ArticleIter(filename):
  current_article = []
  print("Processing", filename)
  for line in open(filename):
    line = line.strip()
    if not line:
      continue
    if line == NEW_ARTICLE_TOKEN:
      if current_article:
        yield "\n".join(current_article)
        current_article = []
    else:
      current_article.append(line)
  if current_article:
    yield "\n".join(current_article)

def LoadArticles(article_glob):
  articles = []
  article_index = []
  for filename in glob.iglob(article_glob):
    print("Loading:", filename)
    for index, article in enumerate(ArticleIter(filename)):
      articles.append(article)
      article_index.append((filename, index))
    print("  articles:", index+1)
  return articles, article_index

def LoadStopwords(filename):
  stopwords = set()
  if not filename:
    return stopwords
  for line in open(filename):
    for word in line.split():
      if word:
        stopwords.add(word)
  return stopwords

class LDAModel(object):
  def __init__(self, stopwords):
    self.vectorizer = CountVectorizer(
        input='content', strip_accents='unicode',
        analyzer='word', stop_words=stopwords,
        max_df=0.7, min_df=0.001, max_features=3000)
    self.lda = LatentDirichletAllocation(
        n_topics=50, max_iter=5, learning_method='online',
        learning_offset=50., random_state=0)

class LDA(object):
  def __init__(self, load_from_file=None):
    if load_from_file:
      self.model = joblib.load(load_from_file)
    else:
      self.model = None

  def Train(self, articles, stopwords_filename, save_to_file=None):
    self.model = LDAModel(stopwords=LoadStopwords(stopwords_filename))
    print("Building TF")
    tf = self.model.vectorizer.fit_transform(articles)
    print("Training LDA")
    self.model.lda.fit(tf)
    print("LDA trained")
    if save_to_file:
      print("Saving model")
      joblib.dump(self.model, save_to_file, compress=True)

  def GetTopicWeights(self, articles):
    print("Building TF")
    tf = self.model.vectorizer.transform(articles)
    print("Applying LDA")
    topic_weights = self.model.lda.transform(tf)
    return topic_weights

  def tf_feature_names(self):
    return self.model.vectorizer.get_feature_names()

  def print_top_words(self, n_top_words=20):
    feature_names = self.model.vectorizer.get_feature_names()
    for topic_idx, topic in enumerate(self.model.lda.components_):
      print("Topic #%d:" % topic_idx)
      print(" ".join([feature_names[i]
                      for i in topic.argsort()[:-n_top_words - 1:-1]]))
    print()


"""Not used
def MakeTfIdf(articles, stopwords):

  print("Building TF-IDF matrix")
  vectorizer = TfidfVectorizer(input='content', strip_accents='unicode',
      analyzer='word', stop_words=stopwords, norm='l2',
      max_df=0.95, min_df=2, max_features=10000)
  tfidf = vectorizer.fit_transform(articles)
  return tfidf, vectorizer.get_feature_names()
"""

def SaveTopicWeights(article_index, topic_weights):
  current_file = None
  out_f = None
  for (filename, article_num), weights in itertools.zip_longest(
                                              article_index, topic_weights):
    if current_file != filename:
      current_file = filename
      out_f = open(filename + ".lda", "w")
    out_f.write(" ".join((str(w) for w in weights)) + "\n")

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--article_glob')
  parser.add_argument('--stopwords')
  parser.add_argument('--lda_model')
  parser.add_argument('--force_train', action='store_true')
  parser.add_argument('--output_topic_distribution', action='store_true')
  args = parser.parse_args()

  lda = None
  if args.force_train or not os.path.exists(args.lda_model):
    print("Loading articles")
    articles, article_index = LoadArticles(args.article_glob)
    print("Articles:", len(articles))
    print("Training")
    lda = LDA()
    lda.Train(articles, args.stopwords, save_to_file=args.lda_model)
  if args.output_topic_distribution:
    if not lda:
      print("Loading model")
      lda = LDA(load_from_file=args.lda_model)
      print("Loading articles")
      articles, article_index = LoadArticles(args.article_glob)
      print("Articles:", len(articles))
    print("Estimating topic distributions")
    topic_weights = lda.GetTopicWeights(articles)
    print("Saving results")
    SaveTopicWeights(article_index, topic_weights)

if __name__ == '__main__':
  main()
