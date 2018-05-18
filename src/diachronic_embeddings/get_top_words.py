import sys
sys.path.append('..')
from article_utils import LoadArticles
from utils import get_tag
from collections import defaultdict

import operator
import pickle

import os

def get_top_words(filepath):
    noun_to_count = defaultdict(int)
    adj_to_count = defaultdict(int)
    all_to_count = defaultdict(int)

    if os.path.isfile("all_to_count.pickle"):
        all_to_count, noun_to_count, adj_to_count = pickle.load(open("all_to_count.pickle", "rb"))
        return noun_to_count, adj_to_count, all_to_count

    articles, _ = LoadArticles(filepath)
    for a in articles:
        words = a.split()
        for word in words:
            tag = get_tag(word)
            if not tag:
                all_to_count[word] += 1
                continue
            if "NOUN" in tag:
                noun_to_count[word] += 1
            elif "ADJF" in tag:
                adj_to_count[word] += 1
            all_to_count[word] += 1
    pickle.dump((all_to_count, noun_to_count, adj_to_count), open("all_to_count.pickle", "wb"))
    return noun_to_count, adj_to_count, all_to_count

def main():
    filepath = "/usr1/home/anjalief/corpora/russian/yearly_mod_subs/iz_lower/2003_1.txt.tok"

    fp = open("top_adj.txt", "w+")
    for key in sorted(adj_to_count, key=adj_to_count.get, reverse = True)[:1000]:
        fp.write(key + "\n")
    fp.close()

    fp = open("top_nouns.txt", "w+")
    for key in sorted(noun_to_count, key=noun_to_count.get, reverse = True)[:1000]:
        fp.write(key + "\n")
    fp.close()

    fp = open("top_all.txt", "w+")
    for key in sorted(all_to_count, key=all_to_count.get, reverse = True)[:1000]:
        fp.write(key + "\n")
    fp.close()


if __name__ == "__main__":
    main()
