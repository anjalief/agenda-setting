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

from collections import defaultdict

country_set = None
def is_not_country_name(keyword):
    global country_set
    if not country_set:
        lines = open("../russian_ner/cleaned.txt").readlines()
        country_set = set([l.split(",")[0].strip() for l in lines])
    return keyword not in country_set

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", default="/usr1/home/anjalief/corpora/ner_model_cache/")
    parser.add_argument("--keywords", default="./keywords.txt")
    parser.add_argument("--out_path", default="./outputs/")
    parser.add_argument('--timestep', type=str,
                        default='monthly',
                        choices=['monthly', 'quarterly', 'yearly'])
    parser.add_argument("--lexicon_size", type=int, default=100)
    args = parser.parse_args()

    # FIRST: Gather inputs. Start with keywords, datelist, and vocab words from model
    keywords = set(load_file(args.keywords))
    keywords = ["экономического"]

    date_seq, filenames = get_files_by_time_slice(
        args.model_path, args.timestep, suffix= "_" + args.timestep + ".pickle")
#    filenames = [["/usr1/home/anjalief/word_embed_cache/ner_model_cache/izvestia_quarterly/2011_7_quarterly.pickle"]]

    # model_name1 = get_model_filename(args.model_path, YEARS[0], MONTHS[0], args.timestep)
    # model1 = KeyedVectors.load(model_name1)
    # vocab = model1.index2entity
    # print(len(vocab))

    # pull vocab from model that was trained on all files
    base_model = Word2Vec.load("/usr1/home/anjalief/word_embed_cache/ner_model_cache/base_model.pickle").wv
    for file_list in filenames:
        assert (len(file_list) == 1)
        for model_name in file_list:

            wv = KeyedVectors.load(model_name)

            basename = os.path.basename(model_name)
            fp = open(os.path.join(args.out_path, basename), "w")

            vocab = [l[0] for l in wv.most_similar(positive=keywords, topn=50)]
            vocab = list(filter(is_not_country_name, vocab))
            print(len(vocab))

            for l in vocab:
                fp.write(str(l) + "\n")

            # avoid our of vocabulary error
#            vocab = wv.index2entity
            # drop country names


            # grab score form base model. Is this really the best way?
            vocab_to_score = {}
            for v in vocab:
                try:
                    vocab_to_score[v] = base_model.similarity(keywords[0], v)
                except:
                    continue

            vocab = list(filter(is_adjective, vocab))

            # grab score form base model. Is this really the best way?
            adj_to_score = {}
            for v in vocab:
                try:
                    adj_to_score[v] = base_model.similarity(keywords[0], v)
                except:
                    continue

            fp.write("\n\nADJ_LEX\n")


            adj_lex = [(k, wv.similarity(keywords[0], k)) for k in vocab]
            adj_lex.sort(key=lambda x: x[1], reverse=True)

            for a in adj_lex[0:100]:
                fp.write(str(a[0]) + "\n")

            fp.write("\n\nVOCAB_DIFF\n")

            # want the words for which the similarity in this quarter is
            # much greater than normal
            vocab_diff = [(k,wv.similarity(keywords[0], k) - vocab_to_score[k]) for k in vocab_to_score]
            vocab_diff.sort(key=lambda x: x[1], reverse=True)

            for a in vocab_diff[0:100]:
                fp.write(str(a[0]) + "\n")

            fp.write("\n\nADJ_DIFF\n")

            # want the words for which the similarity in this quarter is
            # much greater than normal
            adj_diff = [(k,wv.similarity(keywords[0], k) - adj_to_score[k]) for k in adj_to_score]
            adj_diff.sort(key=lambda x: x[1], reverse=True)

            for a in adj_diff[0:100]:
                fp.write(str(a[0]) + "\n")

            fp.close()

if __name__ == "__main__":
    main()
