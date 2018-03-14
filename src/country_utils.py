#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import spacy
# nlp = spacy.load('en')

def get_countries(filename, stemmer = None):
    country_glob = open(filename).read()
    countries = set()
    # in country file, each line contains [country],[capital],[language1],[language2]
    for c in country_glob.split("\n"):
        for i in c.split(","):
            item = i.strip()
            if stemmer:
                item = stemmer.stem(item)
            countries.add(item)
    return countries

def contains_country(words, countries, stemmer = None):
    count_this_article = 0
    l = []

    # figure out if this article mentions another country
    for w in words:
        if stemmer:
            w = stemmer.stem(w)
        if w in countries:
            count_this_article += 1
            l.append(w)

    return count_this_article, l

# def english_ner_contains_country(text):
#     doc = nlp(text)
#     for entity in doc.ents:
#         print (entity.text, entity.label_)


