import gensim
import argparse
from gensim.models import KeyedVectors, Word2Vec
import os
from datetime import date

import sys
sys.path.append("..")
from article_utils import get_ordered_files
from utils import *

from kmeans_cluster import make_clusters
from get_top_words import get_top_words

import numpy
from scipy.spatial.distance import cosine

from datetime import date

SEEDS = ["USA"]
STEP_1 = date(2000, 1, 1)
STEP_2 = date(2001, 1, 1)

# return label -> how far label is from seed in this model
def get_topic_distance_from_seed(label_to_list, wv, seeds):
    label_to_seed_distance = {}
    seed_center = get_seed_center(seeds, wv)

    for label in label_to_list:
#        vocab = [l[0] for l in wv.most_similar(positive=label_to_list[label], topn=100)]
        center = get_seed_center(label_to_list[label], wv)
        label_to_seed_distance[label] = cosine(center, seed_center)
    return label_to_seed_distance

def print_knns(model1, model2, seeds):
    print ([k[0] for k in model1.most_similar(positive=seeds, topn=500)])
    print ([k[0] for k in model2.most_similar(positive=seeds, topn=500)])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", default="/usr1/home/anjalief/word_embed_cache/yearly_mods/lowercased_more_years/")
    parser.add_argument("--article_glob", default="/usr1/home/anjalief/corpora/russian/yearly_mods/iz_lower/*.txt.tok")
    args = parser.parse_args()

    date_seq, filenames = get_ordered_files(args.model_path)

    model1_name = filenames[date_seq.index(STEP_1)]
    model1 = KeyedVectors.load(model1_name)

    model2_name = filenames[date_seq.index(STEP_2)]
    model2 = KeyedVectors.load(model2_name)
    # print_knns(model1, model2, SEEDS)
    # return

    print (model1_name, model2_name)

    # we make clusters from last file
    base_model = KeyedVectors.load(filenames[0])
    noun_to_count,adj_to_count,top_words = get_top_words(args.article_glob)

    vocab = [k for k in sorted(top_words, key=top_words.get, reverse = True)[:10000]]

    # Other ways of building vocab
    # vocab = [k for k in sorted(top_words, key=top_words.get, reverse = True)[:10000]]
    # vocab = [k for k in sorted(adj_to_count, key=adj_to_count.get, reverse = True)[:10000]]
#    vocab = [k[0] for k in base_model.most_similar(positive=SEEDS, topn=10000)]

    # 300 is number of clusters
    label_to_list = make_clusters(vocab, base_model, 300)

    # only keep 50 topics that are close to U.S.
    # d_to_us = {}
    # new_label_to_list = {}
    # for l in label_to_list:
    #     center = get_seed_center(label_to_list[l], base_model)
    #     d_to_us[l] = cosine(center, base_model["USA"])
    # for l in sorted(d_to_us, key=d_to_us.get)[:50]:
    #     print(d_to_us[l], label_to_list[l])
    #     new_label_to_list[l] = label_to_list[l]
    # label_to_list = new_label_to_list
    # print ("**************************************************************************")

    label_to_dist_s1 = get_topic_distance_from_seed(label_to_list, model1, SEEDS)
    label_to_dist_s2 = get_topic_distance_from_seed(label_to_list, model2, SEEDS)

    shifts = {}
    for l in label_to_dist_s1:
        # A large negative shift indicates topic become more salient in s2
        shifts[l] = (label_to_dist_s2[l] - label_to_dist_s1[l])

    for l in sorted(shifts, key=shifts.get)[:10]:
        print (shifts[l], label_to_list[l])

if __name__ == "__main__":
    main()
