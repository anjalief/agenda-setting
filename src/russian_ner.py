#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
from article_utils import LoadArticles
import time
from requests.exceptions import HTTPError

# SPACY
import spacy
nlp = spacy.load('xx')

# TEXTERRA
from ispras import texterra
tt = texterra.API('157be6a2aa25848a75284e3f43ab5c38af2f6974', 'texterra', 'v1')
RUSSIA_NAMES = ["Россия", "русс", "СССР", 'страны', 'советской', 'Союзу', 'РФ']
RUSSIA_NAMES = [x.lower()[0:min(4, len(x))] for x in RUSSIA_NAMES]
print (RUSSIA_NAMES)

def write_spacy(a, fp):
    doc = nlp(a)
    already_found = set()
    for ent in doc.ents:
        if ent.label_ == "LOC" and not ent.text in already_found:
            fp.write(" ".join([ent.text, ent.label_]))
            already_found.add(ent.text)
            fp.write("\n")
    fp.write("***********************************************************************\n")


def texterra_count_countries(a):
    try:
        doc = tt.namedEntitiesAnnotate(a)
    except HTTPError as e:
        print (e.response.status_code)
        print (e.response)
        print (e.response.headers)
        exit
        time.sleep(65)
        doc = tt.namedEntitiesAnnotate(a)
    found = set()
    count = 0
    for d in doc['annotations']['named-entity']:
        # see list of tags below to add more
        if d['value']['tag'] ==  "GPE_COUNTRY":
            cut = d['text'][0:min(4, len(d['text']))].lower()
            # we don't want to include Russia in external country names
            if not cut in RUSSIA_NAMES:
                count += 1
                found.add(d['text'])
        elif d['value']['tag'] == "LOCATION_CONTINENT":
            count += 1
            found.add(d['text'])
    return count, found


def write_texterra(a, fp):
    doc = tt.namedEntitiesAnnotate(a)
    already_found = set()
    for d in doc['annotations']['named-entity']:
        # see list of tags below to add more
        if d['value']['tag'] in ["GPE_COUNTRY", "LOCATION_CONTINENT"] and not d['text'] in already_found:
            fp.write(d['text'] + " " + d['value']['tag'] + "\n")
            already_found.add(d['text'])
    fp.write("***********************************************************************\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--article_glob')
    parser.add_argument('--outfile', default='ner_out.txt')
    args = parser.parse_args()

    fp = open(args.outfile, "w")
    articles,_ = LoadArticles(args.article_glob)
    # TODO: spaCy has parallelization library
    for a in articles:
        lines = a.split("\n")
        # Write countries my list found and remove from article
        raw_countries = ""
        for i in range(len(lines) - 1, -1, -1):
            if "COUNTRIES" in lines[i]:
                raw_countries = lines[i]
                del lines[i]
                break
        fp.write(raw_countries + "\n")

        a = "\n".join(lines)
        write_spacy(a, fp)
#        write_texterra(a, fp)

if __name__ == '__main__':
    main()

# possible texterra tags
# https://api.ispras.ru/texterra/v1/docs#named_entity_tagging_russian
# PERSON
# NORP_NATIONALITY
# NORP_RELIGION
# NORP_POLITICAL
# NORP_OTHER
# FACILITY
# ORGANIZATION_CORPORATION
# ORGANIZATION_EDUCATIONAL
# ORGANIZATION_POLITICAL
# ORGANIZATION_OTHER
# GPE_COUNTRY
# GPE_CITY
# GPE_STATE_PROVINCE
# GPE_OTHER
# LOCATION_RIVER
# LOCATION_LAKE_SEA_OCEAN
# LOCATION_REGION
# LOCATION_CONTINENT
# LOCATION_OTHER
# PRODUCT
# DATE
# TIME
# MONEY
# EVENT
# PLANT
# ANIMAL
# SUBSTANCE
# DISEASE
# WORK_OF_ART
# LANGUAGE
# GAME
