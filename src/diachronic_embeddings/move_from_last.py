import gensim
import argparse
from gensim.models import KeyedVectors, Word2Vec
import os
from datetime import date

import sys
sys.path.append("..")
from article_utils import get_ordered_files
from utils import *

import numpy
from scipy.spatial.distance import cosine

SEEDS = ["USA"]
NUM_NEIGHBORS = 50

def get_local(last_center, new_center, wv):
    return

def main():
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", default="/usr1/home/anjalief/word_embed_cache/yearly_mods/lowercased_more_years/")
    parser.add_argument('--metric', type=str,
                        default='global',
                        choices=['global', 'local'])
    args = parser.parse_args()

    date_seq, filenames = get_ordered_files(args.model_path)
    last_center = None
    last_center_NN = None
    for date,model_name in zip(date_seq, filenames):
        wv = KeyedVectors.load(model_name)

        if last_center is None:
            last_center = get_seed_center(SEEDS, wv)
            continue

        if args.metric == "global":
            new_center = get_seed_center(SEEDS, wv)
            print (date, cosine(last_center, new_center))
            last_center = new_center

if __name__ == "__main__":
    main()
