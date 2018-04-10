
#!/usr/bin/env python3

# Train diachronic word embeddings
# Use initial files to seed the model
# For each timestep file in article_path, take previous model
# update with new articles, save down new model in cache_path
import sys
sys.path.append("..")

from article_utils import LoadArticles, SentenceIter
import argparse
from gensim.models import Word2Vec
from utils import *

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--article_path')
    parser.add_argument('--initial_files')
    parser.add_argument('--cache_path')
    args = parser.parse_args()


    # sg  – Defines the training algorithm. If 1, skip-gram is employed; otherwise, CBOW is used.
    # size – Dimensionality of the feature vectors.
    # window – The maximum distance between the current and predicted word within a sentence.
    # min_count  – Ignores all words with total frequency lower than this.
    # workers (int) – Use these many worker threads to train the model (=faster training with multicore machines).
    sentence_iter = SentenceIter(args.initial_files, verbose=False)

    # SAVE THE BASE
    base_model = Word2Vec(sentence_iter, size=100, window=5, min_count=5, workers=4)
    fp = open(args.cache_path + "base_model.pickle", "wb")
    base_model.save(fp)
    fp.close()

    # for each time slice, save down just the vectors
    for year in YEARS:
        for month in MONTHS:
            filename = year + "_" + month
            original_file = args.article_path + year + "/" + filename + ".txt.tok"
            sentence_iter = SentenceIter(original_file, verbose=False)
            count = 0
            for x in sentence_iter:
                count += 1
            base_model.train(sentence_iter, total_examples=count, epochs=base_model.epochs)
            fp = open(get_model_filename(args.cache_path, year, month), "wb")
            base_model.wv.save(fp)
            fp.close()


    # load base model with
    # model = gensim.models.Word2Vec.load("/usr1/home/anjalief/russian_model_cache/base_model.pickle")

    # load vectors with
    # from gensim.models import KeyedVectors
    # wv = KeyedVectors.load("/usr1/home/anjalief/russian_model_cache/2007_2.pickle")

    # similarity works for both:
    # model.similarity('.', ',')
    # wv.similarity('.', ',')


    # wv2007 = KeyedVectors.load("/usr1/home/anjalief/russian_model_cache/2007_2.pickle")
    # wv2009 = KeyedVectors.load("/usr1/home/anjalief/russian_model_cache/2009_2.pickle")

    # wv2007.similarity("безработица", "Россия")
    # 0.19267169714521806

    # wv2009.similarity("безработица", "Россия")
    # 0.13384728784281097


if __name__ == "__main__":
    main()
