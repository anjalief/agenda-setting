#!/bin/bash

YULIA_BASE_DIR=/usr1/home/ytsvetko/projects/agenda_setting
MY_BASE_DIR=/usr1/home/anjalief/agenda-setting
MY_NEWS_DIR=/usr1/home/anjalief/agenda_setting/data/news/russian
_LANGUAGE_=russian

NEWS=${YULIA_BASE_DIR}/data/news/${_LANGUAGE_}


#####################################################################
## Tokenize
## My tokenizer replaces "ystvetkov# with "anjalief" in the file name
## (i.e. puts the output files in my directory)
#####################################################################

# run the tokenizer on a single Russian txt file from Yulia's directory
# and put the output in my directory
#cd ${MY_BASE_DIR}/src/tokenizer
#./tokenize_anjalie.sh "${NEWS}/Pravda/2016/2016_3.txt"
#cd -

#TOK_FILES="${MY_NEWS_DIR}/*/*/*.txt.tok"

#for f in ${TOK_FILES} ; do
#    echo $f
#done

# Tokenize everything
#cd ${MY_BASE_DIR}/src/tokenizer
#./tokenize_anjalie.sh "${NEWS}/*/*/*.txt"
#cd -
#####################################################################


#####################################################################
# DO LDA
#####################################################################
## Train LDA model
 LDA_MODEL="${MY_BASE_DIR}/models/lda_russian.pkl"
# ORIGINAL
# ${MY_BASE_DIR}/src/lda.py --article_glob "${MY_NEWS_DIR}/*/*/*.txt.tok" \
#     --force_train --output_topic_distribution --lda_model ${LDA_MODEL}

# LOAD TRAINED MODEL
 ${MY_BASE_DIR}/src/lda.py --article_glob "${MY_NEWS_DIR}/*/*/*.txt.tok" \
     --output_topic_distribution --lda_model ${LDA_MODEL}

# # Get topic distribution of an external-policy related article using trained LDA model
# ${MY_BASE_DIR}/src/lda.py \
#    --article_glob "${MY_BASE_DIR}/data/focused_crawl/${_LANGUAGE_}/*.txt.tok" \
#    --output_topic_distribution --lda_model ${LDA_MODEL}



# # Print number of articles about external policy per year per newspaper
MONTHS=(1 2 3 4 5 6 7 8 9 10 11 12)
NEWSPAPERS=(Izvestiia Pravda)

for newspaper in ${NEWSPAPERS[@]}; do
  log_file=../work/topic_stats_${newspaper}.lda
  touch ${log_file}
  for month in ${MONTHS[@]}; do
    echo "Processing ${newspaper}"
    ${MY_BASE_DIR}/src/per_month_lda.py \
      --gold_vectors "${MY_BASE_DIR}/data/focused_crawl/${_LANGUAGE_}/external_policy.txt.tok.lda" \
      --log_file "${log_file}" \
      --per_month_glob "${MY_NEWS_DIR}/${newspaper}/*/*_${month}.txt.tok.lda"
  done
done
#####################################################################


