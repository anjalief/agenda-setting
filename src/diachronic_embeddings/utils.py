#!/usr/bin/env python3

import os
import numpy
from scipy import spatial

# have to load these manually because the file names don't sort correctly
YEARS = ["2003", "2004", "2005", "2006", "2007", "2008", "2009",
         "2010", "2011", "2012", "2013", "2014", "2015", "2016"]
MONTHS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
# YEARS = ["2003"]
# MONTHS = ["1", "2", "3", "4"]
EMBEDDING_SIZE=100

def get_model_filename(path, year, month):
    return os.path.join(path, year + "_" + month + ".pickle")


# this is bad, but for now if there are multiple words in the file, we are just
# going to take the first one
def load_file(name):
    lines = open(name).readlines()
    lines = [l.split()[0] for l in lines]
    return lines

def get_corr(x, y):
    # this returns a matrix where 0,1 is the correlation between seq 0 and seq 1 (I think)
    # since we're only going to give in 1D lists, we can grab the top right element
    return numpy.corrcoef(x, y)[0, 1]


# Calculate average of similarities between keyword and every word in context_words
def get_pointwise_similarity(keyword, context_words, wv):
    total_sim = 0
    word_count = len(context_words)
    for w in context_words:
        if not w in wv:
            word_count -= 1
            continue
        total_sim += wv.similarity(keyword, w)
    return (float(total_sim) / word_count)

# Find center of a set of vectors (unnormalized)
def get_center(words, wv, embedding_size):
    center = [0 for i in range(0, embedding_size)]
    for w in words:
        if not w in wv:
            continue
        center = [x+y for x,y in zip(center, wv[w])]
    return center

# First find center of context_words vectors, then return similarity between keyword and center
def get_mean_similarity(keyword, context_words, wv):
    center = get_center(context_words, wv, EMBEDDING_SIZE)
    return 1 - spatial.distance.cosine(center, wv[keyword])


# Entry point, other programs should call this one and we can flip
# type of similarity here
# Returns similarity between single vector "keyword" and set of vectors "context_words"
def get_similarity(keyword, context_words, wv):
    if not keyword in wv:
        print ("NO EMBEDDING FOR KEYWORD", keyword)
        return False

#    return get_mean_similarity(keyword, context_words, wv)
    return get_pointwise_similarity(keyword, context_words, wv)

def get_date_seq():
    date_seq = []
    for year in YEARS:
        for month in MONTHS:
            date_seq.append(date(int(year), int(month), 1))
    return date_seq
