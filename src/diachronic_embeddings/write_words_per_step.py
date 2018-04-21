# Need to run diachronic_word_embeddings to create
# models before using this script

# Input: list of keywords (country names)
# Output: For each timestep in models, write files with lexicon
import gensim
import argparse
from gensim.models import KeyedVectors
from diachronic_word_embeddings import YEARS, MONTHS, get_model_filename
import os
from datetime import date
from econ_utils import load_monthly_gdp, load_rtsi
from utils import *

from collections import defaultdict


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", default="/usr1/home/anjalief/russian_model_cache")
    parser.add_argument("--keywords", default="/usr1/home/anjalief/corpora/russian/us_countries.txt")
    parser.add_argument("--out_path", default="./outputs/us_per_step_")
    parser.add_argument("--lexicon_size", type=int, default=100)
    args = parser.parse_args()

    # FIRST: Gather inputs. Start with keywords, datelist, and vocab words from model
    keywords = set(load_file(args.keywords))

    # only pull vocab words that appear in first model. They (and only they) should appear in all models
    model_name1 = get_model_filename(args.model_path, YEARS[0], MONTHS[0])
    vocab = KeyedVectors.load(model_name1).index2entity

    # skip countries that are not in vocab
    for k in keywords:
        if not k in vocab:
            print ("MISSING COUNTRY", k)
    keywords = [k for k in keywords if k in vocab]

    for year in YEARS:
        for month in MONTHS:
            model_name = get_model_filename(args.model_path, year, month)
            wv = KeyedVectors.load(model_name)

            fp = open(args.out_path + year + "_" + month, "w")


            lex = wv.most_similar(positive=keywords, negative=["Россия"], topn=100)
            for l in lex:
                fp.write(str(l) + "\n")
            fp.close()

if __name__ == "__main__":
    main()
