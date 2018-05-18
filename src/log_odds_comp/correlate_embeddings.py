import sys
sys.path.append("..")
from econ_utils import load_econ_file, get_corr
from article_utils import *
from basic_log_odds import LoadBackgroundCorpus, LoadCountsExternal, write_log_odds

from scipy.spatial.distance import cosine
from gensim.models import KeyedVectors
import argparse
from collections import defaultdict
import pickle
import numpy
from sklearn import preprocessing # Probably don't need this

def get_seed_center(keywords, wv):
    for k in keywords:
        if k in wv:
            length = len(wv[k])
            break
    center = numpy.zeros(length)
    skip_count = 0
    for k in keywords:
        if not k in wv:
            skip_count += 1
            continue
        center += wv[k]
    print ("SKIPPED", skip_count, len(keywords))
    return preprocessing.normalize(center.reshape(1, -1)).reshape(length)

def print_stats(econ_seq, frame_seq):
    assert(len(econ_seq) == len(frame_seq))
    print(get_corr(econ_seq, frame_seq))

    res = do_granger_test(frame_seq, econ_seq)
    for lag in res:
        print (lag)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--econ_file", default="/usr1/home/anjalief/corpora/russian/russian_yearly_gdp.csv")
#    parser.add_argument("--input_path", default="/usr1/home/anjalief/corpora/russian/yearly_mod_subs/iz_lower/")
    parser.add_argument("--model_path", default="/usr1/home/anjalief/word_embed_cache/yearly_mods/lowercased_200_100/")
    parser.add_argument("--keywords", default="./keywords.txt")
    parser.add_argument('--timestep', type=str,
                        default='yearly',
                        choices=['monthly', 'quarterly', 'semi', 'yearly'])
    args = parser.parse_args()

    date_seq, filenames = get_files_by_time_slice(
        args.model_path, args.timestep, suffix= "_" + args.timestep + ".pickle")

    econ_seq = load_econ_file(args.econ_file, args.timestep, date_seq)

    frame_to_lex = pickle.load(open("frame_to_lex.pickle", "rb"))
    frame_to_dist_usa = defaultdict(list)

    for date, file_list in zip(date_seq, filenames):
        assert (len(file_list) == 1)
        for model_name in file_list:
            wv = KeyedVectors.load(model_name)
            basename = os.path.basename(model_name)

            for c in frame_to_lex:
                seeds = frame_to_lex[c]
                # I don't think we need to add neighbors, 100+ word lex should be good enough
                center = get_seed_center(seeds, wv)
                # if difference is negative, means topic is closer to US
                # (distance to US is smaller than distance to Russia)
                # if difference is positive, means topic is closer to Russa
                # we expect negative topics to have positive correlation with
                # GDP -- they get closer to US as economy does worse
                frame_to_dist_usa[c].append(cosine(center, wv["USA"])
                                            - cosine(center, wv["RUSSIA"]))


    for c in frame_to_dist_usa:
        print(c)
        print(get_corr(frame_to_dist_usa[c], econ_seq))
        print("******************************************************************************")
        for x in frame_to_dist_usa[c]:
            print (x)
        print("******************************************************************************")



if __name__ == "__main__":
    main()
