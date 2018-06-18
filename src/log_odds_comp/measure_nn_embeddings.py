import sys
sys.path.append("..")
sys.path.append("../diachronic_embeddings")
from econ_utils import load_econ_file, get_corr
from article_utils import *
from basic_log_odds import LoadBackgroundCorpus, LoadCountsExternal, write_log_odds
from merge_frames import get_merged_frames
from utils import get_mean_similarity

from scipy.spatial.distance import cosine
from gensim.models import KeyedVectors
import argparse
from collections import defaultdict
import pickle
import numpy
from sklearn import preprocessing # Probably don't need this


def get_knn_overlap(seeds, wv, cosine_sim = True):
    seed_neigh = [k[0] for k in wv.most_similar(positive=[s for s in seeds if s in wv], topn=1000)]
    seed_neigh += seeds
    usa_neigh = [k[0] for k in wv.most_similar(positive="USA", topn=1000)]

    if cosine_sim:
        sim = 0
        for n in usa_neigh:
            if n in seed_neigh:
                sim += (1 - cosine(wv["USA"], wv[n]))
        return sim / len(seeds)

    usa_neigh.append("USA")
    count = 0
    for n in usa_neigh:
        if n in seed_neigh:
            count += 1
    return count / float(len(seed_neigh))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", default="/usr1/home/anjalief/word_embed_cache/yearly_mods/lowercased_more_years/")
    parser.add_argument('--timestep', type=str,
                        default='yearly',
                        choices=['monthly', 'quarterly', 'semi', 'yearly'])
    args = parser.parse_args()

    date_seq, filenames = get_files_by_time_slice(
        args.model_path, args.timestep, suffix= "_" + args.timestep + ".pickle")


    frame_to_lex = pickle.load(open("frame_to_lex_final.pickle", "rb"))
#    frame_to_lex = get_merged_frames(frame_to_lex)
    del frame_to_lex["Other"]
    frame_to_overlap_usa = defaultdict(list)


    for date, file_list in zip(date_seq, filenames):
        assert (len(file_list) == 1)
        for model_name in file_list:
            wv = KeyedVectors.load(model_name)

            for c in frame_to_lex:
                seeds = frame_to_lex[c]
#                frame_to_overlap_usa[c].append(get_knn_overlap(seeds, wv))
                frame_to_overlap_usa[c].append(get_mean_similarity("USA",seeds, wv))

    print(" ", end=";")
    for f in sorted(frame_to_lex):
        print (f, end=";")
    print("")

    for i,d in enumerate(date_seq):
        print(d, end=";")
        for f in sorted(frame_to_overlap_usa):
            print (frame_to_overlap_usa[f][i], end=";")
        print("")

def small_main():
    model = KeyedVectors.load("/usr1/home/anjalief/word_embed_cache/all_train_v3_200.model")
    frame_to_lex = pickle.load(open("frame_to_lex_final.pickle", "rb"))
    for c in frame_to_lex:
        seeds = frame_to_lex[c]
        print(c + ";" + str(get_knn_overlap(seeds, model)))

if __name__ == "__main__":
    main()
