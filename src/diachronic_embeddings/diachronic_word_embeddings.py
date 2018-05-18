#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Train diachronic word embeddings
# Use initial files to seed the model
# For each timestep file in article_path, take previous model
# update with new articles, save down new model in cache_path
import sys
sys.path.append("..")

from article_utils import *
import argparse
from gensim.models import Word2Vec
from utils import *

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path') # default="/usr1/home/anjalief/corpora/russian/country_sub/Isveztiia/")
    parser.add_argument('--initial_files', default="/usr1/home/anjalief/corpora/russian/country_sub/Isveztiia/init_files/*.txt.tok")
    parser.add_argument('--cache_path')
    parser.add_argument('--window_size', default=5)
    parser.add_argument('--reload_base', action='store_true', help="Train each step from base instead of from previous step")
    parser.add_argument('--timestep', type=str,
                        default='monthly',
                        choices=['monthly', 'quarterly', 'semi', 'yearly'])
    args = parser.parse_args()


    # sg  – Defines the training algorithm. If 1, skip-gram is employed; otherwise, CBOW is used.
    # size – Dimensionality of the feature vectors.
    # window – The maximum distance between the current and predicted word within a sentence.
    # min_count  – Ignores all words with total frequency lower than this.
    # workers (int) – Use these many worker threads to train the model (=faster training with multicore machines).
    sentence_iter = SentenceIter(args.initial_files, verbose=False)

    # SAVE THE BASE
    base_model = Word2Vec(sentence_iter, size=200, window=args.window_size, min_count=100, workers=6)
    base_model_name = args.cache_path + "base_model.pickle"
    fp = open(base_model_name, "wb")
    base_model.save(fp)
    fp.close()

    if not args.input_path:
        return

    # for each time slice, save down just the vectors
    date_seq, filenames = get_files_by_time_slice(args.input_path, args.timestep)

    # They are sorted already
    for (d,files) in zip(date_seq, filenames):
        for filename in files:
            if args.reload_base:
                base_model = Word2Vec.load(base_model_name)
            sentence_iter = SentenceIter(filename, verbose=False)
            count = 0
            for x in sentence_iter:
                count += 1
            base_model.train(sentence_iter, total_examples=count, epochs=base_model.epochs)
        fp = open(get_model_filename(args.cache_path, str(d.year), str(d.month), args.timestep), "wb")
        base_model.wv.save(fp)
        fp.close()


if __name__ == "__main__":
    main()
