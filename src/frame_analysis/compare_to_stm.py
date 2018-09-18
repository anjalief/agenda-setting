#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This script is for comparing framing lexicons to frames learned by a topic
# model
# You must manually align topics to frames. Then, this script computes KL divergence,
# assuming the topic model is gold
import sys
sys.path.append("..")
import argparse
import pickle
import pandas
from collections import Counter, defaultdict
from nltk import tokenize
from datetime import datetime
from econ_utils import get_corr

from params import Params

params = Params()
NUM_TOPICS = 20

# We must manually align topics
FRAME_TO_TOPIC = {"Economic": ["V2","V5"],
                  "Political": ["V19"],
#                  "Policy Prescription and Evaluation"
#                  "Public Sentiment"
#                  "Morality"
#                  "Health and Safety"
#                  "Quality of Life"
                  "Legality, Constitutionality, Jurisdiction": ["V15"],
                  "Cultural Identity": ["V17"],
                  "Crime and Punishment" : ["V12"]
#                  "Fairness and Equality"
#                  "External Regulation and Reputation"
#                  "Capacity and Resources"
#                  "Security and Defense"
#                  "Other"
                  }

class DateCounter:
    def __init__(self):
        self.total_word_count = 0
        self.frame_to_count = Counter()

    def update(self, new_count):
        self.total_word_count += new_count

    def update_frame(self, frame, new_count):
        self.frame_to_count[frame] += new_count

def compare_series(date_to_counter, date_to_topic_counter, frame_to_topic):
    # now build a normalized series for each frame
    frame_to_lex_series = defaultdict(list)
    frame_to_topic_series = defaultdict(list)

    for date in sorted(date_to_counter):
        lex_counter = date_to_counter[date]
        topic_counter = date_to_topic_counter[date]
        for frame in lex_counter.frame_to_count:
            frame_to_lex_series[frame].append(lex_counter.frame_to_count[frame] / lex_counter.total_word_count)
            frame_to_topic_series[frame].append(topic_counter.frame_to_count[frame] / topic_counter.total_word_count)

    # What can we do other than correlation?
    for frame in frame_to_topic:
        print (frame, get_corr(frame_to_lex_series[frame], frame_to_topic_series[frame]))


# Take proportion of framing words vs. average topic representation
def word_level_divergence(all_data, frame_to_lex, frame_to_topic):
    date_to_counter = defaultdict(DateCounter)
    date_to_topic_counter = defaultdict(DateCounter)

    for idx,row in all_data.iterrows():
        date = datetime.strptime(row.loc["date"], '%d/%m/%Y')

        text = tokenize.word_tokenize(row.loc["documents"])
        text_counter = Counter(text)

        # update base counts: number of words and number of articles
        date_to_counter[date].update(len(text))
        date_to_topic_counter[date].update(1)


        # No point in counting frames that we haven't aligned
        for frame in frame_to_topic:
            frame_count = sum([text_counter[w] for w in frame_to_lex[frame]])
            date_to_counter[date].update_frame(frame, frame_count)

            # We sum proportion of article on each frame
            for topic in frame_to_topic[frame]:
                date_to_topic_counter[date].update_frame(frame, row.loc[topic])

    compare_series(date_to_counter, date_to_topic_counter, frame_to_topic)

# Take if article uses frame by lexicon vs. by topic model
# (what threshold to use for topic model proportion?)
def doc_level_divergence(all_data, frame_to_lex, frame_to_topic):
    date_to_counter = defaultdict(DateCounter)
    date_to_topic_counter = defaultdict(DateCounter)

    for idx,row in all_data.iterrows():
        date = datetime.strptime(row.loc["date"], '%d/%m/%Y')

        text = tokenize.word_tokenize(row.loc["documents"])
        text_counter = Counter(text)

        # update base counts for number of articles
        date_to_counter[date].update(1)
        date_to_topic_counter[date].update(1)

        # No point in counting frames that we haven't aligned
        for frame in frame_to_topic:
            frame_count = sum([text_counter[w] for w in frame_to_lex[frame]])
            if frame_count >= params.LEX_COUNT:
                date_to_counter[date].update_frame(frame, 1)

            # We sum proportion of article on each frame
            sum_topic_frame = 0
            for topic in frame_to_topic[frame]:
                sum_topic_frame += row.loc[topic]
            if sum_topic_frame >= (len(frame_to_topic[frame]) / NUM_TOPICS):
                date_to_topic_counter[date].update_frame(frame, 1)

    compare_series(date_to_counter, date_to_topic_counter, frame_to_topic)


def main():
    parser = argparse.ArgumentParser()
    # Output of STM; csv format
    parser.add_argument("--topic_weights", default="./stm20.csv")
    # CSV file with articles and dates (i.e. input to STM)
    parser.add_argument("--article_csv", default="/usr1/home/anjalief/stm/russian/data/monthly_usa_izvestiia.csv")
    # output of parse_frames
    parser.add_argument("--frame_lex", default="./cache/frame_to_lex_v2_200.pickle")
    args = parser.parse_args()

    frame_to_lex = pickle.load(open(args.frame_lex, "rb"))

    text_data = pandas.read_csv(args.article_csv)
    topics = pandas.read_csv(args.topic_weights)

    assert len(text_data) == len(topics), "Error: STM output does not equal STM input"

    # they should be paralell, we can just merge
    all_data = pandas.concat([text_data, topics], axis=1)
    frame_to_KL = word_level_divergence(all_data, frame_to_lex, FRAME_TO_TOPIC)
    print("***********************************************************************************************")
    frame_to_KL = doc_level_divergence(all_data, frame_to_lex, FRAME_TO_TOPIC)


if __name__ == "__main__":
    main()
