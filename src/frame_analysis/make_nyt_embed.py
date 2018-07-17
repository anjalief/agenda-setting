#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gensim.models import Word2Vec, KeyedVectors
import sys
sys.path.append("..")
from article_utils import SentenceIter
from data_iters import BackgroundIter
import glob

# Use this when we only train embeddings with target corpus
NYT_ONLY=False

class MFC_NYT_iter(object):
    def __init__(self, nyt_iter, mfc_iter):
        self.nyt_iter = nyt_iter
        self.mfc_iter = mfc_iter

    def __iter__(self):
        for sentence in self.nyt_iter:
            yield sentence
        for sentence in self.mfc_iter:
            yield sentence

def main():
    article_glob = "/usr1/home/anjalief/corpora/nyt_news/all_nyt_paras_text/*/*.txt.tok"


    sentence_iter = SentenceIter(article_glob, verbose=False, skip_corrections=True)

    if NYT_ONLY:
        base_model = Word2Vec(sentence_iter, size=200, window=5, min_count=100, workers=10)
        fp = open("./cache/nyt_base.model", "wb")
    else:
        mfc_glob = glob.iglob("/usr1/home/anjalief/media_frames_corpus/parsed/*/json/*.json")
        mfc_iter = BackgroundIter(mfc_glob)
        dual_iter = MFC_NYT_iter(sentence_iter, mfc_iter)
        base_model = Word2Vec(dual_iter, size=200, window=5, min_count=100, workers=10)
        fp = open("./cache/nyt_mfc.model", "wb")

    base_model.save(fp)
    fp.close()

if __name__ == "__main__":
    main()
