#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Need to run diachronic_word_embeddings to create
# models before using this script because we use it
# to generate vocab

import gensim
import argparse
from gensim.models import KeyedVectors
import re
from utils import *
import sys
sys.path.append("..")
from article_utils import get_files_by_time_slice

# for parallelizing
import multiprocessing
LIWC_REG = []

def read_liwc_file(filename, key):
    liwc_words = set()
    for line in open(filename).readlines():
        splits = line.split()
        if len(splits) < 2:
            continue
        # file format is: word [key] [key] [key]
        if key in splits[1:]:
            liwc_words.add(splits[0])
    return liwc_words

def build_lex(vocab_word):
    my_lexicon = []
    for x in LIWC_REG:
        if x.match(vocab_word.lower()):
            return (vocab_word, x)
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", default="/usr1/home/anjalief/word_embed_cache/ner_model_cache")
    parser.add_argument("--timestep", default="yearly")
    parser.add_argument("--liwc_file", default="/usr1/home/anjalief/corpora/russian/Russian_LIWC2007_Dictionary.dic")
    parser.add_argument("--liwc_key")
    parser.add_argument("--outfile", default="./tmp.txt")

    args = parser.parse_args()

    vocab = set()

    liwc_words = read_liwc_file(args.liwc_file, args.liwc_key)
    global LIWC_REG
    LIWC_REG = [re.compile(x.replace("*", ".*") + "$") for x in liwc_words]

    date_seq, filenames = get_files_by_time_slice(
        args.model_path, args.timestep, suffix= "_" + args.timestep + ".pickle")

    for filename_list in filenames:
        for filename in filename_list:
            wv = KeyedVectors.load(filename)
            for x in wv.index2entity:
                vocab.add(x)

    print (len(vocab))

    pool = multiprocessing.Pool(processes=10)
    out_data = pool.map(build_lex, vocab)

    fp = open(args.outfile, "w")
    for x in out_data:
        if not x is None:
            fp.write(x[0])
            fp.write("\n")
    fp.close()

if __name__ == "__main__":
    main()
