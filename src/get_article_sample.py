# script to pull articles per NYT times topics
# current version pulls articles that are external according to baseline
# writes articles to files called "topic.txt"

from article_utils import LoadArticles
from baseline_country import get_countries, contains_country
import argparse
import os

MAX_PER_TOPIC = 10

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--article_glob')
    parser.add_argument('--country_list')
    parser.add_argument('--outfile')
    args = parser.parse_args()

    countries = get_countries(args.country_list)

    dirname_to_articles = {}

    articles, article_index = LoadArticles(args.article_glob)

    for a,i in zip(articles, article_index):

        dirname = os.path.dirname(i[0])
        base_dirname = os.path.basename(dirname)

        # we don't need any more articles on this topic
        curr_list = dirname_to_articles.get(base_dirname, [])
        if len(curr_list) >= MAX_PER_TOPIC:
            continue

        words = a.split()
        count_this_article = contains_country(words, countries)

        if count_this_article:
            curr_list.append((a, i))

            dirname_to_articles[base_dirname] = curr_list

    # output each topic to its own file
    for t in dirname_to_articles:
        fp = open(args.outfile + "/" + t + ".txt", "w")
        for a in dirname_to_articles[t]:
            fp.write(str(a[1]) + "\n" + a[0] + "\n\n")
        fp.close()

if __name__ == '__main__':
  main()

