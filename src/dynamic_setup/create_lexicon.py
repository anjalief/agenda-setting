#!/usr/bin/env python
# Create a list of all types in a corpora. Print to file, with
# one word per line
# python create_lexicon.py --article_glob "/projects/tir1/users/anjalief/nyt_filtered/*/*.tok"

from article_utils import LoadArticles
import argparse
import glob

lexicon = set()

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--article_glob')
  args = parser.parse_args()

  articles, article_index = LoadArticles(args.article_glob, False)
  for a in articles:
      words = a.split()
      for w in words:
          lexicon.add(w)

  out_f = open("lexicon.txt", "a")
  for s in lexicon:
      out_f.write(s + "\n")

  out_f.close()

if __name__ == '__main__':
  main()
