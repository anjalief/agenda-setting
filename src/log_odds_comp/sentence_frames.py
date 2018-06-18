from datetime import date
import pickle
import argparse
from collections import defaultdict, Counter
import os
import sys
sys.path.append("..")
from article_utils import *
from get_dates import *

def extract_frames(filenames, frame_to_lex):
    # count number of words per frame
    frame_to_word_count = defaultdict(int)
    for filename in filenames:
        for sent in SentenceIter(filename):
            frame_to_in_article_count = defaultdict(int)
            word_counter = Counter(sent)
            for f in frame_to_lex:
                f_count = sum([word_counter[w] for w in frame_to_lex[f]])
                frame_to_word_count[f] += f_count
                if word_counter["USA"] > 1 and f_count > 1:
                    print (get_date(filename), f, "|", " ".join(sent))
    return frame_to_word_count

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--percent_change", default="/usr1/home/anjalief/corpora/russian/percent_change/russian_rtsi_rub.csv")
    parser.add_argument("--input_path", default="/usr1/home/anjalief/corpora/russian/yearly_mod_subs/iz_lower/init_files/")
    args = parser.parse_args()

    good_dates, bad_dates = get_month_prev(args.percent_change)
    good_file_names = [os.path.join(args.input_path,
                                    str(d.year) + "_" + str(d.month) + ".txt.tok")
                       for d in good_dates]
    bad_file_names = [os.path.join(args.input_path,
                                   str(d.year) + "_" + str(d.month) + ".txt.tok")
                      for d in bad_dates]
    frame_to_lex = pickle.load(open("frame_to_lex.pickle", "rb"))
#    del frame_to_lex["External Regulation and Reputation"]
#    del frame_to_lex["Other"]
    new_frame_to_lex = {}
    new_frame_to_lex["External Regulation and Reputation"] = frame_to_lex["External Regulation and Reputation"]
    frame_to_lex = new_frame_to_lex
    print("*****************************************************************")
    print (good_file_names)
    print("*****************************************************************")
    print (bad_file_names)
    print("*****************************************************************")
    d = extract_frames(good_file_names, frame_to_lex)
    for f in d:
        print (f, d[f])
    print("*****************************************************************")
    d = extract_frames(bad_file_names, frame_to_lex)
    for f in d:
        print (f, d[f])


if __name__ == "__main__":
    main()
