import pandas
import pickle
from collections import defaultdict

def calculate_cohen(samples1, samples2):
    count = 0
    category_count1 = defaultdict(int)
    category_count2 = defaultdict(int)
    # count raw accuracy
    for s1, s2 in zip(samples1, samples2):
        if (s1 == s2):
            count += 1
        category_count1[s1] += 1
        category_count2[s2] += 1
    p0 = float(count) / len(samples1)

    # count chance accuracy
    pe = 0.0
    for c in category_count1:
        pe += category_count1[c] * category_count2[c]
    pe /= len(samples1) * len(samples1)
    return (p0 - pe) / (1 - pe)

def calculate_agreement_per_frame(rows1, rows2, target_frame):
    samples1 = []
    samples2 = []
    for i in range(0, len(rows1)):

        if pandas.isna(rows1.iloc[i][0]):
            continue

        if rows1.iloc[i][0] == "Annotations":
            assert (rows2.iloc[i][0] == "Annotations")
            assert (rows1.iloc[i-1][0] == rows2.iloc[i-1][0])

            frame = rows1.iloc[i-1][0]
            if frame != target_frame:
                continue

            assert(rows2.iloc[i-1][0] == frame)

            for j in range(1, len(rows1.iloc[i-1])):
                assert (rows1.iloc[i-1][j] == rows2.iloc[i-1][j])

                word = rows1.iloc[i-1][j]
                samples1.append(rows1.iloc[i][j])
                samples2.append(rows1.iloc[i][j])
                # if frame == "Crime and Punishment" and rows1.iloc[i][j] != rows2.iloc[i][j]:
                #     print(frame, word)

    assert(len(samples1) == len(samples2))
    agreement = calculate_cohen(samples1, samples2)
    print(target_frame, agreement, len(samples1))

def main():
    frame_to_lex = pickle.load(open("../frame_to_lex_final.pickle", "rb"))
    del frame_to_lex["Other"]
    rows1 = pandas.read_csv("frame_lex1.csv")
    rows2 = pandas.read_csv("frame_lex2.csv")

    assert(len(rows1) == len(rows2))

    for f in frame_to_lex:
        calculate_agreement_per_frame(rows1, rows2, f)

if __name__ == "__main__":
    main()
