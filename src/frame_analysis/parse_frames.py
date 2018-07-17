import sys
from scipy.spatial.distance import cosine

sys.path.append("..")
from article_utils import LoadArticles

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
from data_iters import load_codes, BackgroundIter, load_json_as_list

VOCAB_SIZE = 50000
MIN_COUNT = 25
TO_RETURN_COUNT = 250
VEC_SEARCH = 250
SIM_THRESH = 0.5
LEX_COUNT = 4

def get_article_top_words(input_file):
    dir_name = os.path.basename(os.path.dirname(os.path.dirname(input_file)))
    base_name = os.path.join("cache", dir_name + ".counter")
    if (os.path.isfile(base_name)):
        return pickle.load(open(base_name, "rb"))

    c = Counter()
    num_sent = 0
    articles, _ = LoadArticles(input_file)
    for a in articles:
        c.update(a.split())
    pickle.dump(c, open(base_name, "wb"))
    return c

# Takes in a counter over all words in corpus
# # of tokens in corpus (corpus_count)
# A counter over words in target articles
# Number of words to return
def words_to_pmi(background_counter, corpus_count, code_counter, to_return_count = 100):
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

    return sorted(word_to_pmi, key=word_to_pmi.get, reverse=True)[:to_return_count]


def seeds_to_real_lex(raw_lex, model_name, vocab, code="", topn=500, threshold=0.4):
    wv = KeyedVectors.load(model_name)
    filtered_seeds = [k for k in raw_lex if k in vocab and k in wv]

    if len(filtered_seeds) < 50:
        print ("WARNING: low seeds for code", len(filtered_seeds), code)

    expanded_seeds = [x[0] for x in wv.most_similar(positive=filtered_seeds, topn=topn) if x[1] >= threshold]
    return set(expanded_seeds + raw_lex)

from nltk.corpus import stopwords
stop_words = stopwords.words('english')
def process_text(text):
    tokenized_text = tokenize.word_tokenize(text)
    return [t for t in tokenized_text if not t.replace(",", "").replace(".","").isdigit() \
#                and t.isalpha() \
                and not t in stop_words]

# this guy wants json_text to be a list, not a dict
def do_counts(json_text):
    corpus_counter = Counter()
    code_to_counter = defaultdict(Counter)
    for annotated_file in json_text:
        assert "framing" in annotated_file["annotations"]
        if annotated_file["annotations"]["framing"] == {}:
            continue

        text = annotated_file["text"].lower()

        corpus_counter.update(process_text(text))
        for annotation_set in annotated_file["annotations"]["framing"]:
            for frame in annotated_file["annotations"]["framing"][annotation_set]:
                coded_text = text[int(frame["start"]):int(frame["end"])]
                code_to_counter[frame["code"]].update(process_text(coded_text))
            # for now just grab first annotators marks, can't decide how to incorporate both
            # and keep the background corpus reasonable
            break
    return corpus_counter, code_to_counter

def get_file_names(input_files):
    train_files = []
    code_file_name = None
    for filename in input_files:
        if "meta" in filename:
            continue
        if "code" in filename:
            code_file_name = filename
            continue
        train_files.append(filename)
    return train_files, code_file_name

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_files", default="/usr1/home/anjalief/corpora/media_frames_corpus/*.json")
    parser.add_argument("--model_name", default="/usr1/home/anjalief/word_embed_cache/all_train_v2_200.model")
    parser.add_argument("--lex_cache", default="./cache/frame_to_lex_v2_200.pickle")
    parser.add_argument("--article_glob", default="")
    parser.add_argument("--refresh", action='store_true')
    args = parser.parse_args()

    cache_filename1 = "cache/corpus_cache.pickle"
    cache_filename2 = "cache/frame_cache.pickle"
    cache_filename3 = "cache/codes_cache.pickle"

    if os.path.isfile(cache_filename1) and not args.refresh:
        corpus_counter = pickle.load(open(cache_filename1, "rb"))
        code_to_counter = pickle.load(open(cache_filename2, "rb"))
        code_to_str = pickle.load(open(cache_filename3, "rb"))
    else:
        train_files, code_file_name = get_file_names(glob.iglob(args.input_files))
        print(train_files)
        code_to_str = load_codes(code_file_name)
        train_data = load_json_as_list(train_files)
        corpus_counter, code_to_counter = do_counts(train_data)
        pickle.dump(corpus_counter, open(cache_filename1, "wb"))
        pickle.dump(code_to_counter, open(cache_filename2, "wb"))
        pickle.dump(code_to_str, open(cache_filename3, "wb"))

    # cut infrequent words
    corpus_counter = {c:corpus_counter[c] for c in corpus_counter if corpus_counter[c] > MIN_COUNT }

    # calculate PMI
    corpus_count = sum([corpus_counter[k] for k in corpus_counter])
    code_to_lex = {}
    for c in code_to_counter:
        if "primary" in code_to_str[c] or "headline" in code_to_str[c] or "primany" in code_to_str[c]:
            continue
        code_to_lex[c] = words_to_pmi(corpus_counter, corpus_count, code_to_counter[c], TO_RETURN_COUNT)

    for c in code_to_lex:
        print (code_to_str[c], code_to_lex[c])
    print ("*******************************************************************************************")

    # translate to Russian
    translator = Translator()
    for c in code_to_lex:
        cache_file = "cache/" + str(c) + ".pickle"

        if os.path.isfile(cache_file):
            code_to_lex[c] = pickle.load(open(cache_file, "rb"))
            print ("Loaded from cache", c)
            continue

        new_list = []
        for w in code_to_lex[c]:
            try:
                new_list.append(translator.translate(w, dest='ru').text)
            except:
                translator = Translator()
                print ("sleepy", w)
                time.sleep(5)
                new_list.append(translator.translate(w, dest='ru').text)
        code_to_lex[c] = new_list
        pickle.dump(new_list, open(cache_file, "wb"))

    # use word embeddings to generate lexicons
    top_words = get_article_top_words(args.article_glob)

    # we don't want to seed off of very infrequent words; limit vocab to common words
    vocab = sorted(top_words, key=top_words.get, reverse = True)[:VOCAB_SIZE]

    # Weird but the lex ends up being mostly nouns
    code_to_lex = {code_to_str[c]:seeds_to_real_lex(code_to_lex[c], args.model_name, vocab, code_to_str[c], topn=VEC_SEARCH, threshold=SIM_THRESH) for c in code_to_lex}

    for x in code_to_lex:
        print (x)
        print (code_to_lex[x], len(code_to_lex[x]))
    pickle.dump(code_to_lex, open(args.lex_cache, "wb"))


if __name__ == "__main__":
    main()
