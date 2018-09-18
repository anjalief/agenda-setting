# All positive class baseline

from eval_frames import get_data_split
import argparse
from data_iters import *
from collections import defaultdict
from sklearn.linear_model import LogisticRegression
from gensim.corpora import Dictionary
import gensim
from sklearn.metrics import confusion_matrix, f1_score, accuracy_score


def generate_features(tokenized_data):
    dictionary = Dictionary(tokenized_data)

    # remove all words that occur less than 5 times
    dictionary.filter_extremes(no_below=5, no_above=0.95)

    # bag-of-words representation
    bows = [dictionary.doc2bow(x) for x in tokenized_data]
    return bows, dictionary

def logistic_regress(code_to_str):
    short_codes = set([code_to_short_form(code) for code in code_to_str])
    short_codes.remove(0.0) # Skip "None"
    short_codes.remove(15.0) # Skip "Other"
    short_codes.remove(16.0) # Skip "Irrelevant
    short_codes.remove(17.0) # Skip tones
    short_codes.remove(18.0)
    short_codes.remove(19.0)

    train_files = ["/usr1/home/anjalief/corpora/media_frames_corpus/immigration.json"]

    code_to_scores = defaultdict(list)
    for i in range(0, 10):
        # skip things that are missing primary frame (This is done with filter_tone = True
        test_data, train_data = get_random_split(train_files, fold=i, num_folds=10, filter_tone = True)

        train_iter = FrameAnnotationsIter(train_data)
        code_to_train_labels = defaultdict(list)
        train_data = []

        for text,frames,_ in train_iter:
            train_data.append(text)
            for c in short_codes:
                code_to_train_labels[c].append(c in frames)

        test_iter = FrameAnnotationsIter(test_data)
        code_to_test_labels = defaultdict(list)
        test_data = []

        for text,frames,_ in test_iter:
            test_data.append(text)
            for c in short_codes:
                code_to_test_labels[c].append(c in frames)

        train_data, dictionary = generate_features(train_data)
        test_data = [dictionary.doc2bow(f) for f in test_data]


        # We have to do this so train and test match
        all_data = train_data + test_data
        all_data = gensim.matutils.corpus2csc(all_data).transpose()

        train_data = all_data[:len(train_data)]
        test_data = all_data[-len(test_data):]

        for c in short_codes:
            train_labels = code_to_train_labels[c]
            test_labels = code_to_test_labels[c]

            model = LogisticRegression()
            model.fit(train_data, train_labels)

            preds = model.predict(test_data)
            score = f1_score(test_labels, preds)

            code_to_scores[c].append(score)


    # Average over folds
    for c in code_to_scores:
        print (code_to_str[c], sum(code_to_scores[c]) / 10)

def count_frames(frame_iter):
    frame_counter = Counter()
    text_count = 0
    for text,frames,_ in frame_iter:
        for frame in frames:
            frame_counter[frame] += 1
        text_count += 1

    return frame_counter, text_count

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--code_file", default="/usr1/home/anjalief/corpora/media_frames_corpus/codes.json")
    # specify what to use as training data and what to use as test set. If random, hold out 20% of data of test
    # if kfold, we do a different data split for each frame, so that test and train data have same proportion
    # of the frame at the document level
    parser.add_argument("--split_type", choices=['tobacco', 'immigration', 'samesex', 'random', 'kfold', 'dcard'])
    args = parser.parse_args()


    code_to_str = load_codes(args.code_file)
    logistic_regress(code_to_str)
    return
    _, test_data, _ = get_data_split(args.split_type)
    # make data iters
    doc_level_iter = FrameAnnotationsIter(test_data)

    frame_counter, num_articles = count_frames(doc_level_iter)

    half = num_articles / 2

    for frame in frame_counter:
        # For now assume every doc has every frame
        # if frame_counter[frame] < half:
        #     precision = 0
        #     recall = frame_counter[frame] / num_articles
        precision = frame_counter[frame] / num_articles
        recall = 1
        f1_score = 2 * (precision * recall) / (precision + recall)
        accuracy = frame_counter[frame] / num_articles

        print(code_to_str[frame], f1_score, accuracy)


if __name__ == "__main__":
    main()
