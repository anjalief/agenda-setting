import pandas
import pickle
from collections import defaultdict

def main():
    frame_to_lex = pickle.load(open("../frame_to_lex_final.pickle", "rb"))

    rows = pandas.read_csv("frame_lex1.csv")

    frame_to_perfect = defaultdict(int)
    frame_to_in_lex = defaultdict(int)
    frame_to_selected = defaultdict(int)
    frame_to_raw_perfect = defaultdict(int)
    for i in range(0, len(rows)):
        if pandas.isna(rows.iloc[i][0]):
            continue
        if rows.iloc[i][0] == "Annotations":
            frame = rows.iloc[i-1][0]
            lex = frame_to_lex[frame]
            for j in range(1, len(rows.iloc[i-1])):
                word = rows.iloc[i-1][j]
                label = rows.iloc[i][j]

                if word in lex:
                    frame_to_in_lex[frame] += 1
                if label == "1":
                    frame_to_selected[frame] += 1

                if word in lex and label == "1":
                    frame_to_perfect[frame] += 1
                    frame_to_raw_perfect[frame] += 1

                if word not in lex and label == "0":
                    frame_to_raw_perfect[frame] += 1

    # for f in frame_to_in_lex:
    #     assert frame_to_in_lex[f] == 51

    print ("FRAME", "RECALL", "PRECISION", "ACCURACY")
    for f in frame_to_in_lex:
        print (f.replace(" ",""),
               frame_to_perfect[f] / float(frame_to_selected[f]) * 100,
               frame_to_perfect[f] / float(frame_to_in_lex[f]) * 100,
               frame_to_raw_perfect[f] / 102. * 100)


if __name__ == "__main__":
    main()
