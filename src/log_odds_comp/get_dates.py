import sys
sys.path.append("..")
from econ_utils import load_percent_change
from datetime import timedelta, date
from collections import defaultdict

def get_hardcoded_dates():

    BAD_DATES = [
        # "Great Recession"
        date(2008, 7, 1),
        date(2008, 8, 1),
        date(2008, 9, 1),
        date(2008, 10, 1),
        date(2008, 11, 1),
        date(2008, 12, 1),
        date(2009, 1, 1),
        # "Russian financial crisis"
        date(2014, 7, 1),
        date(2014, 8, 1),
        date(2014, 9, 1),
        date(2014, 10, 1),
        date(2014, 11, 1),
        date(2014, 12, 1),
        date(2015, 1, 1),

        date(2015, 5, 1),
        date(2015, 6, 1),
        date(2015, 7, 1),
        date(2015, 8, 1),
        date(2015, 9, 1)
        ]

    GOOD_DATES = [
        # Lots of growth from 2002 - 2008, selection of months
        # with most RTSI growth
        date(2003, 4, 1),
        date(2003, 5, 1),
        date(2003, 8, 1),
        date(2004, 3, 1),
        date(2005, 9, 1),
        date(2006, 1, 1),
        date(2006, 4, 1),
        date(2006, 11, 1),
        date(2008, 5, 1),

        # Recovery after crisis ("strong recovery"
        date(2009, 9, 1),
        date(2009, 10, 1),
        date(2009, 11, 1),
        date(2009, 12, 1),
        date(2010, 1, 1),
        date(2010, 2, 1),
        date(2010, 3, 1),
        date(2010, 4, 1)
        ]
    return GOOD_DATES, BAD_DATES

def get_month_just_after(percent_change_file):
    econ_seq = load_percent_change(percent_change_file)
    sorted_econ = sorted(econ_seq, key=econ_seq.get)

    # take top 10% as good months and bottom 10% as bad months
    num = int(len(econ_seq) / 6)
    prev_bad = sorted_econ[:num]
    prev_good = sorted_econ[-num:]

    def plus_month(seq):
        next_month = timedelta(days=31)
        new_seq = []
        for x in seq:
            new_date = x + next_month
            floored_date = date(new_date.year, new_date.month, 1)
            new_seq.append(floored_date)
        return new_seq

    return plus_month(prev_good), plus_month(prev_bad)

def get_same_month(percent_change_file):
    econ_seq = load_percent_change(percent_change_file)
    sorted_econ = sorted(econ_seq, key=econ_seq.get)

    # take top 10% as good months and bottom 10% as bad months
    num = int(len(econ_seq) / 6)
    prev_bad = sorted_econ[:num]
    prev_good = sorted_econ[-num:]

    return prev_good, prev_bad

# We think news coverage changes in downturn
# we should be looking at month before downturn and
# month after downturn. What changed?
# We could even do this one month at a time instead
# of aggergating, since topics should be pretty similar
# month to month
def get_month_prev(percent_change_file):
    econ_seq = load_percent_change(percent_change_file)
    sorted_econ = sorted(econ_seq, key=econ_seq.get)

    # take top 10% as good months and bottom 10% as bad months
    num = int(len(econ_seq) / 6)
    prev_bad = sorted_econ[:num]

    def plus_month(seq):
        next_month = timedelta(days=31)
        new_seq = []
        for x in seq:
            new_date = x + next_month
            floored_date = date(new_date.year, new_date.month, 1)
            new_seq.append(floored_date)
        return new_seq

    # take month of downturn as "good" and next month as "bad"
    return prev_bad, plus_month(prev_bad)


def get_good_month_prev(percent_change_file):
    econ_seq = load_percent_change(percent_change_file)
    sorted_econ = sorted(econ_seq, key=econ_seq.get)

    # take top 10% as bad months and following 10% as good months
    num = int(len(econ_seq) / 6)
    prev_good = sorted_econ[-num:]

    def plus_month(seq):
        next_month = timedelta(days=31)
        new_seq = []
        for x in seq:
            new_date = x + next_month
            floored_date = date(new_date.year, new_date.month, 1)
            new_seq.append(floored_date)
        return new_seq

    # take month of upturn as "bad" and next month as "good"
    return plus_month(prev_good), prev_good

# Take 15% of months, only let there be at most 2 files per year
# in each set
def get_month_after_limited(percent_change_file):
    econ_seq = load_percent_change(percent_change_file)
    sorted_econ = sorted(econ_seq, key=econ_seq.get)

    for x in sorted_econ:
        print (x, econ_seq[x])

    # take top 10% as good months and bottom 10% as bad months
    num = int(len(econ_seq) / 6)
    prev_bad = sorted_econ[:num]
    prev_good = sorted_econ[-num:]
    prev_good = reversed(prev_good)

    def plus_month(seq):
        next_month = timedelta(days=31)
        new_seq = []
        year_to_count = defaultdict(int)
        for x in seq:
            if year_to_count[x.year] >= 2:
                continue
            year_to_count[x.year] += 1
            new_date = x + next_month
            floored_date = date(new_date.year, new_date.month, 1)
            new_seq.append(floored_date)
        return new_seq

    return plus_month(prev_good), plus_month(prev_bad)

if __name__ == "__main__":
    test = "/usr1/home/anjalief/corpora/russian/percent_change/russian_rtsi_usd.csv"
    good,bad = get_month_after_limited(test)
    print (len(good), len(bad))
    for d in good:
        print (d)
    print ("**************************************")
    for d in bad:
        print (d)
