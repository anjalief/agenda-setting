from data_iters import get_per_frame_split, code_to_short_form, FrameAnnotationsIter, load_codes, get_random_split
from parse_frames import words_to_pmi, do_counts, seeds_to_real_lex, get_words_to_cut
from eval_frames import get_wv_nyt_name, get_top_words, test_annotations, test_primary_frame, do_all
from collections import Counter, defaultdict
from tune_frames import do_per_frame
import multiprocessing
import argparse

from params import Params

TUNE_SPLIT = 0
SPLIT_TYPE = "kfold"
TEST_BACKGROUND = "/usr1/home/anjalief/media_frames_corpus/parsed/*/json/*.json"
NUM_FRAMES=14
codes=None
NUM_FOLDS=10

# TRAIN_FILES = ["/usr1/home/anjalief/corpora/media_frames_corpus/tobacco.json",
#                "/usr1/home/anjalief/corpora/media_frames_corpus/immigration.json",
#                "/usr1/home/anjalief/corpora/media_frames_corpus/samesex.json"]
TRAIN_FILES = ["/usr1/home/anjalief/corpora/media_frames_corpus/immigration.json"]
# TRAIN_FILES = ["/usr1/home/anjalief/corpora/media_frames_corpus/tobacco.json"]

params = Params()

def do_frame(frame_code):
    average_score = 0

    for fold in range(1, 5): # fold 1 is tune
        test_data, train_data = get_per_frame_split(TRAIN_FILES, frame_code, fold)
        f1_score = do_per_frame(train_data, test_data, TEST_BACKGROUND, frame_code,
                                params.VOCAB_SIZE, params.MIN_CUT, params.MAX_CUT, params.TO_RETURN_COUNT, params.VEC_SEARCH, params.SIM_THRESH, params.LEX_COUNT)
        average_score += f1_score
#    return average_score / NUM_FRAMES
    return average_score / 4 # divide by number of folds

def do_random_parallel(fold):
    global args
    global code_to_str

    if args.split_type == 'dcard':
        test_data, train_data = get_random_split(TRAIN_FILES, fold, NUM_FOLDS, filter_tone=True)
    else:
        test_data, train_data = get_random_split(TRAIN_FILES, fold, NUM_FOLDS)

    code_to_lex, doc_level_iter = do_all(args, train_data, test_data, TEST_BACKGROUND, code_to_str, params, do_print = False)
    code_to_f1 = test_annotations(code_to_lex, code_to_str, doc_level_iter, lex_count=params.LEX_COUNT, do_print = False)
    primary_acc = test_primary_frame(code_to_lex, code_to_str, doc_level_iter, do_print = False)

    return primary_acc, code_to_f1

def do_random(t_code_to_str, t_args):
    global args
    args = t_args
    global code_to_str
    code_to_str = t_code_to_str

    folds = range(0, NUM_FOLDS)
    pool = multiprocessing.Pool(processes=10)
    out_data = pool.map(do_random_parallel, folds)

    primary_accs = [o[0] for o in out_data]
    code_to_f1s = defaultdict(list)

    for _,code_to_f1 in out_data:
        for code in code_to_f1:
            code_to_f1s[code].append(code_to_f1[code])

    print (primary_accs)
    print("PRIMARY", sum(primary_accs) / NUM_FOLDS)
    for c in code_to_f1s:
        scores = code_to_f1s[c]
        if not len(scores) == NUM_FOLDS:
            continue
        print(code_to_str[c] + ";", sum(scores) / (NUM_FOLDS))

# This is the non-parallel version
# def do_random(code_to_str, args):
#     primary_accs = []
#     code_to_f1s = defaultdict(list)

#     for fold in  range(0, NUM_FOLDS):
#         if args.split_type == 'dcard':
#             print("DCARD")
#             test_data, train_data = get_random_split(TRAIN_FILES, fold, NUM_FOLDS, filter_tone=True)
#         else:
#             test_data, train_data = get_random_split(TRAIN_FILES, fold, NUM_FOLDS)

#         code_to_lex, doc_level_iter = do_all(args, train_data, test_data, TEST_BACKGROUND, code_to_str, params, do_print = False)
#         code_to_f1 = test_annotations(code_to_lex, code_to_str, doc_level_iter, lex_count=params.LEX_COUNT, do_print = False)
#         primary_acc = test_primary_frame(code_to_lex, code_to_str, doc_level_iter, do_print = False)

#         primary_accs.append(primary_acc)
#         for c in code_to_f1:
#             code_to_f1s[c].append(code_to_f1[c])

#     print (primary_accs)
#     print("PRIMARY", sum(primary_accs) / NUM_FOLDS)
#     for c in code_to_f1s:
#         scores = code_to_f1s[c]
#         if not len(scores) == NUM_FOLDS:
#             continue
#         print(code_to_str[c] + ";", sum(scores) / (NUM_FOLDS))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", action='store_true')
    # can only cross-validate for these two
    parser.add_argument("--split_type", choices=['random', 'kfold', 'dcard'])
    args = parser.parse_args()

    global codes

    # Get codes we care about
    code_file="/usr1/home/anjalief/corpora/media_frames_corpus/codes.json"
    code_to_str = load_codes(code_file)
    codes = set([code_to_short_form(code) for code in code_to_str])
    codes.remove(0.0) # Skip "None"
    codes.remove(15.0) # Skip "Other"
    codes.remove(16.0) # Skip "Irrelevant
    codes.remove(17.0) # Skip tones
    codes.remove(18.0)
    codes.remove(19.0)

    if args.split_type == 'random' or args.split_type == 'dcard':
        do_random(code_to_str, args)
        return

    pool = multiprocessing.Pool(processes=3)
    out_data = pool.map(do_frame, codes)
    for code,f1 in zip(codes, out_data):
        print (code_to_str[code], f1)

if __name__ == "__main__":
    main()
