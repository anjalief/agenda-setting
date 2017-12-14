import sys
import re

filename = sys.argv[1]


fp = open(filename)
lines = fp.readlines()
fp.close()



## Script to identify topics that are cross-listed with "Business"
## Doesn't really work, because we end up exlcuding only things like
# "Style", because something that is "StyleTechnology" gets included
# because "TechnologyBusiness" is a topic

# two pass approach
# first pass: get all topics that
# have "Business" in them
# second pass: get all topics that match
# topics from the first set

# use dict to avoid duplicates
topics_with_Business = {}
for line in lines:
    line = line.strip()
    if "Business" in line:
        topics = re.findall('[A-Z][^A-Z]*', line)
        for topic in topics:
            topics_with_Business[topic] = 1

topics_to_keep = {}
topics_to_x = {}
all_topics = {}

print topics_with_Business
print ""

for line in lines:
    line = line.strip()
    topics = re.findall('[A-Z][^A-Z]*', line)
    add = False
    for topic in topics:
        all_topics[topic] = 1
        if topic in topics_with_Business:
            add = True
            break
    if add:
        topics_to_keep[line] = 1
    else:
        topics_to_x[line] = 1


print topics_to_keep
print ""
print topics_to_x
print "TOPIC COUNT", len(all_topics)
