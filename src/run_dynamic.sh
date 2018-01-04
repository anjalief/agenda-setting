#!/bin/bash

TEXT_DIR=/projects/tir1/users/anjalief/dtm
MY_NEWS_DIR=/projects/tir1/users/anjalief/nyt_filtered

# Create lexicon
# python dynamic_setup/create_lexicon.py --article_glob "${MY_NEWS_DIR}/*/*.tok"

# python dynamic_setup/create_dtm.py --article_glob "${MY_NEWS_DIR}/*/*.tok" --lexicon "${TEXT_DIR}/lexicon.txt" --outdir "${TEXT_DIR}/"


#### NOTE THIS NEEDS SOME MANNUAL CLEAN UP
# [anjalief@tir dtm]$ cat filepath.out | cut -d" " -f1 | cut -d"/" -f8 | uniq -c > count_per_month.txt
# [anjalief@tir dtm]$ emacs count_per_month.txt
# [anjalief@tir dtm]$ wc -l count_per_month.txt
# 365 count_per_month.txt
# [anjalief@tir dtm]$
# [anjalief@tir dtm]$ cat count_per_month.txt | cut -d" " -f4 > mult.out

cd /home/anjalief/dtm/dtm
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/anjalief/gsl/lib
./main \
  --ntopics=25 \
  --mode=fit \
  --rng_seed=0 \
  --initialize_lda=true \
  --corpus_prefix=example/test \
  --outname=example/model_run \
  --top_chain_var=0.005 \
  --alpha=0.01 \
  --lda_sequence_min_iter=6 \
  --lda_sequence_max_iter=20 \
  --lda_max_em_iter=10 \
   "${TEXT_DIR}/dtm.out" \
   "${TEXT_DIR}/mult.out"