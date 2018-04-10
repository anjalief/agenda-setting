#!/usr/bin/env python3

import os
import numpy

# have to load these manually because the file names don't sort correctly
YEARS = ["2003", "2004", "2005", "2006", "2007", "2008", "2009",
         "2010", "2011", "2012", "2013", "2014", "2015", "2016"]
MONTHS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
# YEARS = ["2003"]
# MONTHS = ["1", "2", "3", "4"]

def get_model_filename(path, year, month):
    return os.path.join(path, year + "_" + month + ".pickle")


# this is bad, but for now if there are multiple words in the file, we are just
# going to take the first one
def load_file(name):
    lines = open(name).readlines()
    lines = [l.split()[0] for l in lines]
    return lines

def get_corr(x, y):
    # this returns a matrix where 0,1 is the correlation between seq 0 and seq 1 (I think)
    # since we're only going to give in 1D lists, we can grab the top right element
    return numpy.corrcoef(x, y)[0, 1]

