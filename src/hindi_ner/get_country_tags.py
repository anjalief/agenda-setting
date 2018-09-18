import spacy
import pandas
from collections import Counter

nlp = spacy.load('en_core_web_sm')

def main():
    sample = "hindi_downsample.csv"
    data = [line.split(",")[0] for line in open(sample).readlines()]

    ents = Counter()
    for doc in data:
        parsed = nlp(doc)
        ents.update([ent.text for ent in parsed.ents if ent.label_ == "GPE"])

    common = [c[0] for c in ents.most_common(100)]

    for x in sorted(common):
        print (x)


if __name__ == "__main__":
    main()
