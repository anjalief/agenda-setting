import sys
import re

filename = sys.argv[1]


fp = open(filename)
lines = fp.readlines()
fp.close()



## Script to identify list of topics
## we want to break TechnologyBusiness into "Technology" and "Business"
## But we want to keep RealEstate as RealEstate


# Store each topic by it's subsets.
# ex "Book" -> "Book", "BookBusiness", "ArtBook"
topics_by_keyword = {}

for line in lines:
    line = line.strip()
    topics = re.findall('[A-Z][^A-Z]*', line)
    for topic in topics:
        if topic in topics_by_keyword:
            topics_by_keyword[topic].append(line)
        else:
            topics_by_keyword[topic] = [line]

final_topics = {}  # just use a dict to avoid duplicates
for keyword in topics_by_keyword:
    subset = topics_by_keyword[keyword]
    min_length = 1000
    min_topic = ""
    for topic in subset:
        if len(topic) < min_length:
            min_length = len(topic)
            min_topic = topic
    final_topics[min_topic] = keyword

print final_topics.keys()
print len(final_topics)

for topic in final_topics.keys():
    print topic



### OUTPUT
# anjalief@moto:~/agenda-setting/src$ python get_topics.py ~/corpora/nyt_news/topic_list.txt
# ['PublicEditor', 'Booming', 'Arts', 'RealEstate', 'TimesInsider', 'NewYork', 'Unknown', 'Travel', 'Multimedia', 'NYTNow', 'NewYorkandRegion', 'Sports', 'CorrectionsEditorsNotes', 'BusinessDay', 'Olympics', 'GreatHomesandDestinations', 'HomeandGarden', 'TimesTopics', 'TimesMachine', 'NYRegion', 'Food', 'Business', 'Automobiles', 'DiningandWine', 'UrbanEye', 'AfternoonUpdate', 'Movies', 'Obituaries', 'JobMarket', 'FashionStyle', 'World', 'SundayReview', 'Blogs', 'PaidDeathNotices', 'Theater', 'DiningWine', 'Topics', 'Science', 'Style', 'HomeGarden', 'Universal', 'MultimediaPhotos', 'Magazine', 'TodaysPaper', 'WeekInReview', 'Corrections', 'Opinion', 'YourMoney', 'Autos', 'TheUpshot', 'CrosswordsGames', 'GreatHomesDestinations', 'Open', 'National', 'Washington', 'US', 'InternationalHome', 'Books', 'College', 'WeekinReview', 'Learning', 'Health', 'Education', 'Technology', 'FrontPage', 'Giving']
# 66
# anjalief@moto:~/agenda-setting/src$
