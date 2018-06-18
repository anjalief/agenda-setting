import sys
sys.path.append("..")
from article_utils import LoadArticles
from merge_frames import get_merged_frames

import random
from collections import Counter
import pickle

def main():
    input_path = "/usr1/home/anjalief/corpora/russian/yearly_mod_subs/iz_lower/2*"
    frame_to_lex = pickle.load(open("frame_to_lex_final.pickle", "rb"))

    merged_frames = get_merged_frames(frame_to_lex)

    articles,indices = LoadArticles(input_path, verbose=False)

    sample = random.sample(range(0, len(articles)), 1000)

    # grab the first 10 that fit our requirements
    globalization = []
    mitigation = []
    other = []

    for z in sample:
        s = articles[z]

        words = Counter(s.split())
        if not words["USA"] >= 2:
            continue

        global_count = sum([words[w] for w in merged_frames["Economic"]])
        miti_count = sum([words[w] for w in merged_frames["Strife"]])
        if global_count < 2 and miti_count < 2:
            other.append((s, indices[z]))
        elif global_count >=2 and miti_count < 2:
            globalization.append((s, indices[z]))
        elif global_count < 2 and miti_count >= 2:
            mitigation.append((s, indices[z]))

        if len(globalization) >= 10 and len(mitigation) >= 10 and len(other) >= 10:
            break

    print (len(globalization), len(mitigation), len(other))
    key = ['G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G',
           'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M',
           'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']
    all_articles = globalization[:10] + mitigation[:10] + other[:10]
    shuffle = random.sample(range(0, 30), 30)
    for i in shuffle:
        print (key[i], all_articles[i][1])
    for i in shuffle:
        print ("NEW ARTICLE")
        print (all_articles[i][0].replace(".", ".\n"))
        print ("")

if __name__ == "__main__":
    main()
