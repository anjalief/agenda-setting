#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gensim.models import Word2Vec, KeyedVectors
import argparse
from parse_frames import do_counts, words_to_pmi, seeds_to_real_lex
import os
from collections import Counter, defaultdict
import pickle
from random import shuffle
import operator
from scipy import spatial

import json
from nltk import tokenize, data
sentence_tokenizer = data.load('tokenizers/punkt/english.pickle')
import glob

class FrameAnnotationsIter(object):
  def __init__(self, input_files, verbose=False):
      self.input_files = input_files
      self.verbose = verbose

  def __iter__(self):
      for filename in self.input_files:
          if self.verbose:
              print("Loading:", filename)

          json_text = json.load(open(filename))
          for annotated_file_key in json_text:
              annotated_file = json_text[annotated_file_key]
              if not "framing" in annotated_file["annotations"]:
                  continue
              text = annotated_file["text"].lower()

              # we return all frames anybody found in the sentence
              frames = set()
              for annotation_set in annotated_file["annotations"]["framing"]:
                  for frame in annotated_file["annotations"]["framing"][annotation_set]:
                      frames.add(code_to_short_form(frame["code"]))
              yield tokenize.word_tokenize(text), frames

              # for annotation_set in annotated_file["annotations"]["framing"]:
              #     for frame in annotated_file["annotations"]["framing"][annotation_set]:
              #         coded_text = text[int(frame["start"]):int(frame["end"])]
              #         yield frame["code"], tokenize.word_tokenize(coded_text)

class PrimaryFrameIter(object):
  def __init__(self, input_files, verbose=False):
      self.input_files = input_files
      self.verbose = verbose

  def __iter__(self):
      for filename in self.input_files:
          if self.verbose:
              print("Loading:", filename)

          json_text = json.load(open(filename))
          primary_frames = set()

          for annotated_file_key in json_text:
              annotated_file = json_text[annotated_file_key]

              text = annotated_file["text"].lower()
              primary_frame = annotated_file["primary_frame"]

              if primary_frame != "null" and primary_frame != None:
                yield tokenize.word_tokenize(text), code_to_short_form(primary_frame)


def code_to_short_form(frame):
  f = str(frame).split(".")
  return float(f[0] + ".0")

# This is super confusing but I think what we want is take the text
# that uses a frame and take all text that doesn't use a frame
# all text that uses frame is easy
# all text that doesn't use a frame, we can either take annotated spans,
# or we can take sentences. Let's take sentences
def get_sentence_level_test(input_files, all_frames, verbose=False):
    frame_to_contains = defaultdict(list)
    frame_to_doesnt = defaultdict(list)
    for filename in input_files:
          if verbose:
              print("Loading:", filename)

          json_text = json.load(open(filename))
          for annotated_file_key in json_text:
              annotated_file = json_text[annotated_file_key]
              if not "framing" in annotated_file["annotations"]:
                  continue
              text = annotated_file["text"].lower()

              # the tokenizer cuts some whitespace. We're just going to go with . divisions
              # I think that's sufficient for testing
              # sentences = sentence_tokenizer.tokenize(text)
              sentences = [s + "." for s in text.replace("?",".").replace("!",".").split('.')]
              # last sentence might not have a period
              if sentences[-1][-1] != text[-1]:
                sentences[-1] = sentences[-1][:-1]
              q = sum([len(s) for s in sentences])
              assert(q == len(text)), str(q) + " " + str(len(text)) + " " + str(len(sentences))


              start_idx = 0
              for s in sentences:
                  end_idx = start_idx + len(s)

                  frames_in_sentence = set()

                  for annotation_set in annotated_file["annotations"]["framing"]:
                      for frame in annotated_file["annotations"]["framing"][annotation_set]:
                          code = code_to_short_form(frame["code"])

                          # easy part we KNOW this text uses this frame
                          # only add it once
                          frame_start = int(frame["start"])
                          frame_end = int(frame["end"])
                          if start_idx == 0:
                              coded_text = text[frame_start:frame_end]
                              frame_to_contains[code].append(tokenize.word_tokenize(coded_text))

                          # if either the start or end are inside the text, then we have overlap
                          if (frame_start >= start_idx and frame_start < end_idx) or \
                             (frame_end >= start_idx and frame_end < end_idx):
                              frames_in_sentence.add(code)

                  if verbose:
                      print(s, frames_in_sentence)
                  for f in all_frames:
                      if not f in frames_in_sentence:
                          frame_to_doesnt[f].append(tokenize.word_tokenize(s))

                  start_idx = end_idx # move to next sentence
              assert end_idx == len(text), str(end_idx) + " " + str(len(text))
    return frame_to_contains, frame_to_doesnt


class BackgroundIter(object):
  def __init__(self, input_files, verbose=False):
      self.input_files = input_files
      self.verbose = verbose

  def __iter__(self):
      for filename in self.input_files:
          if self.verbose:
              print("Loading:", filename)

          json_text = json.load(open(filename))
          for sentence in json_text["BODY"]:
              yield tokenize.word_tokenize(sentence.lower())

# NEW WAY -- train on top of NYT model
def get_wv_nyt_name(input_file):
    dir_name = os.path.basename(os.path.dirname(os.path.dirname(input_file)))
    base_name = os.path.join("cache", dir_name + ".nyt.model")
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

# OLD WAY (not enough data?)
def get_wv_model_name(input_file):
    dir_name = os.path.basename(os.path.dirname(os.path.dirname(input_file)))
    base_name = os.path.join("cache", dir_name + ".model")

    if (os.path.isfile(base_name)):
        return base_name

    sentence_iter = BackgroundIter(glob.iglob(input_file), verbose=False)
    base_model = Word2Vec(sentence_iter, size=200, window=5, min_count=100, workers=10)

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

def test_primary_frame(code_to_lex, code_to_str, test_file):
    text_iter = PrimaryFrameIter([test_file])

    total = 0
    correct = 0
    for text,true_frame in text_iter:
        total += 1
        text_counter = Counter(text)

        sums = []
        for f in code_to_lex:
            sums.append((f, sum([text_counter[w] for w in code_to_lex[f]])))

        # we shuffle so that ties are randomly broken
        shuffle(sums)
        frame, word_count = max(sums, key=operator.itemgetter(1))
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

def test_primary_frame_wv(code_to_lex, code_to_str, test_file, wv):
    text_iter = PrimaryFrameIter([test_file])

    total = 0
    correct = 0
    for text,true_frame in text_iter:
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


def test_sentence_annotations(code_to_lex, code_to_str, test_file, all_frames):
    frame_to_contains, frame_to_doesnt = get_sentence_level_test([test_file], all_frames, verbose=False)

    for f in code_to_lex:
#        print(f, len(frame_to_contains[f]), len(frame_to_doesnt[f]))
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
        print (code_to_str[f], ";",
           p, ";",
           r, ";",
           (2 * (p * r)/(p + r)), ";",
           a, ";")

  # for f in frame_to_contains:
  #   print(code_to_str[f], len(frame_to_contains[f]))
  #   print(code_to_str[f], len(frame_to_doesnt[f]))

def test_annotations(code_to_lex, code_to_str, test_file):
  code_to_frame_tracker = {}
  for c in code_to_lex:
    code_to_frame_tracker[c] = frameTracker()

  total = 0
  for text, frames in FrameAnnotationsIter([test_file]):
    total += 1
    text_counter = Counter(text)

    for c in code_to_lex:
      applies_frame = (sum([text_counter[w] for w in code_to_lex[c]]) >= 2)

      gold_applies_frame = (c in frames)

      if applies_frame == gold_applies_frame:
        code_to_frame_tracker[c].marked_correct += 1

      if applies_frame:
        code_to_frame_tracker[c].marked_positive += 1
        if gold_applies_frame:
          code_to_frame_tracker[c].correct_positive += 1

      if gold_applies_frame:
        code_to_frame_tracker[c].true_positive += 1

  for c in code_to_frame_tracker:
    p,r,a = code_to_frame_tracker[c].get_metrics(total)
    print (code_to_str[c], ";",
           p, ";",
           r, ";",
           (2 * (p * r)/(p + r)), ";",
           a, ";")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_files", action='append', default=["/usr1/home/anjalief/corpora/media_frames_corpus/immigration.json", "/usr1/home/anjalief/corpora/media_frames_corpus/samesex.json", "/usr1/home/anjalief/corpora/media_frames_corpus/codes.json"])
    parser.add_argument("--test_file", default="/usr1/home/anjalief/corpora/media_frames_corpus/tobacco.json")
    parser.add_argument("--test_background", default="/usr1/home/anjalief/media_frames_corpus/parsed/smoking/json/*.json")
    parser.add_argument("--baseline", action='store_true')
    args = parser.parse_args()

    wv_name = get_wv_nyt_name(args.test_background)
    # wv = KeyedVectors.load(wv_name)
    # for k in wv.index2entity:
    #   print(k)
    print ("Done Loading Word Vectors")

    # we don't want to seed off of very infrequent words; limit vocab to common words
    top_words = get_top_words(args.test_background)
    vocab = sorted(top_words, key=top_words.get, reverse = True)[:50000]


    corpus_counter, code_to_counter, code_to_str = do_counts(args.train_files)
    print ("Done Corpus Counts")


    # cut infrequent words
    corpus_counter = {c:corpus_counter[c] for c in corpus_counter if corpus_counter[c] > 50 }


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
            code_to_lex[c] = [q[0] for q in code_to_counter[c].most_common(100)]
        else:
            code_to_lex[c] = words_to_pmi(corpus_counter, corpus_count, code_to_counter[c])

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
          try:
              code_to_new_lex[c] = seeds_to_real_lex(code_to_lex[c], wv_name, vocab, code_to_str[c])
          except:
              print("Skipping", code_to_str[c])


    # for x in code_to_new_lex:
    #     print (code_to_str[x])
    #     print (code_to_new_lex[x])
    # print("*******************************************************************************")
    # print("DOC")
    # test_annotations(code_to_new_lex, code_to_str, args.test_file)
    # print("*******************************************************************************")
    # print("SENTENCE")
    # test_sentence_annotations(code_to_new_lex,code_to_str, args.test_file, all_frames)
    # print("*******************************************************************************")
    # print("PRIMARY")
    # test_primary_frame(code_to_new_lex, code_to_str, args.test_file)
    print("*******************************************************************************")
    print("PRIMARY WV")
    test_primary_frame_wv(code_to_new_lex, code_to_str, args.test_file, KeyedVectors.load(wv_name))

    to_save = {}
    for x in code_to_new_lex:
      to_save[code_to_str[x]] = code_to_new_lex[x]
    pickle.dump(to_save, open("cache/tobacco_lex.pickle", "wb"))



    to_save = {}
    for x in code_to_lex:
      to_save[code_to_str[x]] = code_to_new_lex[x]
    pickle.dump(to_save, open("cache/tobacco_base_lex.pickle", "wb"))




if __name__ == "__main__":
    main()
