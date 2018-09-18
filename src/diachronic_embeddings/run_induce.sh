# python induce_lex.py  --model_path /usr1/home/anjalief/word_embed_cache/ner_model_cache/izvestia_quarterly/ --keywords ./keywords.txt --econ_file /usr1/home/anjalief/corpora/russian/russian_rtsi_rub.csv --timestep quarterly > adj_lex.out

python induce_lex.py  --model_path /usr1/home/anjalief/word_embed_cache/wide_model_cache/izvestia_quarterly/ --keywords ./keywords.txt --econ_file /usr1/home/anjalief/corpora/russian/russian_rtsi_rub.csv --timestep quarterly > wide_adj_lex.out

python induce_lex.py  --model_path /usr1/home/anjalief/word_embed_cache/reload_base_cache/izvestia_quarterly/ --keywords ./keywords.txt --econ_file /usr1/home/anjalief/corpora/russian/russian_rtsi_rub.csv --timestep quarterly > reload_adj_lex.out

# yearly
python induce_lex.py  --model_path /usr1/home/anjalief/word_embed_cache/ner_model_cache/izvestia_yearly/ --keywords ./keywords.txt --econ_file /usr1/home/anjalief/corpora/russian/russian_yearly_gdp.csv --timestep yearly > yearly_adj_lex.out

python induce_lex.py  --model_path /usr1/home/anjalief/word_embed_cache/wide_model_cache/izvestia_yearly/ --keywords ./keywords.txt --econ_file /usr1/home/anjalief/corpora/russian/russian_yearly_gdp.csv --timestep yearly > yearly_wide_adj_lex.out

python induce_lex.py  --model_path /usr1/home/anjalief/word_embed_cache/reload_base_cache/izvestia_yearly/ --keywords ./keywords.txt --econ_file /usr1/home/anjalief/corpora/russian/russian_yearly_gdp.csv --timestep yearly > yearly_reload_adj_lex.outr