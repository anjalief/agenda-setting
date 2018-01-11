#!/bin/bash

MY_TEST_DIR=/projects/tir1/users/anjalief/annotated_russia
MY_BASE_DIR=/home/anjalief/agenda-setting
LDA_MODEL="${MY_BASE_DIR}/models/lda_russian.pkl"

# NOTE: These didn't run on tir (maybe need python3??)
# SCP'd files to moto and ran them there
# Get topic distribution using trained LDA model
# ${MY_BASE_DIR}/src/lda.py \
#    --article_glob "${MY_TEST_DIR}/*.txt" \
#    --output_topic_distribution --lda_model ${LDA_MODEL}

# make sure we're using the same  model
# ${MY_BASE_DIR}/src/lda.py \
#    --article_glob "${MY_BASE_DIR}/data/focused_crawl/russian/external_policy.txt.tok.lda" \
#    --output_topic_distribution --lda_model ${LDA_MODEL}

# echo "Pravda"
# python eval_lda.py --gold_vectors "${MY_BASE_DIR}/data/focused_crawl/russian/external_policy.txt.tok.lda" --filename "${MY_TEST_DIR}/tune_pravda.txt.tok.lda" --true_vals "${MY_TEST_DIR}/tune_pravda.txt.labels"

# echo "Isvestiia"
# python eval_lda.py --gold_vectors "${MY_BASE_DIR}/data/focused_crawl/russian/external_policy.txt.tok.lda" --filename "${MY_TEST_DIR}/tune_isvestiia.txt.tok.lda" --true_vals "${MY_TEST_DIR}/tune_isvestiia.txt.labels"

# # # FYI
# # [anjalief@tir annotated_russia]$ cp tune_isvestiia.txt.labels tune_isvestiia.txt.tok.labels
# # [anjalief@tir annotated_russia]$
# # [anjalief@tir annotated_russia]$ !!:gs/isvestiia/pravda
# # cp tune_pravda.txt.labels tune_pravda.txt.tok.labels
# # [anjalief@tir annotated_russia]$

python baseline_country.py --labeled_data "${MY_TEST_DIR}/tune_pravda.txt" --country_list "${MY_TEST_DIR}/countries_languages.txt"

# python baseline_country.py --labeled_data "${MY_TEST_DIR}/tune_isvestiia.txt" --country_list "${MY_TEST_DIR}/countries_languages.txt"


# build annotation set for 2014