from data_iters import get_per_frame_split, code_to_short_form, FrameAnnotationsIter, load_codes
from parse_frames import words_to_pmi, do_counts, seeds_to_real_lex
from eval_frames import get_wv_nyt_name, get_top_words, test_annotations
from collections import Counter
import multiprocessing

TUNE_SPLIT = 0
SPLIT_TYPE = "kfold"
TEST_BACKGROUND = "/usr1/home/anjalief/media_frames_corpus/parsed/*/json/*.json"
NUM_FRAMES=14
codes=None
code_to_split=None

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

def try_params(params):
    global codes
    global code_to_split

    average_score = 0

    for frame_code in codes:

        test_data, train_data = code_to_split[frame_code]

        f1_score = do_per_frame(train_data, test_data, TEST_BACKGROUND, frame_code,
                                params[0], params[1], params[2], params[3], params[4], params[5])
        average_score += f1_score
    return average_score / NUM_FRAMES

def main():

    global codes
    global code_to_split

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

    # Get data split
    train_files = ["/usr1/home/anjalief/corpora/media_frames_corpus/tobacco.json",
                   "/usr1/home/anjalief/corpora/media_frames_corpus/immigration.json",
                   "/usr1/home/anjalief/corpora/media_frames_corpus/samesex.json"]


    VOCAB_SIZEs = [25000, 50000, 75000, 100000]
    MIN_COUNTs = [25, 50, 75, 100]
    TO_RETURN_COUNTs = [50, 100, 250, 500]
    VEC_SEARCHs = [50, 100, 250, 500]
    SIM_THRESHs = [0.2, 0.3, 0.4, 0.5]
    LEX_COUNTs = [1, 2, 3, 4, 5]

    # VOCAB_SIZEs = [50000]
    # MIN_COUNTs = [50]
    # TO_RETURN_COUNTs = [100]
    # VEC_SEARCHs = [100]
    # SIM_THRESHs = [0.4]
    # LEX_COUNTs = [3]

    code_to_split = {}
    for frame_code in codes:
        code_to_split[frame_code] = get_per_frame_split(train_files, frame_code, TUNE_SPLIT)

    num_frames = len(codes)
    params_to_score = {}

    params_to_try = []
    for VOCAB_SIZE in VOCAB_SIZEs:
        for MIN_COUNT in MIN_COUNTs:
            for TO_RETURN_COUNT in TO_RETURN_COUNTs:
                for VEC_SEARCH in VEC_SEARCHs:
                    for SIM_THRESH in SIM_THRESHs:
                        for LEX_COUNT in LEX_COUNTs:
                            params_to_try.append((VOCAB_SIZE, MIN_COUNT, TO_RETURN_COUNT, VEC_SEARCH, SIM_THRESH, LEX_COUNT))



    pool = multiprocessing.Pool(processes=16)
    out_data = pool.map(try_params, params_to_try)


    sorted_indices = sorted(range(0, len(params_to_try)), key = lambda x: out_data[x], reverse=True)
    for i in sorted_indices:
        print(params_to_try[i], out_data[i])

if __name__ == "__main__":
    main()
