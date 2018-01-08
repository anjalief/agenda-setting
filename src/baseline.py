import argparse
from eval_utils import TrackCorrect, LoadGold
from article_utils import LoadVectors
import glob
import os

parser = argparse.ArgumentParser()
parser.add_argument('--article_glob')
parser.add_argument('--labeled_data')
parser.add_argument('--log_file')
# parser.add_argument('--track_by_topic', action='store_true') # only for English
args = parser.parse_args()

all_topics = [ "Arts",
               "RealEstate",
               "Travel",
               "Sports",
               "HomeandGarden",
               "Food",
               "Business",
               "Automobiles",
               "DiningandWine",
               "Movies",
               "Obituaries",
               "JobMarket",
               "World",
               "Theater",
               "DiningWine",
               "Science",
               "Style",
               "YourMoney",
               "Autos",
               "Washington",
               "US",
               "Books",
               "Health",
               "Education",
               "Technology"
               ]

def is_external(v, t):
    return v[10] > t

def count_external_vectors(vectors):
    count = 0
    for v in vectors:
        if is_external(v, 0.005):
            count += 1
    return count

def main():
    if args.article_glob:
        topic_to_count = {}
        for t in all_topics:
            topic_to_count[t] = (0,0)

        for filename in glob.iglob(args.article_glob):
            dirname = os.path.dirname(filename)
            base_dirname = os.path.basename(dirname)
            vectors = LoadVectors(filename)

            num_external = count_external_vectors(vectors)

            for t in all_topics:
                if t in base_dirname:
                    count = topic_to_count[t]
                    topic_to_count[t] = (count[0] + len(vectors),
                                         count[1] + num_external)

        out_f = open(args.log_file, "w")
        for k in topic_to_count:
            v = topic_to_count[k]
            out_f.write(k + " " + str(v[0]) + " " + str(v[1]) + "\n")
        out_f.close()

    if args.labeled_data:
        threshold_vals = [0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3]

        for t in threshold_vals:
            vectors = LoadVectors(args.labeled_data)
            track_by_topic = False
            labels = LoadGold(args.labeled_data.replace(".lda", ".labels"), track_by_topic)

            tracker = TrackCorrect()
            for v,l in zip(vectors, labels):
                i = is_external(v, t)
                tracker.update(l.is_external, i)

            precision, recall, accuracy, gold_external, count = tracker.get_stats()
            print t, precision, recall, accuracy, gold_external, count


if __name__ == '__main__':
  main()
