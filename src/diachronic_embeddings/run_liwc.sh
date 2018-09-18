python correlations_with_lexicon.py --model_path /usr1/home/anjalief/word_embed_cache/ner_model_cache/izvestia_quarterly/ --keywords ./keywords.txt --econ_file /usr1/home/anjalief/corpora/russian/russian_rtsi_rub.csv --timestep quarterly --pos_lexicon ./liwc127.txt > reg_iz_quarterly_127.out

python correlations_with_lexicon.py --model_path /usr1/home/anjalief/word_embed_cache/wide_model_cache/izvestia_quarterly/ --keywords ./keywords.txt --econ_file /usr1/home/anjalief/corpora/russian/russian_rtsi_rub.csv --timestep quarterly --pos_lexicon ./liwc127.txt > wide_iz_quarterly_127.out

python correlations_with_lexicon.py --model_path /usr1/home/anjalief/word_embed_cache/reload_base_cache/izvestia_quarterly/ --keywords ./keywords.txt --econ_file /usr1/home/anjalief/corpora/russian/russian_rtsi_rub.csv --timestep quarterly --pos_lexicon ./liwc127.txt > reload_iz_quarterly_127.out


# yearly
python correlations_with_lexicon.py --model_path /usr1/home/anjalief/word_embed_cache/ner_model_cache/izvestia_yearly/ --keywords ./keywords.txt --econ_file /usr1/home/anjalief/corpora/russian/russian_yearly_gdp.csv --timestep yearly --pos_lexicon ./liwc127.txt > reg_iz_yearly_127.out

python correlations_with_lexicon.py --model_path /usr1/home/anjalief/word_embed_cache/wide_model_cache/izvestia_yearly/ --keywords ./keywords.txt --econ_file /usr1/home/anjalief/corpora/russian/russian_yearly_gdp.csv --timestep yearly --pos_lexicon ./liwc127.txt > wide_iz_yearly_127.out

python correlations_with_lexicon.py --model_path /usr1/home/anjalief/word_embed_cache/reload_base_cache/izvestia_yearly/ --keywords ./keywords.txt --econ_file /usr1/home/anjalief/corpora/russian/russian_yearly_gdp.csv --timestep yearly --pos_lexicon ./liwc127.txt > reload_iz_yearly_127.out
