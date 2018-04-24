#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pickle
from russian_ner import get_texterra_tags
import argparse
import glob

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pickle_glob')
    parser.add_argument('--outpath')
    args = parser.parse_args()

    all_countries = set()
    tags = ["GPE_COUNTRY", "LOCATION_CONTINENT"]
    for filename in glob.iglob(args.pickle_glob):
        annotations = pickle.load(open(filename, "rb"))
        all_countries = all_countries.union(get_texterra_tags(annotations, tags))

    fp = open(args.outpath, "w")
    curr = ""
    for c in sorted(all_countries):
        if len(c) >= 4:
            if c[0:4] != curr:
                curr = c[0:4]
                fp.write("\n")
        fp.write(c)
        fp.write(",")
    fp.close()

if __name__ == "__main__":
    main()
