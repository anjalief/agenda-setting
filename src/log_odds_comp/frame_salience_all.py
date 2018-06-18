import sys
sys.path.append("..")

from article_utils import *
from get_dates import *
from collections import defaultdict
import argparse
import pickle

from frame_salience import CountFrameFrequency
from basic_log_odds import USAvsNone

def CountFrameFrequencyInternalExternal(frame_to_lex, filenames, external, keywords):
    word_to_frame = defaultdict(list)
    for f in frame_to_lex:
        for w in frame_to_lex[f]:
            word_to_frame[w].append(f)

    frame_to_word_count = defaultdict(int)
    frame_to_article_count = defaultdict(int)

    total_article_count = 0
    total_word_count = 0

    for filename in filenames:
        articles,_ = LoadArticles(filename, verbose=False)
        for article in articles:
            total_article_count += 1

            words = article.split()
            word_counter, is_external, is_internal = USAvsNone(words, keywords)
            if external:
                if not is_external:
                    continue
            else:
                if not is_internal:
                    continue

            frames_in_article = defaultdict(int)
            total_word_count += len(words)

            for w in words:
                frame = word_to_frame.get(w, None)
                if frame is not None:
                    for f in frame:
                        frame_to_word_count[f] += 1
                        frames_in_article[f] += 1
            for frame in frames_in_article:
                if frames_in_article[frame] >= 2:
                    frame_to_article_count[frame] += 1

    return frame_to_word_count, total_word_count, frame_to_article_count, total_article_count

def do_stuff(date_seq, filenames, frame_to_lex, keywords):
    print(" ", end=";")
    for f in frame_to_lex:
        print (f, end=";")
    print("")

    for date,filename in zip(date_seq,filenames):
        frame_to_word_count, total_word_count, frame_to_article_count, total_article_count = \
            CountFrameFrequencyInternalExternal(frame_to_lex, filename, False, keywords)
        print(date, end=";")
        for f in frame_to_lex:
            print (frame_to_word_count[f] / total_word_count, end=";")
        print("")

    print("")
    print("")
    print(" ", end=";")
    for f in frame_to_lex:
        print (f, end=";")
    print("")
    for date,filename in zip(date_seq,filenames):
        frame_to_word_count, total_word_count, frame_to_article_count, total_article_count = \
            CountFrameFrequencyInternalExternal(frame_to_lex, filename, False, keywords)
        print(date, end=";")
        for f in frame_to_lex:
            print (frame_to_article_count[f] / total_article_count, end=";")
        print("")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--percent_change", default="/usr1/home/anjalief/corpora/russian/percent_change/russian_rtsi_rub.csv")
    parser.add_argument("--input_path", default="/usr1/home/anjalief/corpora/russian/yearly_mod_subs/iz_lower/init_files/")
    parser.add_argument("--keywords", default="./keywords.txt")
    args = parser.parse_args()

    date_seq, filenames = get_files_by_time_slice(args.input_path, "monthly")
    frame_to_lex = pickle.load(open("frame_to_lex.pickle", "rb"))
    keywords = [l.strip() for l in open(args.keywords).readlines()]

    do_stuff(date_seq, filenames, frame_to_lex, keywords)

if __name__ == "__main__":
    main()
