#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gensim.models import Word2Vec, KeyedVectors
import sys
sys.path.append("..")
from article_utils import SentenceIter


def main():
    article_glob = "/usr1/home/anjalief/corpora/nyt_news/all_nyt_paras_text/*/*.txt.tok"
    fp = open("./cache/nyt_base.model", "wb")

    sentence_iter = SentenceIter(article_glob, verbose=False, skip_corrections=True)
    base_model = Word2Vec(sentence_iter, size=200, window=5, min_count=100, workers=10)

    base_model.save(fp)
    fp.close()

if __name__ == "__main__":
    main()
