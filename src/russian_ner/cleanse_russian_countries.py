#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from russian_ner import TexterraAnnotator
# from russian_ner import annotate_texterra_articles
from article_utils import LoadArticles
import glob
import argparse
import os
import pickle

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--article_glob')
    parser.add_argument('--outpath')
    # indicate what api key you want to start on (no point
    # in trying keys that we know we've burned)
    parser.add_argument('--api_start_idx', type=int, default=0)
    args = parser.parse_args()

    country_tags = set()
    continent_tags = set()
    annotator = TexterraAnnotator(args.api_start_idx)
    for filename in sorted(glob.iglob(args.article_glob)):

        # if we've already done this file, move on
        outfile_name = os.path.join(args.outpath, os.path.basename(filename) + ".pickle")
        if os.path.isfile(outfile_name):
            print ("Already done", outfile_name)
            continue

        articles, _ = LoadArticles(filename)
        tags = annotator.annotate(articles)
#        tags = annotate_texterra_articles(articles)

        # clear out the crazy amount of extra text that this API returns
        for tag in tags:
            if not "annotations" in tag:
                continue
            if not "named-entity" in tag["annotations"]:
                continue
            for y in tag["annotations"]["named-entity"]:
                del y["annotated-text"]

        # cache these guys
        fp = open(outfile_name, "wb")
        pickle.dump(tags, fp)
        fp.close()

        # maybe want to get more tags eventually
        # for d in tags['annotations']['named-entity']:
        #     if d['value']['tag'] ==  "GPE_COUNTRY":
        #         country_tags.add(d['text'])

        #     elif d['value']['tag'] == "LOCATION_CONTINENT":
        #         continent_tags.add(d['text'])

    print ("Done")


if __name__ == "__main__":
    main()
