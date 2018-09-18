#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Test primary frame using BOW logistic regression
from eval_frames import get_data_split
from nltk import tokenize
from sklearn.linear_model import LogisticRegression
from gensim.corpora import Dictionary
import gensim
from sklearn.metrics import confusion_matrix, f1_score, accuracy_score
from data_iters import get_random_split

def generate_features(train_data):
    tokenized_data = [tokenize.word_tokenize(annotated_file["text"]) for annotated_file in train_data]
    dictionary = Dictionary(tokenized_data)

    # remove all words that occur less than 5 times
    dictionary.filter_extremes(no_below=5, no_above=0.95)

    # bag-of-words representation
    bows = [dictionary.doc2bow(x) for x in tokenized_data]
    return bows, dictionary

def main():
    accs = []
    # train_files = ["/usr1/home/anjalief/corpora/media_frames_corpus/tobacco.json",
    #                "/usr1/home/anjalief/corpora/media_frames_corpus/immigration.json",
    #                "/usr1/home/anjalief/corpora/media_frames_corpus/samesex.json"]
    train_files = ["/usr1/home/anjalief/corpora/media_frames_corpus/immigration.json"]
    for i in range(0, 10):
        # skip things that are missing primary frame (This is done with filter_tone = True)

        test_data, train_data = get_random_split(train_files, fold=i, num_folds=10, filter_tone = True)

        train_labels = [int(f["primary_frame"]) for f in train_data]

        test_labels = [int(f["primary_frame"]) for f in test_data]

        train_data, dictionary = generate_features(train_data)
        test_data = [dictionary.doc2bow(tokenize.word_tokenize(annotated_file["text"])) for annotated_file in test_data]


        # We have to do this so train and test match
        all_data = train_data + test_data
        all_data = gensim.matutils.corpus2csc(all_data).transpose()

        train_data = all_data[:len(train_data)]
        test_data = all_data[-len(test_data):]

        model = LogisticRegression()
        model.fit(train_data, train_labels)

        preds = model.predict(test_data)
        accs.append(accuracy_score(test_labels, preds))

    print(accs)
    print(sum(accs) / 10)


if __name__ == "__main__":
    main()
