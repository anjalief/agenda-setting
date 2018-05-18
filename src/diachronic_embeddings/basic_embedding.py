import sys
sys.path.append("..")

from article_utils import *
import argparse
from gensim.models import Word2Vec
from utils import *

def main():

    files = "/usr1/home/anjalief/corpora/russian/yearly_mod_subs/iz_lower/*.txt.tok"
    model_name = "/usr1/home/anjalief/word_embed_cache/all_train.model"

    sentence_iter = SentenceIter(files, verbose=False)
    base_model = Word2Vec(sentence_iter, size=300, window=5, min_count=100, workers=6, sg=1)

    fp = open(model_name, "wb")
    base_model.save(fp)


if __name__ == "__main__":
    main()
