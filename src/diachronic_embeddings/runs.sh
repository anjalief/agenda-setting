#!/bin/bash

# nohup python diachronic_word_embeddings.py --input_path /usr1/home/anjalief/corpora/russian/country_sub/Isveztiia/ --cache_path /usr1/home/anjalief/word_embed_cache/wide_model_cache/izvestia_monthly/ --timestep monthly --window_size 10 > wide_monthly.out &

# nohup python diachronic_word_embeddings.py --input_path /usr1/home/anjalief/corpora/russian/liwc_sub/Izvestiia/ --initial_files "/usr1/home/anjalief/corpora/russian/liwc_sub/Izvestiia/init_files/*.txt.tok"  --cache_path /usr1/home/anjalief/word_embed_cache/liwc_model_cache/izvestia_monthly/ --timestep monthly > liwc_monthly.out &

# python induce_lex.py --keywords ./keywords.txt --model_path /usr1/home/anjalief/word_embed_cache/wide_model_cache/izvestia_yearly/ --econ_file /usr1/home/anjalief/corpora/russian/russian_yearly_gdp.csv --timestep yearly


nohup python diachronic_word_embeddings.py --input_path /usr1/home/anjalief/corpora/russian/country_sub2/Isvestiia/ --cache_path /usr1/home/anjalief/word_embed_cache/ner_model_cache2/izvestia_monthly/ --timestep monthly --initial_files "/usr1/home/anjalief/corpora/russian/country_sub2/Isvestiia/init_files/*.txt.tok" > new_monthly.out &

nohup python diachronic_word_embeddings.py --input_path /usr1/home/anjalief/corpora/russian/country_sub2/Isvestiia/ --cache_path /usr1/home/anjalief/word_embed_cache/ner_model_cache2/izvestia_quarterly/ --timestep quarterly --initial_files "/usr1/home/anjalief/corpora/russian/country_sub2/Isvestiia/init_files/*.txt.tok" > new_quarterly.out &

nohup python diachronic_word_embeddings.py --input_path /usr1/home/anjalief/corpora/russian/country_sub2/Isvestiia/ --cache_path /usr1/home/anjalief/word_embed_cache/ner_model_cache2/izvestia_yearly/ --timestep yearly --initial_files "/usr1/home/anjalief/corpora/russian/country_sub2/Isvestiia/init_files/*.txt.tok" > new_yearly.out &
