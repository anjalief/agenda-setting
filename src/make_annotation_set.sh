#!/bin/bash

RUSSIA_DIR=/projects/tir1/users/anjalief/russian_monthly
RUSSIA_ALL_NEWS=/projects/tir1/users/anjalief/russian_news
ANNO_DIR=/projects/tir1/users/anjalief/annotated_russia


# Build economic lexicon
source ~/venv/agenda_setting/bin/activate
# python generate_counts.py
# python log_odds_ratio.py -f business_counts.txt -s all_counts.txt  > nyt_business_odds.txt

# Build external mix of Pravda/Izvestiia
# python make_annotation_set.py --article_glob "${RUSSIA_DIR}/*/2007/2007.txt.tok" --tune_file_name "${ANNO_DIR}/topic/external_2007.txt" --country_list "${ANNO_DIR}/countries_languages.txt" --merge_labels

# python make_annotation_set.py --article_glob "${RUSSIA_DIR}/*/2009/2009.txt.tok" --tune_file_name "${ANNO_DIR}/topic/external_2009.txt" --country_list "${ANNO_DIR}/countries_languages.txt" --merge_labels

# python make_annotation_set.py --article_glob "${RUSSIA_DIR}/*/2007/2007.txt.tok" --tune_file_name "${ANNO_DIR}/topic/business_2007.txt" --country_list "${ANNO_DIR}/business_from_nyt.txt" --merge_labels

# An attempt to economic articles but doesn't really work
# python make_annotation_set.py --article_glob "${RUSSIA_DIR}/*/2009/2009.txt.tok" --tune_file_name "${ANNO_DIR}/topic/business_2009.txt" --country_list "${ANNO_DIR}/business_from_nyt.txt" --merge_labels

# Pull annotation set from all Pravda and Izvestiia
# python make_annotation_set.py --article_glob "${RUSSIA_ALL_NEWS}/*_use/2*.txt.tok" --tune_file_name "${ANNO_DIR}/annotation_set_20180131_2.txt" --country_list "${ANNO_DIR}/countries.txt"

# ./make_annotation_set.py --article_glob "${RUSSIA_ALL_NEWS}/Pravda/2007.txt.tok" --file_name Pravda_2007_samples --num_samples 2 --sample_size 50 --country_list "${ANNO_DIR}/countries.txt"

# ./make_annotation_set.py --article_glob "${RUSSIA_ALL_NEWS}/Izvestiia/2007.txt.tok" --file_name Izvestiia_2007_samples --num_samples 2 --sample_size 50 --country_list "${ANNO_DIR}/countries.txt"

# ./make_annotation_set.py --article_glob "${RUSSIA_ALL_NEWS}/Pravda/2009.txt.tok" --file_name Pravda_2009_samples --num_samples 2 --sample_size 50 --country_list "${ANNO_DIR}/countries.txt"

# ./make_annotation_set.py --article_glob "${RUSSIA_ALL_NEWS}/Izvestiia/2009.txt.tok" --file_name Izvestiia_2009_samples --num_samples 2 --sample_size 50 --country_list "${ANNO_DIR}/countries.txt"

# python shuffle_sets.py --file1 "Pravda_2009_samples0" --file2 "Izvestiia_2009_samples0" --outfile "shuffled_2009_0.txt"

# python shuffle_sets.py --file1 "Pravda_2007_samples0" --file2 "Izvestiia_2007_samples0" --outfile "shuffled_2007_0.txt"

# python shuffle_sets.py --file1 "shuffled_2009_0.txt" --file2 "shuffled_2007_0.txt" --outfile "shuffled_0.txt"

python shuffle_sets.py --file1 "${ANNO_DIR}/Izvestiia_2009_samples0" --file2 "${ANNO_DIR}/Izvestiia_2007_samples0" --shortestn 10 --outfile "${ANNO_DIR}/shuffled_Izvestiia0.txt"


# for a in 0 2 3 4 5 6 7
# do
#   python shuffle_sets.py --file1 "2007_samples${a}" --file2 "2009_samples${a}" --outfile "shuffled_${a}.txt"
# done