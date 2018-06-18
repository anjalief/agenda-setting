from datetime import date
import argparse
from collections import defaultdict, Counter
import os
import sys
sys.path.append("..")
from article_utils import *
from get_dates import *

BIGRAMS=False
LIMIT=False

import pickle

##########################################################################################################
# Different metrics for splitting internal/external
# All must return counter, is_external, is_internal
##########################################################################################################

# Treat articles that mention USA at least 2 times as external
# [Note that we got good p-values when we took articles that mention USA at least
# 2 times and weighted by word counts]
# [We actually got even better p-values with articles that mention USA 3 times, should we use these?]
# Treat articles that don't mention USA as internal
def USAvsNonUSA(words):
  counter = make_counter(words)
  return counter, counter["USA"] >= 2, counter["USA"] == 0

# Treat articles that mention USA at least 2 times as external
# Treat articles that don't mention another other country more than once as internal
def USAvsNone(words, keywords):
  counter = make_counter(words)
  return counter, counter["USA"] >= 2, sum([counter[x] for x in keywords]) <= 1

# Treat articles that mention at least 3 other countries as external
# Treat articles that mention 1 or fewer counteries as internal
def OtherCountries(words, keywords):
  counter = make_counter(words)
  count_external = sum([counter[x] for x in keywords])

  return counter, count_external > 2, count_external < 2

##########################################################################################################

def make_counter(words):
  len_words = len(words)
  if BIGRAMS:
    for i in range(0, len_words - 2):
      words.append(words[i] + " " + words[i + 1])
  return Counter(words)

def LoadCountsExternal(filenames, keywords):
  external_dict = Counter()
  internal_dict = Counter()
  external_count = 0
  internal_count = 0
  total_article_count = 0

  for filename in filenames:
      articles,_ = LoadArticles(filename, verbose=False)
      for article in articles:
          total_article_count += 1

          words = article.split()
          counter, is_external, is_internal = USAvsNone(words, keywords)

          # Something should never be both internal and external
          assert (not (is_external and is_internal))

          if is_external:
            external_count += 1
            external_dict.update(counter)

          elif is_internal:
            internal_count += 1
            internal_dict.update(counter)

  return external_dict, internal_dict, external_count, internal_count, total_article_count

# We use all filenames
def LoadBackgroundCorpus(input_path, timestep = "monthly", cache_file_name = "background_cache.pickle"):

  if os.path.isfile(cache_file_name):
    return pickle.load(open(cache_file_name, "rb"))

  _,all_files = get_files_by_time_slice(input_path, timestep)

  word_to_count = Counter()
  for filenames in all_files:
    for filename in filenames:
      articles, _ = LoadArticles(filename)
      for article in articles:
        words = article.split()
        word_to_count.update(make_counter(words))

  pickle.dump(word_to_count, open(cache_file_name, "wb"))
  return word_to_count


def LoadSingleCorpus(files):
  word_to_count = Counter()
  for filename in files:
    articles, _ = LoadArticles(filename)
    for article in articles:
      words = article.split()
      word_to_count.update(make_counter(words))

  return word_to_count


def write_log_odds(counts1, counts2, prior, outfile_name = None):
    # COPIED FROM LOG_ODDS FILE
    sigmasquared = defaultdict(float)
    sigma = defaultdict(float)
    delta = defaultdict(float)

    for word in prior.keys():
        prior[word] = int(prior[word] + 0.5)

    for word in counts2.keys():
        counts1[word] = int(counts1[word] + 0.5)
        if prior[word] == 0:
            prior[word] = 1

    for word in counts1.keys():
        counts2[word] = int(counts2[word] + 0.5)
        if prior[word] == 0:
            prior[word] = 1

    n1  = sum(counts1.values())
    n2  = sum(counts2.values())
    nprior = sum(prior.values())


    for word in prior.keys():
        if prior[word] > 0:
            l1 = float(counts1[word] + prior[word]) / (( n1 + nprior ) - (counts1[word] + prior[word]))
            l2 = float(counts2[word] + prior[word]) / (( n2 + nprior ) - (counts2[word] + prior[word]))
            sigmasquared[word] =  1/(float(counts1[word]) + float(prior[word])) + 1/(float(counts2[word]) + float(prior[word]))
            sigma[word] =  math.sqrt(sigmasquared[word])
            delta[word] = ( math.log(l1) - math.log(l2) ) / sigma[word]

    if outfile_name:
      outfile = open(outfile_name, 'w')
      for word in sorted(delta, key=delta.get):
        outfile.write(word)
        outfile.write(" %.3f\n" % delta[word])

      outfile.close()
    else:
      return delta


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--keywords", default="./keywords.txt")
    parser.add_argument("--outfile_prefix", default="./Prev")
    parser.add_argument("--percent_change", default="/usr1/home/anjalief/corpora/russian/percent_change/russian_rtsi_rub.csv")
    parser.add_argument("--input_path", default="/usr1/home/anjalief/corpora/russian/yearly_mod_subs/iz_lower/init_files/")
    args = parser.parse_args()


    # Intersect with framing lexicons
    prior = LoadBackgroundCorpus(args.input_path)

    keywords = [l.strip() for l in open(args.keywords).readlines()]

    good_dates, bad_dates = get_month_prev(args.percent_change)

    good_file_names = [os.path.join(args.input_path,
                                    str(d.year) + "_" + str(d.month) + ".txt.tok")
                       for d in good_dates]
    bad_file_names = [os.path.join(args.input_path,
                                   str(d.year) + "_" + str(d.month) + ".txt.tok")
                      for d in bad_dates]
    for x in good_dates:
      print(x)

    print("")
    print("")
    for x in bad_dates:
      print(x)
    print("")
    print("")

    good_e, good_i, good_e_count, good_i_count, good_count = \
        LoadCountsExternal(good_file_names, keywords)

    bad_e, bad_i, bad_e_count, bad_i_count, bad_count = \
        LoadCountsExternal(bad_file_names, keywords)

    frame_to_lex = pickle.load(open("frame_to_lex_final.pickle", "rb"))
    delta = write_log_odds(good_e, bad_e, prior)

    badest_1000 = sorted(delta, key=delta.get)[:2000]
    bestest_1000 = sorted(delta, key=delta.get)[-2000:]
    for f in frame_to_lex:
        print(f)

        for w in frame_to_lex[f]:
            if w in badest_1000:
                print ("Bad", w, delta[w])
            if w in bestest_1000:
                print("Good", w, delta[w])
        print("")
    return

    # SUPER BASIC USED FOR BACKSTORY
    if True:
      # good_dates, bad_dates = get_month_just_after(args.percent_change)
      # good_file_names = [os.path.join(args.input_path,
      #                                 str(d.year) + "_" + str(d.month) + ".txt.tok")
      #                    for d in good_dates]
      # bad_file_names = [os.path.join(args.input_path,
      #                                str(d.year) + "_" + str(d.month) + ".txt.tok")
      #                   for d in bad_dates]
      good_file_names = ["/usr1/home/anjalief/corpora/russian/yearly_mod_subs/iz_lower/2013.txt.tok"]
      bad_file_names = ["/usr1/home/anjalief/corpora/russian/yearly_mod_subs/iz_lower/2014.txt.tok"]

      prior = LoadBackgroundCorpus(args.input_path)
      good_counts = LoadSingleCorpus(good_file_names)
      bad_counts = LoadSingleCorpus(bad_file_names)
      write_log_odds(good_counts, bad_counts, prior, "super_basic.txt")
      return

#    good_dates, bad_dates = get_hardcoded_dates()
    good_dates, bad_dates = get_good_month_prev(args.percent_change)

    good_file_names = [os.path.join(args.input_path,
                                    str(d.year) + "_" + str(d.month) + ".txt.tok")
                       for d in good_dates]
    bad_file_names = [os.path.join(args.input_path,
                                   str(d.year) + "_" + str(d.month) + ".txt.tok")
                      for d in bad_dates]
    keywords = [l.strip() for l in open(args.keywords).readlines()]

    cache_file_name = "log_odds_all_cache.pickle"
    if os.path.isfile(cache_file_name):
      prior, \
          good_e, good_i, good_e_count, good_i_count, good_count, \
          bad_e, bad_i, bad_e_count, bad_i_count, bad_count \
          = pickle.load(open(cache_file_name, "rb"))
    else:
      prior = LoadBackgroundCorpus(args.input_path)

      good_e, good_i, good_e_count, good_i_count, good_count = \
          LoadCountsExternal(good_file_names, keywords)

      bad_e, bad_i, bad_e_count, bad_i_count, bad_count = \
          LoadCountsExternal(bad_file_names, keywords)

      pickle.dump((prior,
                   good_e, good_i, good_e_count, good_i_count, good_count,
                   bad_e, bad_i, bad_e_count, bad_i_count, bad_count),
                  open(cache_file_name, "wb"))

    # I think corpus has about 200,000 words, so this should capture
    # common bigrams
    if LIMIT:
      prior_lim = [x[0] for x in prior.most_common(300000)]
      prior = { k: prior[k] for k in prior_lim }

      good_e = { k: good_e[k] for k in prior_lim }
      good_i = { k: good_i[k] for k in prior_lim }
      bad_e = { k: bad_e[k] for k in prior_lim }
      bad_i = { k: bad_i[k] for k in prior_lim }

    print ("GOOD COUNTS", good_e_count, good_i_count, good_count)
    print ("BAD COUNTS", bad_e_count, bad_i_count, bad_count)

    # write_log_odds(bad_i, bad_e, prior, args.outfile_prefix + "_bad_i_bad_e.txt")
    # write_log_odds(good_i, good_e, prior, args.outfile_prefix + "_good_i_good_e.txt")
    # write_log_odds(bad_e, good_e, prior, args.outfile_prefix + "_bad_e_good_e.txt")
    # write_log_odds(bad_i, good_i, prior, args.outfile_prefix + "_bad_i_good_i.txt")


    # Score against frames
    # write_log_odds(bad_i, bad_e, prior)
    # write_log_odds(good_i, good_e, prior)
    # write_log_odds(bad_i, good_i, prior )

    frame_to_lex = pickle.load(open("frame_to_lex_final.pickle", "rb"))
    for f in frame_to_lex:
      print (f)
      print (frame_to_lex[f])
    return
    delta = write_log_odds(bad_e, good_e, prior)
    print("BAD_E_GOOD_E")
    for c in frame_to_lex:
      summary = 0
      word_count = 0
      for word in frame_to_lex[c]:
        if word in delta:
          word_count += 1
          summary += delta[word]
        else:
          print ("Skipping ", word)
      print (c, summary, word_count)


    delta = write_log_odds(bad_i, good_i, prior)
    print("BAD_I_GOOD_I")
    for c in frame_to_lex:
      summary = 0
      word_count = 0
      for word in frame_to_lex[c]:
        if word in delta:
          summary += delta[word]
          word_count += 1
        else:
          print ("Skipping ", word)
      print (c, summary, word_count)

    delta = write_log_odds(bad_i, bad_e, prior)
    print("BAD_I_BAD_E")
    for c in frame_to_lex:
      summary = 0
      word_count = 0
      for word in frame_to_lex[c]:
        if word in delta:
          summary += delta[word]
          word_count += 1
        else:
          print ("Skipping ", word)
      print (c, summary, word_count)


    delta = write_log_odds(good_i, good_e, prior)
    print("GOOD_I_GOOD_E")
    for c in frame_to_lex:
      summary = 0
      word_count = 0
      for word in frame_to_lex[c]:
        if word in delta:
          summary += delta[word]
          word_count += 1
        else:
          print ("Skipping ", word)
      print (c, summary, word_count)





if __name__ == "__main__":
    main()
