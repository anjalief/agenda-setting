#!/usr/bin/env python3

# Need to run diachronic_word_embeddings to create
# models before using this script

# Input: list of keywords (country names); list of positive words; list of negative words; economic indicator
# For each country, measure correlation of positive/negative words with economic indicators
# Output countries with the strongest correlations
import gensim
import argparse
from gensim.models import KeyedVectors
from diachronic_word_embeddings import YEARS, MONTHS, get_model_filename
import os
from datetime import date

from econ_utils import load_monthly_gdp, load_rtsi
from utils import *

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", default="/usr1/home/anjalief/russian_model_cache")
    parser.add_argument("--keywords", default="/usr1/home/anjalief/corpora/russian/countries.txt")
    parser.add_argument("--gdp_file", default="/usr1/home/anjalief/corpora/russian/russian_monthly_gdp.csv")
    parser.add_argument("--pos_lexicon", default="/usr1/home/anjalief/corpora/russian/ru.filtered.pos")
    parser.add_argument("--neg_lexicon", default="/usr1/home/anjalief/corpora/russian/ru.filtered.neg")
    args = parser.parse_args()

    keywords = set(load_file(args.keywords))
    pos_words = []
    neg_words = []

    if args.pos_lexicon:
        pos_words = load_file(args.pos_lexicon)

    if args.neg_lexicon:
        neg_words = load_file(args.neg_lexicon)

    keyword_to_score_sequence = {}

    date_seq = []
    for year in YEARS:
        for month in MONTHS:
            model_name = get_model_filename(args.model_path, year, month)
            wv = KeyedVectors.load(model_name)
            date_seq.append(date(int(year), int(month), 1))

            # flip sign on distance to negative words
            # we're measuring if the keyword is close to positive words and far from negative words
            # Then, a positive correlation with economic indicator means
            # We talk about this country more positively in good economic times
            # We expected to see positive correlations for U.S. and negative correlations for Russia
            # (i.e. as Russia does worse, we talk more about how great Russia is and how bad
            # everywhere else is)
            def process_step(keyword, context_words, sign):
                if not keyword in wv:
                    print ("NO EMBEDDING FOR COUNTRY", keyword)
                    return False
                total_sim = 0
                word_count = len(context_words)
                for w in context_words:
                    if not w in wv:
                        word_count -= 1
                        continue
                    total_sim += wv.similarity(keyword, w)
                return (float(total_sim) / word_count) * sign

            to_remove = set()
            for keyword in keywords:
                pos = process_step(keyword, pos_words, 1)

                # we're missing this country
                if not pos:
                    to_remove.add(keyword)
                    continue

                neg = process_step(keyword, neg_words, -1)
                l = keyword_to_score_sequence.get(keyword, [])
                l.append(pos + neg)
                keyword_to_score_sequence[keyword] = l
            # skip countries that are not in vocab
            for c in to_remove:
                keywords.remove(c)
                assert not c in keyword_to_score_sequence

    # TODO calculate correlations
    for c in keyword_to_score_sequence:
        assert len(keyword_to_score_sequence[c]) == len(date_seq), \
            str(keyword_to_score_sequence[c]) + " " + str(date_seq)

    if args.gdp_file:
        date_to_gdp = load_monthly_gdp(args.gdp_file)
        gdp_seq = [date_to_gdp[d] for d in date_seq]

        corrs = []
        for k in keyword_to_score_sequence:
            corr = get_corr(keyword_to_score_sequence[k], gdp_seq)
            corrs.append((corr,k))

        corrs.sort(key=lambda x: x[0])

        print ("TOP", corrs[:10])
        print ()
        print ("BOTTOM", corrs[-10:])
        print ()



if __name__ == "__main__":
    main()
