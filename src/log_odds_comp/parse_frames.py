import sys
sys.path.append("../diachronic_embeddings")
from get_top_words import get_top_words
from utils import get_center

from scipy.spatial.distance import cosine

import json
import argparse
import glob
from collections import Counter, defaultdict
import math
from nltk import tokenize
from googletrans import Translator
import time
import pickle
import os
from gensim.models import KeyedVectors, Word2Vec

def load_codes(filename):
    str_to_code = json.load(open(filename))
    return {float(k) : str_to_code[k] for k in str_to_code}

def words_to_pmi(background_counter, corpus_count, code_counter):
    frame_count = sum([code_counter[k] for k in code_counter])

    word_to_pmi = {}
    for word in code_counter:
        # means it is a partial word or is infrequent
        if not word in background_counter:
            continue
        # number of times word appears with this frame
        # divide by number of words in frame = p( y | x)
        p_y_x = code_counter[word] / float(frame_count)
        # number of times word appears at all / number of words in corpus = p(y)
        p_y = background_counter[word] / float(corpus_count)

        assert (p_y_x > 0 and p_y_x < 1), str(p_y_x) + " " +  word
        assert (p_y > 0 and p_y < 1), str(p_y) + " " +  word

        word_to_pmi[word] = math.log(p_y_x / p_y)

    return sorted(word_to_pmi, key=word_to_pmi.get, reverse=True)[:100]


def seeds_to_real_lex(raw_lex, model_name, vocab):
    wv = KeyedVectors.load(model_name)
    filtered_seeds = [k for k in raw_lex if k in vocab and k in wv]

    if len(filtered_seeds) < 50:
        print ("WARNING: low seeds for code", len(filtered_seeds))

    expanded_seeds = [x[0] for x in wv.most_similar(positive=filtered_seeds, topn=200)]
    final_lex = [k for k in expanded_seeds if k in vocab]
    return final_lex

# Alternative idea: for each word in seed, take 10 NN and then
# keep words closest to center of lex
def seeds_to_real_lex_v2(raw_lex, model_name, vocab):
    wv = KeyedVectors.load(model_name)
    filtered_seeds = [k for k in raw_lex if k in vocab and k in wv]

    if len(filtered_seeds) < 50:
        print ("WARNING: low seeds for code", len(filtered_seeds))

    expanded_seeds = set()
    for k in filtered_seeds:
        for x in wv.most_similar(positive=filtered_seeds, topn=100):
            expanded_seeds.add(x[0])

    center = get_center(expanded_seeds, wv, len(wv[vocab[0]]))

    # return closest -- smallest distance
    final_lex = sorted(expanded_seeds, key=lambda x: cosine(center, wv[x]))
    return final_lex[:300]

def do_counts(input_files):
    corpus_counter = Counter()
    code_to_counter = defaultdict(Counter)
    for filename in glob.iglob(input_files):
        if "meta" in filename:
            continue
        if "code" in filename:
            code_to_str = load_codes(filename)
            continue
        json_text = json.load(open(filename))
        for annotated_file_key in json_text:
            annotated_file = json_text[annotated_file_key]
            if not "framing" in annotated_file["annotations"]:
                continue
            text = annotated_file["text"].lower()
            # I think what we're doing with this is if two annotators mark the text, we add
            # it to the counts twice. That's ok, we're more sure this is the right frame
            # if two people marked it
            corpus_counter.update(tokenize.word_tokenize(text)) # Might want to add uncoded text to counter?
            for annotation_set in annotated_file["annotations"]["framing"]:
                for frame in annotated_file["annotations"]["framing"][annotation_set]:
                    coded_text = text[int(frame["start"]):int(frame["end"])]
#                    corpus_counter.update(coded_text) # if we include marks from multiple annotators, need to do something here
                    code_to_counter[frame["code"]].update(tokenize.word_tokenize(coded_text))
                # for now just grab first annotators marks, can't decide how to incorporate both
                # and keep the background corpus reasonable
                break
    return corpus_counter,code_to_counter,code_to_str

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_files", default="/usr1/home/anjalief/corpora/media_frames_corpus/*.json")
    parser.add_argument("--model_name", default="/usr1/home/anjalief/word_embed_cache/yearly_mods/lowercased_more_years/2016_1_yearly.pickle")
    parser.add_argument("--article_glob", default="")
    parser.add_argument("--refresh", action='store_true')
    args = parser.parse_args()

    cache_filename1 = "corpus_cache.pickle"
    cache_filename2 = "frame_cache.pickle"
    cache_filename3 = "codes_cache.pickle"

    if os.path.isfile(cache_filename1) and not args.refresh:
        corpus_counter = pickle.load(open(cache_filename1, "rb"))
        code_to_counter = pickle.load(open(cache_filename2, "rb"))
        code_to_str = pickle.load(open(cache_filename3, "rb"))
    else:
        corpus_counter, code_to_counter,code_to_str = do_counts(args.input_files)
        pickle.dump(corpus_counter, open(cache_filename1, "wb"))
        pickle.dump(code_to_counter, open(cache_filename2, "wb"))
        pickle.dump(code_to_str, open(cache_filename3, "wb"))

    # cut infrequent words
    corpus_counter = {c:corpus_counter[c] for c in corpus_counter if corpus_counter[c] > 50 }

    # calculate PMI
    corpus_count = sum([corpus_counter[k] for k in corpus_counter])
    code_to_lex = {}
    for c in code_to_counter:
        if "primary" in code_to_str[c] or "headline" in code_to_str[c] or "primany" in code_to_str[c]:
            continue
        code_to_lex[c] = words_to_pmi(corpus_counter, corpus_count, code_to_counter[c])


    # translate to Russian
    translator = Translator()
    for c in code_to_lex:
        cache_file = str(c) + ".pickle"

        if os.path.isfile(cache_file):
            code_to_lex[c] = pickle.load(open(cache_file, "rb"))
            print ("Loaded from cache", c)
            continue

        new_list = []
        for w in code_to_lex[c]:
            try:
                new_list.append(translator.translate(w, dest='ru').text)
            except:
                print ("sleepy")
                time.sleep(5)
                new_list.append(translator.translate(w, dest='ru').text)
        code_to_lex[c] = new_list
        pickle.dump(new_list, open(cache_file, "wb"))

    # use word embeddings to generate lexicons
    _,_,top_words = get_top_words(args.article_glob)

    # we don't want to seed off of very infrequent words; limit vocab to common words
    vocab = sorted(top_words, key=top_words.get, reverse = True)[:50000]

    # Weird but the lex ends up being mostly nouns
    code_to_lex = {code_to_str[c]:seeds_to_real_lex(code_to_lex[c], args.model_name, vocab) for c in code_to_lex}

    print(code_to_lex)
    pickle.dump(code_to_lex, open("frame_to_lex.pickle", "wb"))


if __name__ == "__main__":
    main()
