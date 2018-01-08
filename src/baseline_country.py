# Baseline metric, count an article as external if it contains a
# word from a list of countries
# create two output files, one that's generic topic -> article counts,
# other is exact topic -> article counts (# external, total number)
from article_utils import LoadArticles, all_topics
import argparse
import os

def get_countries(filename):
    country_glob = open(filename).read()
    countries = set()
    # in country file, each line contains [country],[capital],[language1],[language2]
    for c in country_glob.split("\n"):
        for i in c.split(","):
            countries.add(i.strip())
    return countries

def contains_country(words, countries):
    count_this_article = 0

    # figure out if this article mentions another country
    for c in countries:
        if c in words:
            count_this_article = 1
            break
    return count_this_article

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--article_glob')
    parser.add_argument('--country_list')
    args = parser.parse_args()


    countries = get_countries(args.country_list)

    dirname_to_count = {}
    topic_to_count = {}
    for t in all_topics:
        topic_to_count[t] = (0,0)

    articles, article_index = LoadArticles(args.article_glob)

    for a,i in zip(articles, article_index):
        words = a.split()
        count_this_article = contains_country(words, countries)

        dirname = os.path.dirname(i[0])
        base_dirname = os.path.basename(dirname)

        count = dirname_to_count.get(base_dirname, (0, 0))
        dirname_to_count[base_dirname] = (count[0] + count_this_article,
                                          count[1] + 1)

        for t in all_topics:
            if t in base_dirname:
                count = topic_to_count[t]
                topic_to_count[t] = (count[0] + count_this_article,
                                     count[1] + 1)

    fp = open("topics_to_count.txt", 'w')
    for t in topic_to_count:
        fp.write(t + " " + str(topic_to_count[t][0]) + " "  + str(topic_to_count[t][1]) + "\n")
    fp.close()

    fp = open("subtopics_to_count.txt", 'w')
    for t in dirname_to_count:
        fp.write(t + " " + str(dirname_to_count[t][0]) + " "  + str(dirname_to_count[t][1]) + "\n")
    fp.close()



if __name__ == '__main__':
  main()
