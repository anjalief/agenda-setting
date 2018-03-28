#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import pandas

# Russian to English dict
russian_to_english = {
    "Да" : "Yes",
    "Нет" : "No",

    "Иностранные Субъекты являются главными участниками в статье, а Российские Субъекты не упоминаются" : "Only foreign entities are mentioned",
    "Иностранные Субъекты являются главными участниками в статье; Российские Субъекты тоже упоминаются, но лишь мимоходом" : "Russian entities are mentioned but only in passing",
    "Российские Субъекты являются главными участниками в статье" : "Russian entities are prominent in the article",


    "абсолютно позитивнoй" : "Very Positive",
    "в основном позитивной" : "Somewhat Positive",
    "нейтральной" : "Neutral",
    "в основном негативной" : "Somewhat Negative",
    "абсолютно негативной" : "Very Negative",

    # THESE ARE NEW
    "некоторые положительное, а некоторые отрицательно" : "Some are positive and some are negative",
    "некоторых положительно, а некоторых отрицательно" : "Some are positive and some are negative",
    "ненекоторых положительно, а некоторых отрицательноe" : "Some are positive and some are negative",
    "ненекоторых положительно, а некоторых отрицательноe" : "Some are positive and some are negative",
    "некоторые положительное, а некоторые отрицательное" : "Some are positive and some are negative",
    "к некоторым позитивной, а к некоторым  негативной" : "Some are positive and some are negative",
    "абсолютно отрицательное" : "Very Negative",
    "абсолютно положительное" : "Very Positive",
    "нейтрально" : "Neutral",

    "абсолютно положительными" : "Very Positive",
    "в основном положительными" : "Somewhat Positive",
    "нейтральными" : "Neutral",
    "в основном отрицательными" : "Somewhat Negative",
    "абсолютно отрицательными" : "Very Negative",
    "Некоторые положительными, а некоторые отрицательными" : "Some are positive and some are negative",

    # You
    "абсолютно положительно" : "Very Positive",
    "в основном положительно" : "Somewhat Positive",
    "нейтрально" : "Neutral",
    "в основном отрицательно" : "Somewhat Negative",
    "абсолютно отрицательно" : "Very Negative",

    "некоторые положительными, а некоторые отрицательными" : "Some are positive and some are negative",

    "для некоторых позитивнoй, а для некоторых негативной" : "Some are positive and some are negative",

    "Россия не упомянута в статье" : "Russia is not mentioned in the article",
    "Очень слабая" : "Very Unpowerful",
    "В основном слабая" : "Somewhat Unpowerful",
    "Не слабая и не сильная" : "Neutral",
    "В основном сильная" : "Somewhat powerful",
    "Очень сильная" : "Very powerful",

    "Очень слабые" : "Very Unpowerful",
    "В основном слабые" : "Somewhat Unpowerful",
    "Не слабые и не сильные" : "Neutral",
    "В основном сильные" : "Somewhat powerful",
    "Очень сильные" : "Very powerful",
    "Некоторые сильные, а некоторые слабые" : "Some are strong and some are weak",


    "Автор абсолютно непредвзят" : "Objective",
    "Автор в основном непредвзят" : "Mostly Objective",
    "Автор частично предвзят" :  "Somewhat Biased",
    "Автор крайне предвзят" : "Very Biased",

    "В статье упомянут лишь один Иностранный Субъект" : "The article does not mention more than 1 entity",


    "Субъекты друг на друга никак не влияют" : "No Impact (These entites have no interaction)",
    "абсолютно положительное" : "Very Positive",
    "в основном положительное" : "Somewhat Positive",
    "нейтральное" : "Neutral",
    "в основном отрицательное" : "Somewhat Negative",
    "абсолютно отрицательное" : "Very Negative",
    "Некоторые положительными, а некоторые отрицательными" : "Some are positive and some are negative",

    "Абсолютно уверен" : "Very Confident",
    "В основном уверен" : "Confident",
    "Не очень уверен" : "Uncertain",
    "Абсолютно не уверен" : "Very Uncertain"
}

qs_to_english = {
"Описывается ли в статье ситуация, в которой фигурируют Иностранные Субъекты? Например, страна/город или другие географические объекты; организация/фирма или другие юридические лица; политический/общественный/религиозный деятель или другие иностранные субъекты." : "The article describes a situation that involves foreign entities",

"Кто является главными участниками в этой статье?" : "Who are the main entities in the article?",

"В статье описывается ситуация, которая является _________ для её главных участников" : "The article describes a situation that is _________ for the people directly involved",

"О чем статья? Опишите в 1-2 предложениях основной смысл статьи." : "In 1-2 sentence describe the main focus and point of the article; what is the article about, and what point is the article trying to make?",

"В какой степени Россия изображена как сильная, мощная, могущественная страна?" : "To what extent is Russia portrayed as powerful?",

"В какой степени Иностранные Субъекты изображены как сильные, мощные, могущественные?" : "To what extent are foreign entites portrayed as powerful?",

"Пожалуйста, объясните вкратце Ваши ответы о расстанове сил между Субъектами." : "Please briefly justify your answers about power",

"Отношение автора статьи к ситуации, описанной в статье является _________" : "The writer's attitude toward the situation is:",

"Отношение автора статьи к России является _________" : "The writer's attitude toward Russia is:",

"Отношение автора статьи к Иностранным Субъектам, описанным в статье является _________" : "The writer's attitude toward foreign entities is:",

"В какой степени автор статьи относится к ситуации предвзято?" : "To what extent is the writer biased?",

"С точки зрения России, ситуация, описанная в статье является _________" : "From Russia's perspective, the situation is:",

"С точки зрения России, Иностранные Субъекты, описанные в статье являются _________" : "From Russia's perspective, the foreign entities are:",

"С точки зрения Иностранных Субъектов, фигурирующих в статье, ситуация является _________" : "From the perspective of the foreign entities described, the situation is:",

"Если вы ответили на предыдущий вопрос «негативной», пожалуйста поясните вкратце:" : "If you answered \"Negative\" for the previous question, please provide a brief justification",

"Иностранные Субъекты, фигурирующие в статье, относятся друг к другу  _________" : "The foreign entities perceive each other as:",

"Лично Вы, воспринимаете ситуацию, описанную в статье _________" : "You perceive the situation as:",

"Лично Вы, воспринимаете Россию _________" : "You perceive Russia as:",

"Лично Вы, воспринимаете Иностранных Субъектов, фигурирующих в статье _________" : "You perceive foreign entities as:",

"В ситуации, описаннoй в статье, Российские Субъекты оказывают  ________ влияние на Иностранных Субъектов" : "In this situation, Russian entities have a ________ impact on foreign entities",

"В ситуации, описаннoй в статье, Иностранные Субъекты оказывают  ________ влияние на Российских Субъектов" : "In this situation, foreign entities have a ________ impact on Russian entities",

"В ситуации, описаннoй в статье, Иностранные Субъекты не являющиеся соотечественниками друг друга оказывают  ________ влияние друг на друга" : "In this situation, foreign entities from different countries have a ________ impact on each other",

"В ситуации, описаннoй в статье, Иностранные Субъекты являющиеся соотечественниками друг друга оказывают  ________ влияние друг на друга" : "In this situation, foreign entities from the same countries have a ________ impact on each other",

"Насколько вы уверенны в Вашем ответе?" : "How confident are you in this answer?",

"Есть ли у вас дополнительные комментарии к этой статье, что-то о чем мы не спросили?" : "Do you have any further comments on this article?"
}

long_answer_qs = {
    "О чем статья? Опишите в 1-2 предложениях основной смысл статьи." : "In 1-2 sentence describe the main focus and point of the article; what is the article about, and what point is the article trying to make?",
    "Пожалуйста, объясните вкратце Ваши ответы о расстанове сил между Субъектами." : "Please briefly justify your answers about power",
    "Если вы ответили на предыдущий вопрос «негативной», пожалуйста поясните вкратце:" : "If you answered \"Negative\" for the previous question, please provide a brief justification",
    "Есть ли у вас дополнительные комментарии к этой статье, что-то о чем мы не спросили?" : "Do you have any further comments on this article?"
}

# used to split into articles
QUESTION_NUMBER=38

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--annotations_file")
    args = parser.parse_args()

    df = pandas.read_csv(args.annotations_file)

    # convert everything to english
    # first column is timestamp
    english_columns = ["Timestamp"]
    for j in range(1, len(df.columns)):
        label = qs_to_english.get(df.columns[j].strip(), None)
        if label is None:
            label = qs_to_english.get(df.columns[j].strip()[:-2], None)
        if label is None:
            label = qs_to_english.get(df.columns[j].strip()[:-3], None)
        if label is None:
            label = qs_to_english.get(df.columns[j].strip()[:-4], None)
        if label is None:
            print ("ERROR")
            print (df.columns[j], df.columns[j].strip()[:-2])
            break
        english_columns.append(label)
        for i in range(0, len(df)):
            # pandas adds column idx, so cut last two characters
            if df.columns[j][:-2] in long_answer_qs or df.columns[j] in long_answer_qs:
                continue
            try:
                df.iloc[i, j] = russian_to_english[df.iloc[i, j]]
            except KeyError:
                print ("KEY_ERROR")
                print (df.iloc[i, j])
                print (df.columns[j][:-2])
                break

    # split in articles
    # make a seperate file for each annotator
    for i in range(0, len(df)):
        filename = args.annotations_file + "_annotator_" + str(i + 1) + "_v2"
        fp = open(filename, "w")

        # write column headers, first line of csv
        fp.write("|".join(english_columns[1:QUESTION_NUMBER + 1]))
        fp.write("\n")

        for j in range(1, len(df.columns), QUESTION_NUMBER):
            end = j + QUESTION_NUMBER
            fp.write("|".join([str(x).replace("\n",". ").replace("\r", ". ") for x in (df.iloc[i][j:end])]))
            fp.write("\n")
        fp.close()
        # flip rows and columns
        df_flat = pandas.read_csv(filename, delimiter="|")
        df_flat.transpose().to_csv(filename, sep="|")

if __name__ == "__main__":
    main()
