#!/bin/bash

################################################
# For Tir, we need to run python in a virtual env
# module load singularity
# singularity shell --nv /projects/tir1/singularity/ubuntu-16.04-lts_tensorflow-1.4.0_cudnn-8.0-v6.0.img
################################################

################################################
# Set variables
################################################
MY_BASE_DIR=/home/anjalief/agenda-setting
MY_NEWS_DIR=/projects/tir1/users/anjalief/nyt_filtered
_LANGUAGE_=english

 LDA_MODEL="${MY_BASE_DIR}/models/lda_english.pkl"
# FORCE TRAIN
# python ${MY_BASE_DIR}/src/lda.py --article_glob "${MY_NEWS_DIR}/*/*.txt.tok" \
#      --force_train --output_topic_distribution --lda_model ${LDA_MODEL} >> run_english4.out

# LOAD TRAINED MODEL
# ${MY_BASE_DIR}/src/lda.py --article_glob "${MY_NEWS_DIR}/*/*.txt.tok" \
#     --output_topic_distribution --lda_model ${LDA_MODEL}

# Get topic distribution of an external-policy related article using trained LDA model
# ${MY_BASE_DIR}/src/lda.py \
#    --article_glob "${MY_BASE_DIR}/work/us_foreign_policy_wiki.txt.tok" \
#    --output_topic_distribution --lda_model ${LDA_MODEL}


# Print number of articles about external policy per month per topic
MONTHS=(01 02 03 04 05 06 07 08 09 10 11 12)

for topic_dir in ${MY_NEWS_DIR}/*; do
   topic=`basename $topic_dir`
   echo $topic
   log_file=../work/topic_stats_${topic}.lda
   touch ${log_file}
   for month in ${MONTHS[@]}; do
     ${MY_BASE_DIR}/src/per_month_lda.py \
       --gold_vectors "${MY_BASE_DIR}/data/us_foreign_policy_wiki.txt.tok.lda" \
       --log_file "${log_file}" \
       --per_month_glob "${topic_dir}/*_${month}.txt.tok.lda"
   done
done
#####################################################################