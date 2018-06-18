import pickle
import random
import sys
sys.path.append("../diachronic_embeddings")
from get_top_words import get_top_words

def main():
    frame_to_lex = pickle.load(open("frame_to_lex_final.pickle", "rb"))

    # pull em from cache
    _,_,top_words = get_top_words("")

    vocab = sorted(top_words, key=top_words.get, reverse = True)[:50000]

    stopwords = [s.strip() for s in open("/usr1/home/anjalief/agenda-setting/data/stopwords/russian_stopwords.txt").readlines()]

    vocab = [v for v in vocab if not v in stopwords]

    final_set = []
    for f in frame_to_lex:
        print (f)
        print (frame_to_lex[f])
        if f == "Other":
            continue

        # randomly sample 51 words from frame
        frame_words = random.sample(frame_to_lex[f], 51)

        # randomly sample 51 words from vocab
        non_frame_words = random.sample(vocab, 51)

        final_non_frame_words = []
        for w in non_frame_words:
            if w in frame_to_lex[f]:
                while w in frame_to_lex[f] or w in final_non_frame_words:
                    print ("skip", w)
                    w = random.sample(vocab, 1)[0]
            final_non_frame_words.append(w)

        # check we didn't mess up
        print(final_non_frame_words)
        final_non_frame_words = set(final_non_frame_words)
        assert (len(final_non_frame_words) == 51), len(final_non_frame_words)
        for w in final_non_frame_words:
            assert not w in frame_to_lex[f]

        # merge lists, scramble, generate sets of 6
            frame_words.append(w)
        random.shuffle(frame_words)
        for i in range(0, len(frame_words), 6):
            final_set.append([f] + frame_words[i:i+6])

    random.shuffle(final_set)
    assert(len(final_set) == 14 * 102 / 6), len(final_set)
    for f in final_set:
        print("|".join(f))
        print("Annotations|" + "|".join(["1" if w in frame_to_lex[f[0]] else "0" for w in f[1:]]))
        print("")

    print ("*********************************************************")
    for f in final_set:
        print("|".join(f))
        print("Annotations")
        print("")




        # make sure vocab words are not in frame

if __name__ == "__main__":
    main()
