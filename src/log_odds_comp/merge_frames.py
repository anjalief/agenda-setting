import sys
sys.path.append("..")

from article_utils import *
from get_dates import *
from collections import defaultdict, Counter
import argparse
import pickle

from frame_salience import CountFrameFrequency
from basic_log_odds import USAvsNone

keywords = [k.strip() for k in open("./keywords.txt").readlines()]

def CountWeightedFrames(frame_to_lex, filenames):
    frame_to_article_count = defaultdict(int)

    total_article_count = 0
    total_usa_article_count = 0

    for filename in filenames:
        articles,_ = LoadArticles(filename, verbose=False)
        for article in articles:
            total_article_count += 1

            words = Counter(article.split())
#            if words["USA"] >= 2:
            if True:
                total_usa_article_count += 1
                for f in frame_to_lex:
                    if sum([words[x] for x in frame_to_lex[f]]) >= 2:
                        frame_to_article_count[f] += 1
            if True:
                continue

#            if sum([words[k] for k in keywords]) <= 2:

                frame_to_count = {}
                for f in frame_to_lex:
                    frame_to_count[f] = sum([words[x] for x in frame_to_lex[f]])

                # it's not in any frame, we throw it into other
                if sum([frame_to_count[x] for x in frame_to_count]) == 0:
                    frame_to_article_count["Other"] += 1
                # we only lump in frames that have at least 2 counts
                else:
                    frame_to_ratio = {}
                    sum_so_far = 0
                    for f in frame_to_count:
                        if frame_to_count[f] >= 2:
                            frame_to_ratio[f] = frame_to_count[f]
                            sum_so_far += frame_to_count[f]
                    # no one has more than 1
                    if len(frame_to_ratio) == 0:
                        frame_to_article_count["Other"] += 1
                    for f in frame_to_ratio:
                        frame_to_article_count[f] += frame_to_ratio[f]/float(sum_so_far)

        # We've seen all the articles. We should sum properly
        sum_now = 0
        for f in frame_to_article_count:
            sum_now += frame_to_article_count[f]
        # might have rounding errors
#        assert(sum_now - total_usa_article_count < 0.0001), str(sum_now) + " " + str(total_usa_article_count)

    #TODO: Normalize by lexicon length ? and project back onto num_usa_articles space ?
    # But we don't have size of other lex
    return frame_to_article_count, total_usa_article_count

def do_stuff(date_seq, filenames, frame_to_lex):
    print(" ", end=";")
    for f in frame_to_lex:
        print (f, end=";")
    print("")

    for date,filename in zip(date_seq,filenames):
        if date.year < 2000:
            continue
        frame_to_article_count, total_article_count = CountWeightedFrames(frame_to_lex, filename)

        print(date, end=";")
        for f in frame_to_lex:
            print (frame_to_article_count[f] / total_article_count, end=";")
        print("")

def get_merged_frames(frame_to_lex):
    merged_frames = {}
    merged_frames["Strife"] = set()
    merged_frames["Other"] = set()
    for f in frame_to_lex:
        if f == "Economic":
            merged_frames[f] = set(frame_to_lex[f])
        elif f in ["Security and Defense", "Crime and Punishment", "Health and Safety", "Public Sentiment"]:
            merged_frames["Strife"].update(set(frame_to_lex[f]))
        else:
            print(f)
    return merged_frames

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--percent_change", default="/usr1/home/anjalief/corpora/russian/percent_change/russian_rtsi_rub.csv")
    parser.add_argument("--input_path", default="/usr1/home/anjalief/corpora/russian/yearly_mod_subs/iz_lower/init_files/")
    parser.add_argument("--keywords", default="./keywords.txt")
    args = parser.parse_args()

    date_seq, filenames = get_files_by_time_slice(args.input_path, "yearly")
    frame_to_lex = pickle.load(open("frame_to_lex_final.pickle", "rb"))
    del frame_to_lex["Other"]
    # merged_frames = get_merged_frames(frame_to_lex)

    do_stuff(date_seq, filenames, frame_to_lex)

if __name__ == "__main__":
    main()
