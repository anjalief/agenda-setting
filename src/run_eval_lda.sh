#!/bin/bash

MY_TEST_DIR=/projects/tir1/users/anjalief/annotated_nyt
MY_BASE_DIR=/home/anjalief/agenda-setting
MY_NEWS_DIR=/projects/tir1/users/anjalief/nyt_filtered

# python eval_lda.py --gold_vectors "${MY_BASE_DIR}/data/us_foreign_policy_wiki.txt.tok.lda" --filename "${MY_TEST_DIR}/tune_file.txt.lda" --true_vals "${MY_TEST_DIR}/tune_file.txt.labels"

# python eval_lda.py --gold_vectors "${MY_BASE_DIR}/data/us_foreign_policy_wiki.txt.tok.50.lda" --filename "${MY_TEST_DIR}/tune_file.txt.50.lda" --true_vals "${MY_TEST_DIR}/tune_file.txt.labels" --track_by_topic


# THRESH=(0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.75 0.8 0.85 0.9 0.95)

# for t in ${THRESH[@]}; do
#     ${MY_BASE_DIR}/src/eval_lda_by_topic.py \
#         --gold_vectors "${MY_BASE_DIR}/data/us_foreign_policy_wiki.txt.tok.50.lda" \
#         --per_month_glob "${MY_NEWS_DIR}/*/*.txt.tok.50.lda" \
#         --similarity_threshold ${t} --log_file "./summary_50_"
# done


# BASELINE
# python baseline.py --article_glob "${MY_NEWS_DIR}/*/*.tok.lda" --log_file test_baseline.out
# python baseline.py --labeled_data "${MY_TEST_DIR}/tune_file.txt.lda" --log_file test_baseline.out

# MORE BASIC BASELINE
# python baseline_country.py --article_glob "/projects/tir1/users/anjalief/nyt_filtered/*/*.txt.tok" --country_list "/projects/tir1/users/anjalief/annotated_nyt/countries.txt"

python baseline_country.py --labeled_data "${MY_TEST_DIR}/tune_file.txt" --country_list "${MY_TEST_DIR}/countries_languages.txt"

# GATHER ARTICLES TO LOOK AT
# python get_article_sample.py --outfile "/projects/tir1/users/anjalief/annotated_nyt/baseline_country_only" --article_glob "/projects/tir1/users/anjalief/nyt_filtered/*/*.txt.tok" --country_list "/projects/tir1/users/anjalief/annotated_nyt/countries.txt"
