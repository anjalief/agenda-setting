#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gensim.models import Word2Vec, KeyedVectors
import argparse
from parse_frames import do_counts, words_to_pmi, seeds_to_real_lex
from data_iters import FrameAnnotationsIter, BackgroundIter, get_sentence_level_test, load_json_as_list, load_codes, get_random_split, code_to_short_form, get_per_frame_split, FrameHardSoftIter
import os
from collections import Counter, defaultdict
import pickle
from random import shuffle
import operator
from scipy import spatial
import glob

from nltk.corpus import stopwords
stop_words = stopwords.words('english')
stop_words.append("''")
stop_words.append('``')
stop_words.append('--')
stop_words.append("'s")
stop_words.append("n't")
stop_words.append("said")
import string

VOCAB_SIZE = 50000
MIN_COUNT = 25
TO_RETURN_COUNT = 250
VEC_SEARCH = 250
SIM_THRESH = 0.5
LEX_COUNT = 4

def get_top_words(input_file):
    dir_name = os.path.basename(os.path.dirname(os.path.dirname(input_file)))
    base_name = os.path.join("cache", dir_name + ".counter")
    if (os.path.isfile(base_name)):
        return pickle.load(open(base_name, "rb"))

    c = Counter()
    num_sent = 0
    for words in BackgroundIter(glob.iglob(input_file)):
        c.update(words)
        num_sent += 1
    pickle.dump(c, open(base_name, "wb"))
    return c

# Theory that some frames we model better than others because they are less relavent to
# test text. Count how frequent each frame is in input text
def count_frames(code_to_str, frame_iter):
    frame_counter = Counter()
    text_count = 0
    for text,frames,_ in frame_iter:
        for frame in frames:
            frame_counter[frame] += 1
        text_count += 1

    for f in sorted(frame_counter):
        print(code_to_str[f], ";", frame_counter[f])

# NEW WAY -- train on top of NYT model
def get_wv_nyt_name(input_file, split_type):
    if split_type == "random" or split_type == 'kfold':
        base_name = "./cache/nyt_mfc.model"
    else:
        base_name = os.path.join("cache", split_type + ".nyt.model")

    nyt_model = "cache/nyt_base.model"

    if (os.path.isfile(base_name)):
        return base_name

    sentence_iter = BackgroundIter(glob.iglob(input_file), verbose=False)
    base_model = Word2Vec.load(nyt_model)
    count = 0
    for x in sentence_iter:
      count += 1
    base_model.train(sentence_iter, total_examples=count, epochs=base_model.epochs)

    fp = open(base_name, "wb")
    base_model.wv.save(fp)
    fp.close()

    return base_name

class frameTracker():
  def __init__(self):
    self.correct_positive = 0
    self.marked_positive = 0
    self.true_positive = 0
    self.marked_correct = 0

  def get_metrics(self, total):
    # return precision, recall, accuracy
    return self.correct_positive / max(float(self.marked_positive), 0.0001), \
           self.correct_positive / float(self.true_positive),   \
           self.marked_correct / float(total)

def test_primary_frame(code_to_lex, code_to_str, text_iter):
    total = 0
    correct = 0
    del code_to_lex[15.0] # Don't guess Other
    for text,_,true_frame in text_iter:
        if true_frame == "null" or true_frame is None:
            continue
        total += 1
        text_counter = Counter(text)

        sums = []
        for f in code_to_lex:
            sums.append((f, sum([text_counter[w] for w in code_to_lex[f]])))

        # we shuffle so that ties are randomly broken
        shuffle(sums)
        frame, word_count = max(sums, key=operator.itemgetter(1))
        # Mark as "Other" if it doesn't belong to any other frame
        if word_count < 4:
            frame = 15.0
        if frame == true_frame:
            correct += 1

    print (float(correct) / float(total), total)


# Find center of a set of vectors (unnormalized)
# by summing the vectors
def get_center(words, wv):
    embed_size = 0
    for w in words:
        if not w in wv:
            continue
        embed_size = len(wv[w])
        break
    center = [0 for i in range(0, embed_size)]

    for w in words:
        if not w in wv:
            continue
        center = [x+y for x,y in zip(center, wv[w])]
    return center

# First find center of context_words vectors, then return similarity between keyword and center
def get_mean_similarity(keywords, context_words, wv):
    context_center = get_center(context_words, wv)
    keywords_center = get_center(keywords, wv)
    return 1 - spatial.distance.cosine(context_center, keywords_center)

def test_primary_frame_wv(code_to_lex, code_to_str, text_iter, wv):
    total = 0
    correct = 0
    for text,_,true_frame in text_iter:
        if true_frame == "null" or true_frame is None:
            continue

        total += 1

        sums = []
        for f in code_to_lex:
            sums.append((f, get_mean_similarity(text, code_to_lex[f], wv)))

        # we shuffle so that ties are randomly broken
        shuffle(sums)
        frame, word_count = max(sums, key=operator.itemgetter(1))
        if frame == true_frame:
            correct += 1

    print (float(correct) / float(total), total)

def max_index(l):
    index, value = max(enumerate(l), key=operator.itemgetter(1))
    return str(index)


def test_sentence_annotations(code_to_lex, code_to_str, frame_to_contains, frame_to_doesnt):
    for f in sorted(code_to_lex):
        frame_tracker = frameTracker()
        total = 0

        for contains in frame_to_contains[f]:
            total += 1
            frame_tracker.true_positive += 1

            text_counter = Counter(contains)

            applies_frame = sum([text_counter[w] for w in code_to_lex[f]]) >= 1
            if applies_frame:
                frame_tracker.marked_correct += 1
                frame_tracker.marked_positive += 1
                frame_tracker.correct_positive += 1

        for doesnt in frame_to_doesnt[f]:
            total += 1
            text_counter = Counter(doesnt)
            applies_frame = sum([text_counter[w] for w in code_to_lex[f]]) >= 1
            if applies_frame:
                frame_tracker.marked_positive += 1
            else:
                frame_tracker.marked_correct += 1

        assert (frame_tracker.true_positive == len(frame_to_contains[f]))
        assert (total == len(frame_to_contains[f]) + len(frame_to_doesnt[f]))

        p,r,a = frame_tracker.get_metrics(total)
        if (p + r) == 0:
            print(code_to_str[f], "VERB BAD")
            continue
        print (code_to_str[f], ";",
           p, ";",
           r, ";",
           (2 * (p * r)/(p + r)), ";",
           a, ";")

def test_annotations(code_to_lex, code_to_str, frame_iter, lex_count=3, do_print=True):
  code_to_frame_tracker = {}
  for c in code_to_lex:
    code_to_frame_tracker[c] = frameTracker()

  total = 0
  for text,frames,_ in frame_iter:
    total += 1
    text_counter = Counter(text)

    for c in code_to_lex:
      applies_frame = (sum([text_counter[w] for w in code_to_lex[c]]) >= lex_count)

      gold_applies_frame = (c in frames)

      if applies_frame == gold_applies_frame:
        code_to_frame_tracker[c].marked_correct += 1

      if applies_frame:
        code_to_frame_tracker[c].marked_positive += 1
        if gold_applies_frame:
          code_to_frame_tracker[c].correct_positive += 1

      if gold_applies_frame:
        code_to_frame_tracker[c].true_positive += 1

  for c in sorted(code_to_frame_tracker):
    p,r,a = code_to_frame_tracker[c].get_metrics(total)
    if (p + r) == 0:
      print ("VERB BAD")
      return
    if do_print:
        print (code_to_str[c], ";",
               p, ";",
               r, ";",
               (2 * (p * r)/(p + r)), ";",
               a, ";")
    else:
        return (2 * (p * r)/(p + r))

def test_hard_annotations(code_to_lex, code_to_str, frame_iter, lex_count=3):
  code_to_frame_tracker = {}
  for c in code_to_lex:
    code_to_frame_tracker[c] = frameTracker()

  total = 0
  for text,frame_to_all, frame_to_any in frame_iter:
    total += 1
    text_counter = Counter(text)

    for c in code_to_lex:
      applies_frame = (sum([text_counter[w] for w in code_to_lex[c]]) >= lex_count)

      # Check hard, it's only in doc if all annotators think it's in doc
      gold_applies_frame = frame_to_all[c]

      if applies_frame == gold_applies_frame:
        code_to_frame_tracker[c].marked_correct += 1

      if applies_frame:
        code_to_frame_tracker[c].marked_positive += 1
        if gold_applies_frame:
          code_to_frame_tracker[c].correct_positive += 1

      if gold_applies_frame:
        code_to_frame_tracker[c].true_positive += 1

  for c in sorted(code_to_frame_tracker):
    p,r,a = code_to_frame_tracker[c].get_metrics(total)
    if (p + r) == 0:
      print ("VERB BAD")
      return
    print (code_to_str[c], ";",
           p, ";",
           r, ";",
           (2 * (p * r)/(p + r)), ";",
           a, ";")

def get_data_split(split_type, frame = None):

  if split_type == 'tobacco':
      train_files = ["/usr1/home/anjalief/corpora/media_frames_corpus/immigration.json",
                     "/usr1/home/anjalief/corpora/media_frames_corpus/samesex.json"]
      test_files = "/usr1/home/anjalief/corpora/media_frames_corpus/tobacco.json"
      test_background = "/usr1/home/anjalief/media_frames_corpus/parsed/smoking/json/*.json"

  elif split_type == 'immigration':
      train_files = ["/usr1/home/anjalief/corpora/media_frames_corpus/tobacco.json",
                     "/usr1/home/anjalief/corpora/media_frames_corpus/samesex.json"]
      test_files = "/usr1/home/anjalief/corpora/media_frames_corpus/immigration.json"
      test_background = "/usr1/home/anjalief/media_frames_corpus/parsed/immigration/json/*.json"

  elif split_type == 'samesex':
      train_files = ["/usr1/home/anjalief/corpora/media_frames_corpus/tobacco.json",
                     "/usr1/home/anjalief/corpora/media_frames_corpus/immigration.json"]
      test_files = "/usr1/home/anjalief/corpora/media_frames_corpus/samesex.json"
      test_background = "/usr1/home/anjalief/media_frames_corpus/parsed/samesex/json/*.json"
  elif split_type == 'kfold':
      train_files = ["/usr1/home/anjalief/corpora/media_frames_corpus/tobacco.json",
                     "/usr1/home/anjalief/corpora/media_frames_corpus/immigration.json",
                     "/usr1/home/anjalief/corpora/media_frames_corpus/samesex.json"]
      test_background = "/usr1/home/anjalief/media_frames_corpus/parsed/*/json/*.json"
      assert(frame is not None)
      test_data, train_data = get_per_frame_split(train_files, frame)
      return train_data, test_data, test_background
  else:
      assert (split_type == "random")
      train_files = ["/usr1/home/anjalief/corpora/media_frames_corpus/tobacco.json",
                     "/usr1/home/anjalief/corpora/media_frames_corpus/immigration.json",
                     "/usr1/home/anjalief/corpora/media_frames_corpus/samesex.json"]
      test_background = "/usr1/home/anjalief/media_frames_corpus/parsed/*/json/*.json"

      test_data, train_data = get_random_split(train_files)
      return train_data, test_data, test_background

  train_data = load_json_as_list(train_files)
  test_data = load_json_as_list([test_files])

  return train_data, test_data, test_background

def count_all_frames():
    train_files = ["/usr1/home/anjalief/corpora/media_frames_corpus/tobacco.json",
                   "/usr1/home/anjalief/corpora/media_frames_corpus/immigration.json",
                   "/usr1/home/anjalief/corpora/media_frames_corpus/samesex.json"]
    code_to_str = load_codes("/usr1/home/anjalief/corpora/media_frames_corpus/codes.json")
    train_data = load_json_as_list(train_files)
    doc_level_iter = FrameAnnotationsIter(train_data)
    count_frames(code_to_str, doc_level_iter)

def do_all(args, train_data, test_data, test_background, code_to_str, target_frame = None):
    wv_name = get_wv_nyt_name(test_background, args.split_type)
    print ("Done Loading Word Vectors")

    # we don't want to seed off of very infrequent words; limit vocab to common words
    top_words = get_top_words(test_background)
    vocab = sorted(top_words, key=top_words.get, reverse = True)[:VOCAB_SIZE]

    corpus_counter, code_to_counter = do_counts(train_data)
    print ("Done Corpus Counts")

    # Sometimes (kfold) we only care about 1 frame
    if target_frame is not None:
        code_to_counter = {f:code_to_counter[f] for f in [target_frame]}

    # cut infrequent words
    corpus_counter = Counter({c:corpus_counter[c] for c in corpus_counter if corpus_counter[c] > MIN_COUNT})

    # if baseline, cut most frequent words
    if args.baseline:
        topfive_num = int(len(corpus_counter) / 10)
        top_five = set([q[0] for q in corpus_counter.most_common(topfive_num)])
        print("CUT", topfive_num, top_five)
        corpus_counter = Counter({c:corpus_counter[c] for c in corpus_counter if not c in top_five})

    # calculate PMI
    corpus_count = sum([corpus_counter[k] for k in corpus_counter])
    code_to_lex = {}
    all_frames = set()
    for c in code_to_counter:
        if "primary" in code_to_str[c] or "headline" in code_to_str[c] or "primany" in code_to_str[c]:
            continue

        all_frames.add(c)
        # For the baseline, we just take 100 most frequent words
        if args.baseline:
            # remove stopwords
            code_to_counter[c] = Counter({w:code_to_counter[c][w] for w in code_to_counter[c] if w in corpus_counter and not w in stop_words and not w in string.punctuation})
            code_to_lex[c] = [q[0] for q in code_to_counter[c].most_common(100)]
        else:
            code_to_lex[c] = words_to_pmi(corpus_counter, corpus_count, code_to_counter[c], TO_RETURN_COUNT)
            # # Use same seeds as baseline
            # code_to_counter[c] = Counter({w:code_to_counter[c][w] for w in code_to_counter[c] if w in corpus_counter and not w in stop_words and not w in string.punctuation})
            # code_to_lex[c] = [q[0] for q in code_to_counter[c].most_common(100)]

    print("*******************************************************************************")
    for c in code_to_lex:
        print (code_to_str[c], code_to_lex[c])
    print("*******************************************************************************")
    print("*******************************************************************************")

    if args.baseline:
      code_to_new_lex = code_to_lex
    else:
      code_to_new_lex = {}
      for c in code_to_lex:
          # try:
              code_to_new_lex[c] = seeds_to_real_lex(code_to_lex[c], wv_name, vocab, code_to_str[c], topn=VEC_SEARCH, threshold=SIM_THRESH)
          # except:
          #     print("Skipping", code_to_str[c])


    # make data iters
    doc_level_iter = FrameAnnotationsIter(test_data)
    short_codes = set([code_to_short_form(code) for code in code_to_str])
    hard_iter = FrameHardSoftIter(test_data, short_codes)
    # sentence level tests
    frame_to_contains, frame_to_doesnt = get_sentence_level_test(test_data, all_frames)


    for x in code_to_new_lex:
        print (code_to_str[x])
        print (code_to_new_lex[x])
    print("*******************************************************************************")
    print("Frame Counts;")
    count_frames(code_to_str, doc_level_iter)
    print("*******************************************************************************")
    print("DOC")
    test_annotations(code_to_new_lex, code_to_str, doc_level_iter, lex_count=LEX_COUNT)
    # print("*******************************************************************************")
    # Skipping this for now
    # print("DOC HARD")
    # test_hard_annotations(code_to_new_lex, code_to_str, hard_iter)
    print("*******************************************************************************")
    print("SENTENCE")
    test_sentence_annotations(code_to_new_lex,code_to_str, frame_to_contains, frame_to_doesnt)
    print("*******************************************************************************")
    print("PRIMARY")
    test_primary_frame(code_to_new_lex, code_to_str, doc_level_iter)
    print("*******************************************************************************")
    # # Real slow and doesn't work well
    # print("PRIMARY WV")
    # test_primary_frame_wv(code_to_new_lex, code_to_str, doc_level_iter, KeyedVectors.load(wv_name))

    to_save = {}
    for x in code_to_new_lex:
      to_save[code_to_str[x]] = code_to_new_lex[x]
    pickle.dump(to_save, open("cache/" + args.split_type + "_lex.pickle", "wb"))


    to_save = {}
    for x in code_to_lex:
      to_save[code_to_str[x]] = code_to_new_lex[x]
    pickle.dump(to_save, open("cache/" + args.split_type + "_base_lex.pickle", "wb"))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", action='store_true')
    parser.add_argument("--code_file", default="/usr1/home/anjalief/corpora/media_frames_corpus/codes.json")
    # specify what to use as training data and what to use as test set. If random, hold out 20% of data of test
    # if kfold, we do a different data split for each frame, so that test and train data have same proportion
    # of the frame at the document level
    parser.add_argument("--split_type", choices=['tobacco', 'immigration', 'samesex', 'random', 'kfold'])
    args = parser.parse_args()

    code_to_str = load_codes(args.code_file)

    if args.split_type == 'kfold':
        codes = set([code_to_short_form(code) for code in code_to_str])
        codes.remove(0.0) # Skip "None"
        codes.remove(16.0) # Skip "Irrelevant
        codes.remove(17.0) # Skip tones
        codes.remove(18.0)
        codes.remove(19.0)
        for code in codes:
            print(code)

            train_data, test_data, test_background = get_data_split(args.split_type, code)
            do_all(args, train_data, test_data, test_background, code_to_str, code)
    else:
        train_data, test_data, test_background = get_data_split(args.split_type)
        do_all(args, train_data, test_data, test_background, code_to_str)


if __name__ == "__main__":
    main()
