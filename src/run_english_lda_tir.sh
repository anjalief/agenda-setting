#!/bin/bash

################################################
# For Tir, we need to run python in a virtual env
# module load singularity
# singularity shell --nv /projects/tir1/singularity/ubuntu-16.04-lts_tensorflow-1.4.0_cudnn-8.0-v6.0.img
################################################

################################################
# Set variables
################################################
source ~/venv/agenda_setting/bin/activate

MY_BASE_DIR=/home/anjalief/agenda-setting
MY_NEWS_DIR=/projects/tir1/users/anjalief/nyt_filtered
MY_CLEAN_DIR=/projects/tir1/users/anjalief/nyt_stem
MY_TEST_DIR=/projects/tir1/users/anjalief/annotated_nyt
_LANGUAGE_=english


# python preprocess_english.py --article_glob "${MY_NEWS_DIR}/*/*.txt.tok" --output_dir /projects/tir1/users/anjalief/nyt_stem

LDA_MODEL="${MY_BASE_DIR}/models/lda_english_50.pkl"
LDA_MODEL_25="${MY_BASE_DIR}/models/lda_english.pkl"
LDA_MODEL_25_clean="${MY_BASE_DIR}/models/lda_english_25_clean.pkl"
# FORCE TRAIN, don't ouput topics
# python ${MY_BASE_DIR}/src/lda.py --article_glob "${MY_CLEAN_DIR}/*/*.txt.tok" \
#     --force_train --output_topic_distribution --outfile_suffix ".25" --lda_model ${LDA_MODEL_25_clean} --stopwords ${MY_TEST_DIR}/english_stopwords.txt >> run_english_clean.out

# python ${MY_BASE_DIR}/src/lda.py --lda_model ${LDA_MODEL_25} --top_n_words 30 >> get_topics_25.out

# LOAD TRAINED MODEL
# ${MY_BASE_DIR}/src/lda.py --article_glob "${MY_NEWS_DIR}/*/*.txt.tok" \
#    --output_topic_distribution --lda_model ${LDA_MODEL} --outfile_suffix ".50"

# ${MY_BASE_DIR}/src/lda.py --article_glob "${MY_TEST_DIR}/*file.txt" \
#     --output_topic_distribution --lda_model ${LDA_MODEL} --outfile_suffix ".50"

# ${MY_BASE_DIR}/src/lda.py --article_glob "${MY_TEST_DIR}/*file.txt" \
#    --lda_model ${LDA_MODEL} --top_n_words 30

# Get topic distribution using trained LDA model
# ${MY_BASE_DIR}/src/lda.py \
#    --article_glob "${MY_TEST_DIR}/*.txt" \
#    --output_topic_distribution --lda_model ${LDA_MODEL}


# Print number of articles about external policy per month per topic
# MONTHS=(01 02 03 04 05 06 07 08 09 10 11 12)

# for topic_dir in ${MY_NEWS_DIR}/Arts; do
#    topic=`basename $topic_dir`
#    echo $topic_dir
#    log_file=../work/topic_stats_${topic}_TEST.lda
#    touch ${log_file}
#    for month in ${MONTHS[@]}; do
#      ${MY_BASE_DIR}/src/per_month_lda.py \
#        --gold_vectors "${MY_BASE_DIR}/data/us_foreign_policy_wiki.txt.tok.lda" \
#        --log_file "${log_file}" \
#        --per_month_glob "${topic_dir}/*_${month}.txt.tok.lda"
#    done
# done
#####################################################################
# limit to 2000s
# python make_csv.py --article_glob "/projects/tir1/users/anjalief/all_nyt_paras_text/*/20*_*.txt.tok" --outfile "nyt_monthly.csv"
# python remove_corrections.py

./baseline_per_month.py --outfile "english_monthly_baseline2.txt" --article_glob "/projects/tir1/users/anjalief/nyt_stem/*/2*.txt.tok" --country_list "/projects/tir1/users/anjalief/annotated_nyt/countries.txt"