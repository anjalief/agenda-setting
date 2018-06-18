import sys
sys.path.append("..")

from article_utils import *
from get_dates import *
from collections import defaultdict
import argparse
import pickle

def CountFrameFrequency(frame_to_lex, filenames):
    word_to_frame = defaultdict(list)
    for f in frame_to_lex:
        for w in frame_to_lex[f]:
            word_to_frame[w].append(f)

    mult = 0
    for w in word_to_frame:
        if len(word_to_frame[w]) > 1:
            mult += 1

    frame_to_word_count = defaultdict(int)
    frame_to_article_count = defaultdict(int)

    total_article_count = 0
    total_word_count = 0

    for filename in filenames:
        articles,_ = LoadArticles(filename, verbose=False)
        for article in articles:
            frames_in_article = defaultdict(int)
            total_article_count += 1
            words = article.split()
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

def print_good_v_bad(frame_to_lex, args):
    good_dates, bad_dates = get_month_just_after(args.percent_change)

    good_file_names = [os.path.join(args.input_path,
                                    str(d.year) + "_" + str(d.month) + ".txt.tok")
                       for d in good_dates]
    bad_file_names = [os.path.join(args.input_path,
                                   str(d.year) + "_" + str(d.month) + ".txt.tok")
                      for d in bad_dates]
    for b in bad_file_names:
        if b in good_file_names:
            print (b)

    frame_to_word_count, total_word_count, frame_to_article_count, total_article_count = \
        CountFrameFrequency(frame_to_lex, good_file_names)

    print("***********************************GOOD**************************************")
    for f in sorted(frame_to_word_count):
        print (f, ";", frame_to_word_count[f] / float(total_word_count))

    print("*******************************************************************************")

    for f in sorted(frame_to_word_count):
        print (f, ";", frame_to_article_count[f] / float(total_article_count))


    frame_to_word_count, total_word_count, frame_to_article_count, total_article_count = \
        CountFrameFrequency(frame_to_lex, bad_file_names)

    print("***********************************BAD**************************************")
    for f in sorted(frame_to_word_count):
        print (f, ";", frame_to_word_count[f] / float(total_word_count))

    print("*******************************************************************************")

    for f in sorted(frame_to_word_count):
        print (f, ";", frame_to_article_count[f] / float(total_article_count))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--keywords", default="./keywords.txt")
    parser.add_argument("--percent_change", default="/usr1/home/anjalief/corpora/russian/percent_change/russian_rtsi_rub.csv")
    parser.add_argument("--input_path", default="/usr1/home/anjalief/corpora/russian/yearly_mod_subs/iz_lower/init_files/")
    args = parser.parse_args()


    frame_to_lex = pickle.load(open("frame_to_lex.pickle", "rb"))
    print_good_v_bad(frame_to_lex, args)

if __name__ == "__main__":
    main()
