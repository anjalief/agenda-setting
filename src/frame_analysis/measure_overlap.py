# Measure the overlap between two framing lexicons
# Specifically, what percent of words in the new lexicon were
# also in the old lexicon?
# Determine if we need to redo annotations

import argparse
import pickle

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--new_lex")
    parser.add_argument("--old_lex")
    args = parser.parse_args()

    code_to_new = pickle.load(open(args.new_lex, 'rb'))
    code_to_old = pickle.load(open(args.old_lex, 'rb'))

    assert(len(code_to_new) == len(code_to_old))

    for frame in code_to_new:
        new_lex = code_to_new[frame]
        old_lex = code_to_old[frame]

        overlap = 0
        for word in new_lex:
            if word in old_lex:
                overlap += 1
        print (frame, overlap / len(new_lex))



if __name__ == "__main__":
    main()
