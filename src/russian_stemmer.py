#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# The NLTK stemmer mashes too much together
# This version, we're going to keep at least 4 characters
# of each word, and we're going to keep capitalizations

# We also allow passing in multiple words (ex. "New York")

# This is intended for recognizing country names
# So it's ok if we don't match "Because" and "because" to the
# same word. We care that we match China and Chinese
# to the same word
from nltk.stem.snowball import RussianStemmer
from nltk.stem.snowball import EnglishStemmer


class country_russian_stemmer:
    def __init__(self):
        self.stemmer = RussianStemmer()

    def stem_helper(self, word):
        stem = self.stemmer.stem(word)
        min_stem_length = min(4, len(word))
        stem_length = len(stem)
        if stem_length < min_stem_length:
            return word[0:min_stem_length]
        # pretty sure stemmers only cut suffix
        return word[0:stem_length]

    def stem(self, word):
        words = word.split()
        l = []
        for word in words:
            # TO UNDO
            l.append(self.stemmer.stem(word.decode('utf-8')).encode('utf-8'))
        return " ".join(l)

class country_english_stemmer:
    def __init__(self):
        self.stemmer = EnglishStemmer()

    def stem_helper(self, word):
        stem = self.stemmer.stem(word)
        min_stem_length = min(4, len(word))
        stem_length = len(stem)
        if stem_length < min_stem_length:
            return word[0:min_stem_length]
        # pretty sure stemmers only cut suffix
        return word[0:stem_length]

    def stem(self, word):
        words = word.split()
        l = []
        for word in words:
            l.append(self.stemmer.stem(word.decode('utf-8')).encode('utf-8'))
        return " ".join(l)


# Some tests
def main():
    w1 = "Несмотря"
    w2 = "Накануне"
    w3 = "России"
    w4 = "лучше"
    w5 = "лу"

    stemmer = country_russian_stemmer()

    assert stemmer.stem(w1) == "Несмотр"
    assert stemmer.stem(w2) == "Наканун"
    assert stemmer.stem(w3) == "Росс"
    assert stemmer.stem(w4) == "лучш"
    assert stemmer.stem(w5) == "лу"

if __name__ == '__main__':
  main()
