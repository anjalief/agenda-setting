#!/usr/bin/env python3

import os
import glob
import math
from scipy.stats.stats import pearsonr
from scipy import spatial
from datetime import date

NEW_ARTICLE_TOKEN="NEW - ARTICLE - TOKEN"

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

def ArticleIter(filename, new_article_token, verbose=False):
  current_article = []
  if verbose:
    print("Processing", filename)
  for line in open(filename):
    line = line.strip()
    if not line:
      continue
    if line == new_article_token:
      if current_article:
        yield "\n".join(current_article)
        current_article = []
    else:
      current_article.append(line)
  if current_article:
    yield "\n".join(current_article)

def LoadArticles(article_glob, verbose=True, new_article_token=NEW_ARTICLE_TOKEN, sort_files=False, split = False):
  articles = []
  article_index = []
  if sort_files:
    files = sorted(glob.iglob(article_glob))
  else:
    files = glob.iglob(article_glob)
  for filename in files:
    if verbose:
      print("Loading:", filename)
    for index, article in enumerate(ArticleIter(filename, new_article_token, verbose)):
      if split:
        articles.append(article.split())
      else:
        articles.append(article)
      article_index.append((filename, index))
    if verbose:
      print("  articles:", index+1)
  return articles, article_index

def Similarity(v1, v2, metric="cosine"):
  def IsZero(v):
    return all(n == 0 for n in v)

  if metric == "correlation":
    if IsZero(v1) or IsZero(v2):
      return 0.0
    return pearsonr(v1, v2)[0]

  if metric == "abs_correlation":
    if IsZero(v1) or IsZero(v2):
      return 0.0
    return abs(pearsonr(v1, v2)[0])

  if metric == "cosine":
    return spatial.distance.cosine(v1, v2)

def LoadVectors(filename):
  vectors = []
  for line in open(filename):
    vector = [float(n) for n in line.split()]
    if len(vector) == 0:
      continue
    # normalize
    sqrt_length = math.sqrt(sum([n**2 for n in vector]) + 1e-6)
    vectors.append([n/sqrt_length for n in vector])
  return vectors

def GetSimilarArticles(articles, vectors, gold_vector, threshold):
  similar = []
  for article, vector in zip(articles, vectors):
    if Similarity(vector, gold_vector) < threshold:
      similar.append(article)
  return similar


# Note, this is intended for input into gensim models, can't make it
# a full generator because gensim wants an iterator
import nltk
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
#from russian_stemmer import country_russian_stemmer
class SentenceIter(object):
  def __init__(self, article_glob, verbose=True, new_article_token=NEW_ARTICLE_TOKEN):
    self.article_glob = article_glob
    self.verbose = verbose
    self.new_article_token = new_article_token
#    self.stemmer = country_russian_stemmer()

  def __iter__(self):
    for filename in glob.iglob(self.article_glob):
      if self.verbose:
        print("Loading:", filename)
      for article in ArticleIter(filename, self.new_article_token, self.verbose):
        for s in tokenizer.tokenize(article):
          # NOTE: We almost certainly want to use the ispras lemmatizer here,
          # but it's going to be very slow
          yield s.split()

# for ex path/2007_1.txt.tok, return 2007, 1
def get_year_month(file_path):
  filename = os.path.basename(file_path)
  year_month = filename.split('.')[0]
  splits = year_month.split('_')
  return int(splits[0]), int(splits[1])

# Assigns all dates to the first of the month
def get_date(file_path):
  year, month = get_year_month(file_path)
  return date(year, month, 1)

# Return year and Q1, Q2, Q3, Q4
def get_quarter(file_path):
  year, month = get_year_month(file_path)
  return year, (month / 4) + 1
