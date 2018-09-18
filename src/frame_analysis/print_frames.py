import pickle
import argparse
from collections import Counter
from params import Params

params = Params()

def load_sample_articles(filename):
    lines = open(filename).readlines()

    articles = []

    current_article = ""
    for line in lines:
        line = line.strip()
        if "ARTICLE" in line and current_article != "":
            articles.append(current_article)
            current_article = ""
        else:
            current_article += line
    articles.append(current_article)

    return articles

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", default="./sample_articles.txt")
    parser.add_argument("--framing_lex", default="./cache/russian_params.pickle")
    args = parser.parse_args()

    frame_to_lex = pickle.load(open(args.framing_lex, "rb"))
    frame_to_lex['Policy Prescription and Evaluation'].remove('и')

    # for f in frame_to_lex:
    #     print (f, len(frame_to_lex[f]))


    articles = load_sample_articles(args.input_path)
    print (len(articles))
    for i,a in enumerate(articles):
        words = Counter(a.split())
        print(i+1)
        for f in frame_to_lex:
            count = sum([words[w] for w in frame_to_lex[f]])
            frame_words = [w for w in frame_to_lex[f] if words[w] > 0]
            if count >= params.LEX_COUNT:
                print (f, frame_words)
        print("******************************************************************************")
        print()


if __name__ == "__main__":
    main()
