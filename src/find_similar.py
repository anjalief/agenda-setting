# similarity metric is taken from QUOTUS paper
# length normalized Levenshtein distance
# import editdistance as ed
import pandas
import timeit
import argparse
import random
from article_utils import LoadArticles

from sklearn.feature_extraction.text import CountVectorizer
from numpy import squeeze
import scipy
vectorizer = CountVectorizer()

TEXT_IDX=3
SAMPLE_SIZE=1000


def calculate_editdistance(text1, text2):
    return calculate_cosdistance(text1, text2)
    # d = ed.eval(text1, text2)
    # d /= float(max(len(text1), len(text2)))
    # return d

def calculate_cosdistance(text1, text2):
    X = vectorizer.fit_transform([text1, text2])
    return scipy.spatial.distance.cosine(squeeze(X[0].toarray()), squeeze(X[1].toarray()))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_file")
    parser.add_argument("--article_glob")
    parser.add_argument("--threshold", type=float)
    parser.add_argument("--use_edit_distance", action='store_true')
    args = parser.parse_args()

    articles, _ = LoadArticles(args.article_glob)
    count_matches = 0

    distances = []
    start = timeit.default_timer()

    # if we didn't specify a threshold, we don't know it yet
    # pull a random sample of 1000 articles and hope there
    # are some duplicates in there that can help us tune
    sample = min(len(articles), SAMPLE_SIZE)
    if not args.threshold:
        indices = random.sample(range(0, len(articles)), sample)

        # self-note, original was range(0, len(reader))
        for i1 in range(0, sample - 1):
            for j1 in range(i1 + 1, sample):
                i = indices[i1]
                j = indices[j1]
                if args.use_edit_distance:
                    distance = calculate_editdistance(articles[i],
                                                      articles[j])
                else:
                    distance = calculate_cosdistance(articles[i],
                                                     articles[j])
                distances.append((i, j, distance))

        distances.sort(key=lambda x: x[2])
        stop = timeit.default_timer()
        print ("TIME",stop - start)

        # print out lowest 100 distances
        for d in distances[0:100]:
            print (d[2])
            print (articles[d[0]])
            print (articles[d[1]])
            print ("************************************************")

    # THIS IS NOT A DRILL
    # we go through rows in Date order, if we find a later row that
    # matches an earlier row, we remove the later one
    # if we didn't specify a threshold, we don't know it yet
    # else:
    #     skip_count = 0
    #     for i in range(0, len(reader)):
    #         # we've already marked this for skipping
    #         # if there are any articles similar to this one, we should have already
    #         # marked them (i.e. when when marked this one)
    #         if reader.iloc[i,TEXT_IDX] == "SKIP":
    #             continue
    #         for j in range(i + 1, len(reader)):
    #             if args.use_edit_distance:
    #                 distance = calculate_editdistance(reader.iloc[i,TEXT_IDX],
    #                                                   reader.iloc[j,TEXT_IDX])
    #             else:
    #                 distance = calculate_cosdistance(reader.iloc[i,TEXT_IDX],
    #                                                  reader.iloc[j,TEXT_IDX])
    #             # they are too similar, we remove the later one
    #             if distance < args.threshold:
    #                 print (distance)
    #                 reader.iloc[j,TEXT_IDX] = "SKIP"
    #                 skip_count += 1
    #     reader[reader['Text'] != "SKIP"].to_csv(args.out_file)
    #     print ("REMOVED", skip_count)


if __name__ == "__main__":
    main()
