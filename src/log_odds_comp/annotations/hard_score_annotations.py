import pandas
import pickle
from collections import defaultdict

def main():
    frame_to_lex = pickle.load(open("../frame_to_lex_final.pickle", "rb"))

    rows1 = pandas.read_csv("frame_lex1.csv")
    rows2 = pandas.read_csv("frame_lex2.csv")

    assert(len(rows1) == len(rows2))

    frame_to_perfect = defaultdict(int)
    frame_to_in_lex = defaultdict(int)
    frame_to_selected = defaultdict(int)
    frame_to_raw_perfect = defaultdict(int)

    for i in range(0, len(rows1)):

        if pandas.isna(rows1.iloc[i][0]):
            continue

        if rows1.iloc[i][0] == "Annotations":
            assert (rows2.iloc[i][0] == "Annotations")
            assert (rows1.iloc[i-1][0] == rows2.iloc[i-1][0])

            frame = rows1.iloc[i-1][0]
            lex = frame_to_lex[frame]

            for j in range(1, len(rows1.iloc[i-1])):
                assert (rows1.iloc[i-1][j] == rows2.iloc[i-1][j])

                word = rows1.iloc[i-1][j]
                label1 = rows1.iloc[i][j]
                label2 = rows2.iloc[i][j]

                word_annotated_in_lex = False
                if word in lex:
                    frame_to_in_lex[frame] += 1

                    # if BOTH annotator got it right, we count it
                    if label1 == "1" and label2 == "1":
                        word_annotated_in_lex = True
                else:
                    # if anyone marked it wrong, we mark it wrong
                    if label1 == "1" or label2 == "1":
                        word_annotated_in_lex = True

                if word_annotated_in_lex:
                    frame_to_selected[frame] += 1

                if word in lex and word_annotated_in_lex:
                    frame_to_perfect[frame] += 1
                    frame_to_raw_perfect[frame] += 1

                if word not in lex and not word_annotated_in_lex:
                    frame_to_raw_perfect[frame] += 1

    # for f in frame_to_in_lex:
    #     assert frame_to_in_lex[f] == 51

    print ("FRAME", "RECALL", "PRECISION", "ACCURACY")
    for f in frame_to_in_lex:
        print (
               frame_to_perfect[f] / float(frame_to_selected[f]) * 100,
               frame_to_perfect[f] / float(frame_to_in_lex[f]) * 100)


if __name__ == "__main__":
    main()
