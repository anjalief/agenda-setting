# Get PMIs for words in articles that mention USA twice
# Goal: is there even an interesting lexical story here?
# Goal: Identify what frames we should be trying to model. Is there even a story here?
import sys
sys.path.append("..")
sys.path.append("../diachronic_embeddings")
from utils import is_adjective
from article_utils import LoadArticles
from parse_frames import words_to_pmi
from collections import Counter
import argparse

def get_counts(article_glob):
    background_counter = Counter()
    usa_counter = Counter()
    articles, _ = LoadArticles(article_glob, verbose=False)
    for article in articles:
        article_counter = Counter(article.split())
        background_counter.update(article_counter)
        if article_counter["USA"] >= 2:
            usa_counter.update(article_counter)

    return background_counter, usa_counter

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--article_glob", default="/usr1/home/anjalief/corpora/russian/country_sub2/Isvestiia/*_*.txt.tok")
    args = parser.parse_args()

    background_counter, usa_counter = get_counts(args.article_glob)
    print(len(background_counter), len(usa_counter))
    # let's try to cut junk
    background_counter = {x:background_counter[x] for x in background_counter if background_counter[x] >= 5 and is_adjective(x)}
    usa_counter = {x:usa_counter[x] for x in usa_counter if x in background_counter}
    corpus_count = sum([background_counter[k] for k in background_counter])
    print(len(background_counter), len(usa_counter))
    overrepresented_words = words_to_pmi(background_counter, corpus_count, usa_counter, 500)

    for w in overrepresented_words:
        # do something silly to cut back on named entities?
        print(w)


if __name__ == "__main__":
    main()
