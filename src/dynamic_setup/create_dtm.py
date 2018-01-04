#!/usr/bin/env python
# create a sparse document term matrix
# takes in an article glob and a lexicon (create_lexicon.py)
# creates two files:
#   dtm.out: each line represents 1 document as a sparse
#            count of words (wordindex:count) for every word in doc
#   filepath.out: each line has the full file name for the document
#                 in the corresponding line of dtm.out
import sys
sys.path.insert(0, ".") # need to find article utils
from article_utils import LoadArticles
import argparse
import glob
import os


def read_lexicon(filename):
    lex = {}
    index = 0
    for line in open(filename).readlines():
        lex[line.strip()] = str(index)
        index += 1
    return lex

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--article_glob')
  parser.add_argument('--lexicon')
  parser.add_argument('--outdir')
  args = parser.parse_args()

  lexicon = read_lexicon(args.lexicon)
  file_out = open(args.outdir + "filepath.out", "a")
  dtm_out = open(args.outdir + "dtm.out", "a")

  # the name of each file is YYYY_MM.txt.tok
  # we want files grouped by date
  for filename in sorted(glob.iglob(args.article_glob), key=os.path.basename):
      articles, article_index = LoadArticles(filename, False)
      for a,i in zip(articles, article_index):
          counter = {}
          words = a.split()
          for w in words:
              count = counter.get(w, 0)
              counter[w] = count + 1
          dtm_out.write(str(len(counter)) + " ")
          for k in counter:
              dtm_out.write(lexicon[k] + ":" + str(counter[k]) + " ")
          dtm_out.write("\n")
          file_out.write(i[0] + " " + str(i[1]) + "\n")

if __name__ == '__main__':
  main()

