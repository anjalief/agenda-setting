from data_iters import get_per_frame_split, code_to_short_form, FrameAnnotationsIter, load_codes
from parse_frames import words_to_pmi, do_counts, seeds_to_real_lex
from eval_frames import get_wv_nyt_name, get_top_words, test_annotations
from collections import Counter, defaultdict
import multiprocessing

TUNE_SPLIT = 0
SPLIT_TYPE = "kfold"
TEST_BACKGROUND = "/usr1/home/anjalief/media_frames_corpus/parsed/*/json/*.json"
NUM_FRAMES=14
codes=None

TRAIN_FILES = ["/usr1/home/anjalief/corpora/media_frames_corpus/tobacco.json",
               "/usr1/home/anjalief/corpora/media_frames_corpus/immigration.json",
               "/usr1/home/anjalief/corpora/media_frames_corpus/samesex.json"]


VOCAB_SIZE = 50000
MIN_COUNT = 50
TO_RETURN_COUNT = 100
VEC_SEARCH = 100
SIM_THRESH = 0.4
LEX_COUNT = 3

def do_per_frame(train_data, test_data, test_background, frame_code,
           VOCAB_SIZE, MIN_COUNT, TO_RETURN_COUNT, VEC_SEARCH, SIM_THRESH, LEX_COUNT):

    wv_name = get_wv_nyt_name(test_background, SPLIT_TYPE)

    top_words = get_top_words(test_background)
    vocab = sorted(top_words, key=top_words.get, reverse = True)[:VOCAB_SIZE]

    corpus_counter, code_to_counter = do_counts(train_data)
    code_counter = code_to_counter[frame_code]  # Only care about current frame

    # cut infrequent words
    corpus_counter = Counter({c:corpus_counter[c] for c in corpus_counter if corpus_counter[c] > MIN_COUNT})

    corpus_count = sum([corpus_counter[k] for k in corpus_counter])
    base_lex = words_to_pmi(corpus_counter, corpus_count, code_counter, TO_RETURN_COUNT)
    final_lex = seeds_to_real_lex(base_lex, wv_name, vocab, topn=VEC_SEARCH, threshold=SIM_THRESH)

    doc_level_iter = FrameAnnotationsIter(test_data)
    f1_score = test_annotations({frame_code:final_lex}, {}, doc_level_iter, lex_count=LEX_COUNT, do_print=False)

    return f1_score

def do_frame(frame_code):
    average_score = 0

    for fold in range(1, 5): # fold 1 is tune
        test_data, train_data = get_per_frame_split(TRAIN_FILES, frame_code, fold)
        f1_score = do_per_frame(train_data, test_data, TEST_BACKGROUND, frame_code,
                                VOCAB_SIZE, MIN_COUNT, TO_RETURN_COUNT, VEC_SEARCH, SIM_THRESH, LEX_COUNT)
        average_score += f1_score
#    return average_score / NUM_FRAMES
    return average_score / 4 # divide by number of folds

def main():
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

    pool = multiprocessing.Pool(processes=3)
    out_data = pool.map(do_frame, codes)
    for code,f1 in zip(codes, out_data):
        print (code_to_str[code], f1)

if __name__ == "__main__":
    main()
