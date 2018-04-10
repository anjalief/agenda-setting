#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from russian_ner import annotate_texterra_articles
from article_utils import LoadArticles
import glob
import argparse
import os
import pickle

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--article_glob')
    parser.add_argument('--outpath')
    args = parser.parse_args()

    country_tags = set()
    continent_tags = set()
    for filename in sorted(glob.iglob(args.article_glob)):
        # instead of loading each article as a separate block, we're
        # going to load all of them together, so that we don't have to
        # call the API as many times
        articles, _ = LoadArticles(filename)
#        articles = open(filename).read()  # can't do this, it's too big
        tags = annotate_texterra_articles(articles)

        # clear out the crazy amount of extra text that this API returns
        for tag in tags:
            if not "annotations" in tag:
                continue
            if not "named-entity" in tag["annotations"]:
                continue
            for y in tag["annotations"]["named-entity"]:
                del y["annotated-text"]
        # cache these guys so if we want them again don't have to
        # call the api again
        newname = os.path.join(args.outpath, os.path.basename(filename) + ".pickle")
        print (newname)
        fp = open(newname, "wb")
        pickle.dump(tags, fp)
        fp.close()

        # maybe want to get more tags eventually
        # for d in tags['annotations']['named-entity']:
        #     if d['value']['tag'] ==  "GPE_COUNTRY":
        #         country_tags.add(d['text'])

        #     elif d['value']['tag'] == "LOCATION_CONTINENT":
        #         continent_tags.add(d['text'])

    print (country_tags)
    print ()
    print (continent_tags)


if __name__ == "__main__":
    main()
