import json
import glob
import os
import datetime

# This is still useful because outlet and date are not embedded in json

def FileIter(filename):
    for line in open(filename).readlines():
        yield json.loads(line)

def ArticleIter(article_glob):
    for filename in glob.iglob(article_glob):
        date_str = os.path.basename(filename)
        date_obj = datetime.datetime.strptime(date_str, "%Y_%m_%d").date()

        # for /path/outlet/year/filename we want to extract outlet
        outlet_name = os.path.basename(os.path.dirname(os.path.dirname(filename)))
        yield date_obj, outlet_name, FileIter(filename)




# TESTING
def main():
    # for a in FileIter("/usr1/home/anjalief/corpora/hindu_print_topics/2006/2006_01_02"):
    #     print a['body']

    word_count = 0
    for date, outlet, article_iter in ArticleIter("/usr1/home/anjalief/corpora/hindi/times_of_india/*/*"):
        for a in article_iter:
            word_count += len(a['body'].split())
    print (word_count)

if __name__ == "__main__":
    main()
