#!/usr/bin/env python
from collections import defaultdict
import math
import argparse
from article_utils import LoadArticles, LoadVectors
from baseline_country import get_countries, contains_country

# Dan Jurafsky March 22 2013
# bayes.py
# Computes the "weighted log-odds-ratio, informative dirichlet prior" algorithm for 
# from page 388 of 
# Monroe, Colaresi, and Quinn. 2009. "Fightin' Words: Lexical Feature Selection and Evaluation for Identifying the Content of Political Conflict"

# assumes all 3 input files are space-separated, two columns, frequency followed by word
#1371056 the
#923839 and
#765263 i

parser = argparse.ArgumentParser(description='Computes the weighted log-odds-ratio, informative dirichlet prior algorithm')
parser.add_argument('-f','--first', help='Description for first counts file ', default='greatreviews.out')
parser.add_argument('-s','--second', help='Description for second counts file', default='badreviews.out')
parser.add_argument('-p','--prior', help='Description for prior counts file')
parser.add_argument('-c','--country_list', help='If specified, filter by baseline')
parser.add_argument('--min_count', default=0)
parser.add_argument('--stopwords')
args = parser.parse_args()

def LoadCounts(filename, min_count=0, stopwords=set()):
  result = defaultdict(int)
  for line in open(filename):
    word, count = line.split()
    count = int(count)
    if count >= min_count and word not in stopwords:
      result[word] = count
  return result

def LoadStopwords(filename):
  stopwords = set()
  for line in open(filename):
    for word in line.split():
      if word:
        stopwords.add(word)
  return stopwords

# NOTE: not supporting mincount or stopwords
def LoadFilteredCounts(articles, countries, prior):
  result = defaultdict(int)
  for a in articles:
    words = a.split()
    yes = contains_country(words, countries)
    for w in words:
      w = w.decode('utf-8').lower()
      if yes:
        result[w] += 1
      prior[w] += 1
  return result, prior

stopwords = set()
if args.stopwords:
  stopwords = LoadStopwords(args.stopwords)
else:
  print "Not using stopwords"

# this means we want to filter, only take articles that have country names
if (args.country_list):
  countries = get_countries(args.country_list)

  # special casing this for now, atm we want prior to be combined dict
  articles1, _ = LoadArticles(args.first)
  counts1, prior = LoadFilteredCounts(articles1, countries, defaultdict(int))
  articles2, _ = LoadArticles(args.second)
  counts2, prior = LoadFilteredCounts(articles2, countries,  prior)

else:
  counts1 = LoadCounts(args.first, 0, stopwords)
  counts2 = LoadCounts(args.second, 0, stopwords)
  if args.prior:
    prior = LoadCounts(args.prior, args.min_count, stopwords)
  else:
    prior = defaultdict(int)
    for c in counts1:
      prior[c] = counts1[c]
    for c in counts2:
      prior[c] += counts2[c]

sigmasquared = defaultdict(float)
sigma = defaultdict(float)
delta = defaultdict(float)

for word in prior.keys():
    prior[word] = int(prior[word] + 0.5)

for word in counts2.keys():
    counts1[word] = int(counts1[word] + 0.5)
    if prior[word] == 0:
        prior[word] = 1

for word in counts1.keys():
    counts2[word] = int(counts2[word] + 0.5)
    if prior[word] == 0:
        prior[word] = 1

n1  = sum(counts1.values())
n2  = sum(counts2.values())
nprior = sum(prior.values())


for word in prior.keys():
    #if prior[word] == 0 and (counts2[word] > 10):
        #prior[word] = 1
    if prior[word] > 0:
        l1 = float(counts1[word] + prior[word]) / (( n1 + nprior ) - (counts1[word] + prior[word]))
        l2 = float(counts2[word] + prior[word]) / (( n2 + nprior ) - (counts2[word] + prior[word]))
        sigmasquared[word] =  1/(float(counts1[word]) + float(prior[word])) + 1/(float(counts2[word]) + float(prior[word]))
        sigma[word] =  math.sqrt(sigmasquared[word])
        delta[word] = ( math.log(l1) - math.log(l2) ) / sigma[word]

outfile = open("log_odds_09.txt", 'w')
for word in sorted(delta, key=delta.get):
    outfile.write(word.encode('utf-8'))
    outfile.write(" %.3f\n" % delta[word])

outfile.close()
