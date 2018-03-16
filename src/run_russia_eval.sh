#!/bin/bash

source activate py36
MY_TEST_DIR=/projects/tir1/users/anjalief/annotated_russia
MY_NEWS_DIR=/projects/tir1/users/anjalief/russian_news
MONTHLY_NEWS_DIR=/projects/tir1/users/anjalief/russian_monthly
MY_BASE_DIR=/home/anjalief/agenda-setting
LDA_MODEL="${MY_BASE_DIR}/models/lda_russian.pkl"

# NOTE: These didn't run on tir (maybe need python3??)
# SCP'd files to moto and ran them there
# Got this to run on tir with new LDA model?
# Get topic distribution using trained LDA model
#  ALL_LDA_MODEL="${MY_BASE_DIR}/models/lda_all_russian.pkl"
# ${MY_BASE_DIR}/src/lda.py \
#    --article_glob "${MY_TEST_DIR}/*.txt.tok" \
#    --outfile_suffix ".all" \
#    --output_topic_distribution --lda_model ${ALL_LDA_MODEL}

# make sure we're using the same  model
# ${MY_BASE_DIR}/src/lda.py \
#    --article_glob "${MY_BASE_DIR}/data/focused_crawl/russian/external_policy.txt.tok.lda" \
#    --output_topic_distribution --lda_model ${LDA_MODEL}

# echo "Pravda"
# python eval_lda.py --gold_vectors "${MY_BASE_DIR}/data/focused_crawl/russian/external_policy.txt.tok.lda" --filename "${MY_TEST_DIR}/tune_pravda.txt.tok.all.lda" --true_vals "${MY_TEST_DIR}/tune_pravda.txt.labels"

# echo "Isvestiia"
# python eval_lda.py --gold_vectors "${MY_BASE_DIR}/data/focused_crawl/russian/external_policy.txt.tok.lda" --filename "${MY_TEST_DIR}/tune_isvestiia.txt.tok.all.lda" --true_vals "${MY_TEST_DIR}/tune_isvestiia.txt.labels"

# # # FYI
# # [anjalief@tir annotated_russia]$ cp tune_isvestiia.txt.labels tune_isvestiia.txt.tok.labels
# # [anjalief@tir annotated_russia]$
# # [anjalief@tir annotated_russia]$ !!:gs/isvestiia/pravda
# # cp tune_pravda.txt.labels tune_pravda.txt.tok.labels
# # [anjalief@tir annotated_russia]$

python3 baseline_country.py --labeled_data "${MY_TEST_DIR}/tune_pravda.txt.tok" --country_list "${MY_TEST_DIR}/countries.txt" # --lemmatize_russian

echo "IZVESTIA"
python3 baseline_country.py --labeled_data "${MY_TEST_DIR}/tune_isvestiia.txt.tok" --country_list "${MY_TEST_DIR}/countries.txt" # --lemmatize_russian


# python log_odds_ratio.py -f "/projects/tir1/users/anjalief/russian_news/*/2007.txt.tok" -s "/projects/tir1/users/anjalief/russian_news/*/2009.txt.tok" -c /projects/tir1/users/anjalief/annotated_russia/countries_languages.txt > logs_odds_09.txt

# Used to generate files for STM
# python make_csv.py --article_glob "${MY_NEWS_DIR}/*_use/*.txt.tok" --outfile "russian_use.csv"
# python make_csv.py --article_glob "${MONTHLY_NEWS_DIR}/*/*/*_*.txt.tok" --outfile "russian_monthly.csv"


# Count external articles in dataset using baseline
# ./baseline_per_month.py --outfile "russian_monthly_baseline.txt" --article_glob "${MONTHLY_NEWS_DIR}/*/*/*.txt.tok" --country_list "${MY_TEST_DIR}/countries.txt"

# python baseline_per_month.py --outfile "russian_monthly_baseline.txt" --reformat


# Count sentiment
# ./baseline_per_month.py --outfile "russian_pos_sentiment.txt" --article_glob "${MONTHLY_NEWS_DIR}/*/*/*_*.txt.tok" --country_list "/home/anjalief/agenda-setting/ru.filtered.pos"
# ./baseline_per_month.py --outfile "russian_neg_sentiment.txt" --article_glob "${MONTHLY_NEWS_DIR}/*/*/*_*.txt.tok" --country_list "/home/anjalief/agenda-setting/ru.filtered.neg"

# python baseline_per_month.py --outfile "russian_pos_sentiment.txt" --reformat
# python baseline_per_month.py --outfile "russian_neg_sentiment.txt" --reformat