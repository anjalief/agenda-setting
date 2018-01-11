# script to pull articles per NYT times topics
# current version pulls articles that are external according to baseline
# writes articles to files called "topic.txt"

from article_utils import LoadArticles, all_topics
from baseline_country import get_countries
import argparse
import os

MAX_PER_TOPIC = 10

# Returns 1 if the article contains a country word 2 times
# (can be the same word)
def contains_2_countries(words, countries):
    count = 0
    for a in words:
        if a in countries:
            count += 1
        if count == 2:
            break
    if count >= 2:
        return 1
    return 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--article_glob')
    parser.add_argument('--country_list')
    parser.add_argument('--outfile')
    args = parser.parse_args()

    countries = get_countries(args.country_list)

    topic_to_articles = {}

    articles, article_index = LoadArticles(args.article_glob)

    incomplete_topics = set()
    for t in all_topics:
        incomplete_topics.add(t)

    for a,i in zip(articles, article_index):

        dirname = os.path.dirname(i[0])
        base_dirname = os.path.basename(dirname)

        for topic in incomplete_topics:
            # consider this article for one arbitrary topic
            if topic in base_dirname:
                words = a.split()
                if contains_2_countries(words, countries):
                    curr_list = topic_to_articles.get(topic, [])
                    curr_list.append((a, i))

                    if len(curr_list) >= MAX_PER_TOPIC:
                        incomplete_topics.remove(topic)

                    topic_to_articles[topic] = curr_list
                break
        if len(incomplete_topics) == 0:
            break

    # output each topic to its own file
    for t in topic_to_articles:
        fp = open(args.outfile + "/" + t + ".txt", "w")
        for a in topic_to_articles[t]:
            fp.write(str(a[1]) + "\n" + a[0] + "\n\n")
        fp.close()

if __name__ == '__main__':
  main()

