import sys
sys.path.append("..")
from econ_utils import load_percent_change, get_corr, do_granger_test
from article_utils import *
from basic_log_odds import LoadBackgroundCorpus, LoadCountsExternal, write_log_odds

import argparse
from collections import defaultdict
import pickle

def print_stats(econ_seq, frame_seq):
    assert(len(econ_seq) == len(frame_seq))
    print(get_corr(econ_seq, frame_seq))

    res = do_granger_test(frame_seq, econ_seq)
    for lag in res:
        print (lag)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--percent_change", default="/usr1/home/anjalief/corpora/russian/percent_change/russian_rtsi_rub.csv")
    parser.add_argument("--input_path", default="/usr1/home/anjalief/corpora/russian/yearly_mod_subs/iz_lower/")
    parser.add_argument("--keywords", default="./keywords.txt")
    args = parser.parse_args()


    # DANGER DANGER DANGER
    keywords = [l.strip() for l in open(args.keywords).readlines()]

    econ_dict = load_percent_change(args.percent_change)
    econ_seq = [econ_dict[d] for d in sorted(econ_dict)]

    prior = LoadBackgroundCorpus(args.input_path)
    frame_to_lex = pickle.load(open("frame_to_lex.pickle", "rb"))

    date_seq, filenames = get_files_by_time_slice(args.input_path, "monthly")
    prev_e = None
    prev_i = None

    frame_to_seq_e = defaultdict(list)
    frame_to_seq_i = defaultdict(list)

    for d,filename in zip(date_seq, filenames):
        curr_e, curr_i, _, _,_ = LoadCountsExternal(filename, keywords)

        if not prev_e:
            prev_e = curr_e
            prev_i = curr_i
            continue

        delta_e = write_log_odds(prev_e, curr_e, prior)
        delta_i = write_log_odds(prev_i, curr_i, prior)

        for c in frame_to_lex:
            summary_e = 0
            summary_i = 0
            for word in frame_to_lex[c]:
                if word in delta_e:
                    summary_e += delta_e[word]
                else:
                    print ("E Skipping ", word)
                if word in delta_i:
                    summary_i += delta_i[word]
                else:
                    print ("I Skipping ", word)
            frame_to_seq_e[c].append(summary_e)
            frame_to_seq_i[c].append(summary_i)

        prev_e = curr_e
        prev_i = curr_i

    # Done processing files
    print("-------------------------------------------------------------------------------")
    print("EXTERNAL")
    print("-------------------------------------------------------------------------------")
    for c in frame_to_seq_e:
        print(c)
        print_stats(econ_seq, frame_to_seq_e[c])
        print("******************************************************************************")

    print("-------------------------------------------------------------------------------")
    print("INTERNAL")
    print("-------------------------------------------------------------------------------")
    for c in frame_to_seq_i:
        print(c)
        print_stats(econ_seq, frame_to_seq_i[c])
        print("******************************************************************************")



if __name__ == "__main__":
    main()
