#!/bin/bash

MY_TEST_DIR=/projects/tir1/users/anjalief/annotated_russia
MY_BASE_DIR=/home/anjalief/agenda-setting
LDA_MODEL="${MY_BASE_DIR}/models/lda_russia.pkl"

# Get topic distribution using trained LDA model
# ${MY_BASE_DIR}/src/lda.py \
#    --article_glob "${MY_TEST_DIR}/*.txt" \
#    --output_topic_distribution --lda_model ${LDA_MODEL}

# make sure we're using the same  model
# ${MY_BASE_DIR}/src/lda.py \
#    --article_glob "${MY_BASE_DIR}/data/focused_crawl/russian/external_policy.txt.tok.lda" \
#    --output_topic_distribution --lda_model ${LDA_MODEL}

# python eval_lda.py --gold_vectors "${MY_BASE_DIR}/data/focused_crawl/russian/external_policy.txt.tok.lda" --filename "${MY_TEST_DIR}/tune_pravda.txt.lda" --true_vals "${MY_TEST_DIR}/tune_pravda.txt.labels"

python eval_lda.py --gold_vectors "${MY_BASE_DIR}/data/focused_crawl/russian/external_policy.txt.tok.lda" --filename "${MY_TEST_DIR}/tune_isvestiia.txt.lda" --true_vals "${MY_TEST_DIR}/tune_isvestiia.txt.labels"
