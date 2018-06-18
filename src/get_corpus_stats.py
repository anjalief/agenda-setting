
from article_utils import LoadArticles
import glob

# articles, # tokens, #types, average monthly #  of  articles

def main():
    input_path = "/usr1/home/anjalief/corpora/russian/Izvestiia/*/*_*.txt.tok"
    sum_num_articles = 0
    sum_num_months = 0
    token_count = 0
    type_count = set()
    for filename in glob.iglob(input_path):
        sum_num_months += 1

        articles,_ = LoadArticles(filename)
        sum_num_articles += len(articles)
        for a in articles:
            words = a.lower().split()
            token_count += len(words)
            type_count = type_count.union(set(words))

    print ("Average num articles", sum_num_articles / float(sum_num_months))
    print ("num articles", sum_num_articles)
    print ("num tokens", token_count)
    print ("num types", len(type_count))


if __name__ == "__main__":
    main()
