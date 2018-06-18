import guidedlda
import pickle
import sys
import argparse
import glob
import json
from gensim.corpora import Dictionary
import gensim
import numpy as np

from eval_frames import PrimaryFrameIter

from nltk import tokenize

# Convert gensibm BOWs to numpy sparse matrix
def to_np(data):
    return gensim.matutils.corpus2csc(data, dtype=int).transpose()

# Load data into dict and create BOW representation
def load_data(input_path):
    files = glob.iglob(input_path)
    dct = Dictionary()
    all_docs = []

    for filename in files:
        json_text = json.load(open(filename))
        doc = []
        for sent in json_text["BODY"]:
            doc += tokenize.word_tokenize(sent.lower())
        all_docs.append(doc)


    dct.add_documents(all_docs)
    dct.filter_extremes(no_below=5, keep_n=100000)
    print (dct.num_docs)
    print(len(dct.token2id))
    i = 0
    for x in dct.token2id:
        print(x, dct.token2id[x])
        if i > 20:
            break
        i += 1
    bows = [dct.doc2bow(x) for x in all_docs]
    return to_np(bows), dct

def do_lda(seed_topics, data):
    model = guidedlda.GuidedLDA(n_topics=30, n_iter=5000, random_state=7, refresh=10)
    model.fit(data, seed_topics=seed_topics, seed_confidence=0.25)
    pickle.dump(model, open("guidedlda_30.pickle", "wb"))
    return model

def print_top_words(model, idx2word, id2topic, n_top_words = 10):
    topic_word = model.topic_word_
    for i, topic_dist in enumerate(topic_word):
#        sorted_words = sorted(enumerate(topic_dist), key = lambda x: x[1])
        sorted_words = np.argsort(topic_dist)
        top_words = []
        for idx in sorted_words[-n_top_words:]:
            top_words.append(idx2word[idx])
        print('Topic {}: {}'.format(id2topic.get(i, i), ' '.join(top_words)))

# This is pretty ridiculously bad
def eval_primary_frame(model, dct, id2topic, test_file):
    text_iter = PrimaryFrameIter([test_file])

    total = 0
    correct = 0
    for text,true_frame in text_iter:
        total += 1

        topics = model.transform(to_np([dct.doc2bow(text)]))
        topics = topics[0]
        topics = topics[:14] # what if we force it to be a known frame. # It's pretty bad
        primary_frame_idx = np.argsort(topics)[-1] # take the biggest topic

        print(topics, primary_frame_idx, id2topic.get(primary_frame_idx, 0))

        frame = int(primary_frame_idx)

        if frame == int(true_frame):
            correct += 1

    print (float(correct) / float(total), total)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed_lex", default="../log_odds_comp/cache/tobacco_lex.pickle")
    parser.add_argument("--data_path", default="/usr1/home/anjalief/media_frames_corpus/parsed/smoking/json/*.json")
    parser.add_argument("--test_file", default="/usr1/home/anjalief/corpora/media_frames_corpus/tobacco.json")
    parser.add_argument("--print_from_cache", action='store_true')
    args = parser.parse_args()

    seed_lex = pickle.load(open(args.seed_lex, "rb"))
    if args.print_from_cache:
        doc_matrix, dct = pickle.load(open("doc_dict.pickle", "rb"))
    else:
        doc_matrix, dct = load_data(args.data_path)
        pickle.dump((doc_matrix, dct), open("doc_dict.pickle", "wb"))

    print(doc_matrix.shape)

    topic_seeds = {}
    # note if the same word is in two topics we arbitratily assign it to 1
    id_to_topic = {}
    for topic_id, topic in enumerate(seed_lex):
        if topic == "Other":
            continue
        id_to_topic[topic_id] = topic

        # if words are not in data set, we don't care about them
        for word in seed_lex[topic]:
            word = word.lower()
            if word in dct.token2id:
                topic_seeds[dct.token2id[word]] = topic_id
            else:
                pass
#                print("Skipping", word)

    if args.print_from_cache:
        model = pickle.load(open("guidedlda_30.pickle", "rb"))
    else:
        model = do_lda(topic_seeds, doc_matrix)

    # gensism's dct.id2token isn't working
    id2token = {}
    for token in dct.token2id:
        id2token[dct.token2id[token]] = token

    print_top_words(model, id2token, id_to_topic)

    eval_primary_frame(model, dct, id_to_topic, args.test_file)



if __name__ == "__main__":
    main()
