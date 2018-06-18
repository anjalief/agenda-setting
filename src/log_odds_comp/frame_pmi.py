import sys
sys.path.append("..")

from article_utils import *
from get_dates import *
from collections import defaultdict, Counter
import argparse
import pickle
import math

from frame_salience import CountFrameFrequency
from basic_log_odds import USAvsNone
from sent_pmi import ComputeSentPMI

# for each frame for each timestep, we want
# count of articles with frame and usa
# count of usa articles
# count of frame articles

# keywords = [l.strip() for l in open("./keywords.txt").readlines()]
keywords = ["USA"]

def ComputeFramePMI(frame_to_lex, articles):
    frame_to_article_count = defaultdict(int)
    frame_to_article_and_usa_count = defaultdict(int)
    usa_count = 0
    total_article_count = 0

    for article in articles:
        total_article_count += 1
        words = Counter(article.split())
        if sum([words[k] for k in keywords]) >= 2:
            usa_count += 1
        for f in frame_to_lex:
            lex = frame_to_lex[f]
            count_frame_words = sum([words[w] for w in lex])
            if count_frame_words >= 2:
                frame_to_article_count[f] += 1
                if sum([words[k] for k in keywords]) >= 2:
                    frame_to_article_and_usa_count[f] += 1

    frame_to_pmi = {}
    total_article_count = float(total_article_count)
    for f in frame_to_lex:
        num = (frame_to_article_and_usa_count[f] / total_article_count)
        denom = (frame_to_article_count[f] / total_article_count) * (usa_count / total_article_count)
        if (denom == 0):
            frame_to_pmi[f] = 0
            continue
        frame_to_pmi[f] = math.log(num / denom, 2) / -math.log(num, 2)
    return frame_to_pmi

def do_stuff(date_seq, filenames, frame_to_lex, whole_corpus):
    print(" ", end=";")
    for f in frame_to_lex:
        print (f, end=";")
    print("")
    if whole_corpus:
        all_articles = []
        for date,filename in zip(date_seq,filenames):
            articles,_ = LoadArticles(filename[0], verbose=False)
            all_articles += articles
        frame_to_pmi = ComputeSentPMI(frame_to_lex, all_articles)
        for f in frame_to_lex:
            print (frame_to_pmi[f], end=";")
        print("")
        return


    for date,filename in zip(date_seq,filenames):
        assert (len(filename) == 1), filename
        if "2000" in filename:
            continue
        if "2001" in filename:
            continue
        if "2002" in filename:
            continue
        articles,_ = LoadArticles(filename[0], verbose=False)
        frame_to_pmi = ComputeSentPMI(frame_to_lex, articles)
        print(date, end=";")
        for f in frame_to_lex:
            print (frame_to_pmi[f], end=";")
        print("")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", default="/usr1/home/anjalief/corpora/russian/yearly_mod_subs/iz_lower/2")
    parser.add_argument("--whole_corpus", action='store_true')
    parser.add_argument("--timestep")
    args = parser.parse_args()

    date_seq, filenames = get_files_by_time_slice(args.input_path, args.timestep)
    print(filenames)
    frame_to_lex = pickle.load(open("frame_to_lex_final.pickle", "rb"))
    new_frame_to_lex = {}
    new_frame_to_lex["Political"] = frame_to_lex["Political"]
    new_frame_to_lex["Public Sentiment"] = frame_to_lex["Public Sentiment"]
    new_frame_to_lex["External Regulation and Reputation"] = frame_to_lex["External Regulation and Reputation"]
    new_frame_to_lex["Security and Defense"] = frame_to_lex["Security and Defense"]

    do_stuff(date_seq, filenames, new_frame_to_lex, args.whole_corpus)

if __name__ == "__main__":
    main()
