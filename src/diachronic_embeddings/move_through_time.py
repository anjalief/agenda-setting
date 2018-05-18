# Need to run diachronic_word_embeddings to create
# models before using this script

# Input: list of keywords (country names)
# Output: For each timestep in models, write files with lexicon
import gensim
import argparse
from gensim.models import KeyedVectors, Word2Vec
import os
from datetime import date

import sys
sys.path.append("..")
from article_utils import get_files_by_time_slice, YEARS, MONTHS
from utils import *

import numpy
from sklearn import preprocessing # Probably don't need this
from scipy.spatial.distance import cosine
from sklearn.decomposition import PCA

from collections import defaultdict

WRITE_VOCAB=True
WRITE_CENTER_MOVE=False
WRITE_CENTER_FROM_LAST=False
DISTANCE_FROM_USA=True
LEARN_CLUSTERS=True
SINGLE_WORD=False

ECON_SEEDS = ["рынке", "рынка", "рост", "рынок", "экономики"]
MILITARY_SEEDS = ["безопасности", "войны", "оружия", "военной", "мир", "военных", "солдат", "обороны"]
ELECTIONS_SEEDS = ["политики", "выборов", "партии", "выборах", "выборов"]
SPORTS = ["команды", ]


def get_pca_center(keywords, wv):
    print("HERE")
    vectors = [wv[k] for k in keywords]
    vector_array = numpy.stack(vectors)
    pca = PCA(n_components=10)
    pca.fit(vector_array)
    print(pca.explained_variance_ratio_)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", default="/usr1/home/anjalief/corpora/ner_model_cache/")
    parser.add_argument("--article_glob", default="./keywords.txt")
    parser.add_argument("--out_path", default="./outputs/")
    parser.add_argument('--timestep', type=str,
                        default='monthly',
                        choices=['monthly', 'quarterly', 'semi', 'yearly'])
    parser.add_argument("--lexicon_size", type=int, default=100)
    args = parser.parse_args()

    # FIRST: Gather inputs. Start with keywords, datelist, and vocab words from model
#    keywords = ["рынок"]#, , , ] "экономического" "экономика" "фондовый"
    keywords = ELECTIONS_SEEDS
#    keywords = ["USA"]

    date_seq, filenames = get_files_by_time_slice(
        args.model_path, args.timestep, suffix= "_" + args.timestep + ".pickle")

    if LEARN_CLUSTERS:
        # last file name was learned on all data
        base_model = KeyedVectors.load(filenames[0][0])
        from kmeans_cluster import make_clusters
        from get_top_words import get_top_words
        # theoretically we pass an article glob but it should be cached
        noun_to_count,adj_to_count,top_words = get_top_words(args.article_glob)
        vocab = [k for k in sorted(noun_to_count, key=noun_to_count.get, reverse = True)[:10000]]
#        vocab += [k for k in sorted(adj_to_count, key=adj_to_count.get, reverse = True)[:5000]]
        # 300 is number of clusters
        label_to_list = make_clusters(vocab, base_model, 300)

        label_to_last_distance = defaultdict(list)
        label_to_usa_distance = defaultdict(list)
        label_to_last_center = {}
        label_to_center = defaultdict(list)

        for date, file_list in zip(date_seq, filenames):
            assert (len(file_list) == 1)
            for model_name in file_list:
                wv = KeyedVectors.load(model_name)

                # For each label, get the 100 KNNs and get the center
                for label in label_to_list:
                    vocab = [l[0] for l in wv.most_similar(positive=label_to_list[label], topn=100)]
                    center = get_seed_center(vocab, wv)

                    if label in label_to_last_center:
                        label_to_last_distance[label].append(
                            cosine(label_to_last_center[label], center))

                    label_to_last_center[label] = center
                    label_to_usa_distance[label].append(
                        cosine(wv["USA"], center))
                    label_to_center[label].append(center)

# apparently this is pretty fast at least on yearly
#        pickle.dump((label_to_list, label_to_last_distance, label_to_usa_distance, label_to_center), open("move_out.pickle", "wb"))

        # NOT SEEING MUCH INTERESTING HERE
        # Show which topics move the least from first to last
        # Show which topics move the most from first to last
        # sorted_by_movement = sorted(label_to_center,
        #                             key=lambda x: cosine(label_to_center[x][0], label_to_center[x][-1]), reverse=True)
        # print ("Most moved")
        # for k in sorted_by_movement[:10]:
        #     print (label_to_list[k])
        #     print (label_to_last_distance[k], cosine(label_to_center[k][0], label_to_center[k][-1]))

        # print ("Least moved")
        # for k in sorted_by_movement[-10:]:
        #     print (label_to_list[k], cosine(label_to_center[k][0], label_to_center[k][-1]))

        # Show which have strongest correlations: distance to U.S. vs. % Change USA freq
        usa_percent_change = [float(x) for x in open("usa_percent_change.txt").readlines()]
        print (len(usa_percent_change))
        print (len(label_to_usa_distance[0]))
        sort_by_corr = sorted(label_to_usa_distance,
                              key=lambda x:get_corr(label_to_usa_distance[x],
                                                    usa_percent_change), reverse=True)
        print ("Largest Corr")
        for k in sort_by_corr[:10]:
            print(get_corr(label_to_usa_distance[k],usa_percent_change))
            print (label_to_list[k])

        print ("Smallest_corr")
        for k in sort_by_corr[-10:]:
            print(get_corr(label_to_usa_distance[k],usa_percent_change))
            print (label_to_list[k])

        # We want the percent change that is large and negtive, i.e. moved
        # # much closer to this topic
        # print ("Moved most from 2012 to 2013")
        # print(date_seq[9], date_seq[10])
        # sort_by_move = sorted(label_to_usa_distance,
        #                       key=lambda x:((label_to_usa_distance[x][10] / label_to_usa_distance[x][9]) - 1))
        # for c in sort_by_move[30:]:
        #     print (label_to_list[c])
        #     print ((label_to_usa_distance[c][10] / label_to_usa_distance[c][9]) - 1)

        # print ("Closest to 2013")
        # sort_by_dist = sorted(label_to_usa_distance,
        #                       key=lambda x:(label_to_usa_distance[x][10]))
        # for c in sort_by_dist[30:]:
        #     print (label_to_list[c])
        #     print (label_to_usa_distance[c][10])

    last_center = None
    print(keywords[0])
    for i in range(0,1):
        print ("***********************************************")
        for date, file_list in zip(date_seq, filenames):
            assert (len(file_list) == 1)
            for model_name in file_list:
                wv = KeyedVectors.load(model_name)
                basename = os.path.basename(model_name)

                if WRITE_CENTER_MOVE:
                    vocab = [l[0] for l in wv.most_similar(positive=keywords, topn=100)]
                    center = get_seed_center(vocab, wv)
                    # get_pca_center(vocab, wv)
                    # return
                    if DISTANCE_FROM_USA:
                        print (date, cosine(center, wv["RUSSIA"]))
                    else:
                        if not last_center is None:
                            print (date, cosine(center, last_center))
                    last_center = center


                if WRITE_CENTER_FROM_LAST:
                    if last_center is None:
                        vocab = [l[0] for l in wv.most_similar(positive=keywords, topn=100)]
                        center = get_seed_center(vocab, wv)
                    else:
                        vocab = [l[0] for l in wv.most_similar(positive=[last_center], topn=100)]
                        center = get_seed_center(vocab, wv)
                        print (cosine(center, last_center))
                    last_center = center

                if WRITE_VOCAB:
                    fp = open(os.path.join(args.out_path, basename), "w")
                    for l in vocab:
                        fp.write(str(l) + "\n")
                    fp.close()

                if SINGLE_WORD:
                    word = "выборов"
                    print (cosine(wv["USA"], wv[word]))


if __name__ == "__main__":
    main()
