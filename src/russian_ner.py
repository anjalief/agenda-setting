#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
from article_utils import LoadArticles
import time
from requests.exceptions import HTTPError, ReadTimeout
import pickle

# SPACY
# import spacy
# nlp = spacy.load('xx')

# TEXTERRA
from ispras import texterra
# tt = texterra.API('157be6a2aa25848a75284e3f43ab5c38af2f6974', 'texterra', 'v1')
# tt = texterra.API('54e427aefd76b64024d985c78fc84de0d4bd93b0', 'texterra', 'v1')
# tt = texterra.API('c7ed3175aa051e37020e1aa9568779fbe3a8bd08', 'texterra', 'v1')
# tt = texterra.API('3bf01c7fcdb1fc058a50d53d167aa82b4c85f811', 'texterra', 'v1')
RUSSIA_NAMES = ["Россия", "русс", "СССР", 'страны', 'советской', 'Союзу', 'РФ']
RUSSIA_NAMES = [x.lower()[0:min(4, len(x))] for x in RUSSIA_NAMES]

class TexterraAnnotator():
    def __init__(self, api_start):
        self.API_IDX = api_start
        self.APIs = ['aaa3d9f43a9233b2a483ce3c6fd3bf3c4bdf4dad', 'a1e97495b947147367a0edcb67f75e37f719169c', '36533a216d1676a42d37c2a1c4acb5e20231e75a', '54e427aefd76b64024d985c78fc84de0d4bd93b0', '157be6a2aa25848a75284e3f43ab5c38af2f6974', 'c7ed3175aa051e37020e1aa9568779fbe3a8bd08', '3bf01c7fcdb1fc058a50d53d167aa82b4c85f811', 'd3a3c3cc49ef1dd086f139b8ca74e4d2b5091328', '46ee56297d52b1cda55ac78ef56b02e8b29c879a']
#        self.APIs = ['3bf01c7fcdb1fc058a50d53d167aa82b4c85f811']
        self.tt = texterra.API(self.APIs[self.API_IDX], "texterra", "v1")

    def next_tt(self, a=None):
        # It's not working and we should try the next API

        self.API_IDX += 1
        print ("NEXT API", self.API_IDX)

        # DON'T cycle, just die if we have no more APIs
        if self.API_IDX >= len(self.APIs):
            assert False, "We're out of APIs!"

        self.tt = texterra.API(self.APIs[self.API_IDX], "texterra", "v1")

    def annotate(self, articles):
        ner_tags = []
        for a in articles:
            try:
                ner_tags.append(self.tt.namedEntitiesAnnotate(a))
            # we only retry once
            except HTTPError as e:
                self.next_tt()
                print(e)
                ner_tags.append(self.tt.namedEntitiesAnnotate(a))
            except ReadTimeout as e:
                print ("SKIPPING", len(a), a[:min(10, len(a))])
        return ner_tags

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

def annotate_texterra_articles(articles):
    ner_tags = [tt.namedEntitiesAnnotate(a) for a in articles]
    return ner_tags

def write_texterra(a, fp):
    doc = tt.namedEntitiesAnnotate(a)
    already_found = set()
    for d in doc['annotations']['named-entity']:
        # see list of tags below to add more
        if d['value']['tag'] in ["GPE_COUNTRY", "LOCATION_CONTINENT"] and not d['text'] in already_found:
            fp.write(d['text'] + " " + d['value']['tag'] + "\n")
            already_found.add(d['text'])
    fp.write("***********************************************************************\n")

def get_texterra_tags(annotations, tags):
    text = set()
    for entry in annotations:
        if not "named-entity" in entry["annotations"]:
            continue
        for tag in entry["annotations"]["named-entity"]:
            if tag['value']['tag'] in tags:
                text.add(tag["text"])
    return text

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
