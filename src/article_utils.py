#!/usr/bin/env python3

import glob
import math
from scipy.stats.stats import pearsonr
from scipy import spatial

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

def LoadArticles(article_glob, verbose=True, new_article_token=NEW_ARTICLE_TOKEN):
  articles = []
  article_index = []
  for filename in glob.iglob(article_glob):
    if verbose:
      print("Loading:", filename)
    for index, article in enumerate(ArticleIter(filename, new_article_token, verbose)):
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
