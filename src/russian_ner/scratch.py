# lines = open("subs_round2.txt").readlines()
# r_set = set()
# for line in lines:
#     words = line.split(",")
#     for word in words:
#         for w in word.split():
#             r_set.add(w)

# r_list = list(r_set)
# r_list.sort()
# for s in r_list:
#     print(s)

# lines = [l.strip() for l in open("subs_round2.txt").readlines()]
# print (",".join(lines))

#R = "RUSSIA,Рогозину,Россией,Россиею,России,Россий,Российская,Российские,Российский,Российским,Российскими,Российских,Российско,Российского,Российское,Российской,Российском,Российскому,Российскую,Россию,Россия,Россиям,Россиями,Россияне,российско,руссии,руссияьсь,русские,русским,русских,русско,русского,русской"
# R = "Америка,Американская,Американские,Американский,Американских,Американское,Американской,Американскую,Американцев,Американцы,Америке,Америки,Америкой,Америку,САСШ,США,американо,американская,американские,американский,американским,американских,американско,американского,американское,американской,американском,американскую,американцами,американцев,американцы"

# russia = R.lower().split(",")
# text = open("cleaned_round3.txt").read()
# for name in russia:
#     text = text.replace(name,"")
# fp = open("cleaned_round3.txt", "w")
# fp.write(text)
# fp.close()



# text = "USA ,США Европа,САСШ,США Гуантанамо,американская,Американских,Америкой,Америкой ,Америки Грузия,Американские индейцы,США государства,американцев,Американские,Америку Америкой,США Грузия,Штатов Америки,американский,США ,Америке ,Соединенными Штатами,Америкой Чечни,США Брюсселю,Соединёнными Штатами Америки,Америки Иран,американско,Американский,Штаты Америки,Американские СМИ,Америке Ира,США Китаю,американских,американцами,Соединенных Штатах,американскую,США Киеву,американское,Соединенных Штатов,Америка ВСУ,Американские Штаты,Соединенным Штатам,американские,Американское государство,американским,США Франции,Америка ,Соединенные Штаты,Соединенные Штаты Африки,Американская,Американской республики,Соединенные Штаты Америки,США Армении,США Израилем,американском МИДе,Империи Соединенных Штатов,Соединенным Штатами,США Вашингтона,США Вашингтоне,американского,США Филиппины,Америки Китаю,Африка,Америки ,американской,американском Госдепе,Америке,Американских Виргинских островов,США Украине,США Казахстан,США ,США ,американцы,Американской империи,Американские Виргинские острова,США,Американская империя,американскую империю,США Мексике,американского Союза,Америка,Американских Штатов,Американское,американского Юга,Америку Исламское государство,США Поднебесная,США Кубы,США ,американском Юге,США Британия,Американцы,Американских Соединенных Штатов,Америка империей,Соединенным Штатам Америки,Американцев,США Египту,американо,США Вашингтон,американского Ирака,Штатах Америки,Американскую,Соединенные Государства Америки,Америку,Америки,Империей Соединенных Штатов"

# usa = text.split(",")
# usa_set = set()
# for words in usa:
#     word = words.split()
#     for w in word:
#         usa_set.add(w)
# usa_list = list(usa_set)
# usa_list.sort()
# for l in usa_list:
#     print (l)


# text = open("cleaned_round3.txt").readlines()
# for line in text:
#     splits = line.split(",")
#     for x in splits:
#         s = x.split()
#         if len(s) > 1:
#             print (splits[0], x)

from count_country_mentions import do_counts
import sys
sys.path.append("..")
from article_utils import *

input_path = "/usr1/home/anjalief/corpora/russian/yearly_mod_subs/iz_lower/"
# date_seq, filenames = get_files_by_time_slice(input_path, "yearly")
# print (filenames)
# country_to_article_sequence, country_to_words_sequence = do_counts(filenames, "cleaned_round3.txt")

# for date,x in zip(date_seq, country_to_words_sequence["USA"]):
#     print(date, x)

from econ_utils import load_yearly_rtsi, load_semi_rtsi

# year_to_vals = load_yearly_rtsi("/usr1/home/anjalief/corpora/russian/russian_rtsi_rub.csv")

# for year in sorted(year_to_vals):
#     print (year, year_to_vals[year][3])

year_to_vals = load_semi_rtsi("/usr1/home/anjalief/corpora/russian/russian_rtsi_rub.csv")
date_seq, filenames = get_files_by_time_slice(input_path, "semi")

print (date_seq)
country_to_article_sequence, country_to_words_sequence = do_counts(filenames, "cleaned_round3.txt")

for d,a in zip(date_seq, country_to_words_sequence["USA"]):
    print(d, year_to_vals[d][3], a)
