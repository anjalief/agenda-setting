#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from replace_country_mentions import parse_subs_file
from collections import defaultdict

extras = []

def main():
    file_name = "first_pass.txt"

    bad_to_good = parse_subs_file(file_name)
    to_sort = set()
    for line in extras:
        words = line.split(",")
        for word in words:
            terms = word.split()
            if len(terms) == 1:
                if not terms[0] in bad_to_good:
                    to_sort.add(terms[0])
            elif len(terms) == 2:
                if not terms[1] in bad_to_good:
                    to_sort.add(word)
            else:
                if not word in bad_to_good:
                    to_sort.add(word)

    for s in sorted(to_sort):
        print(s)

    good_to_bad = defaultdict(set)
    for x in bad_to_good:
        good_to_bad[bad_to_good[x]].add(x)
    for g in sorted(good_to_bad):
        print (g, ",", end="")
        print (",".join(good_to_bad[g]))

if __name__ == "__main__":
    main()
