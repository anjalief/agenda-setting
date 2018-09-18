from statsmodels.tsa.stattools import grangercausalitytests
import numpy
import sys
import argparse
import pandas

def get_percent_change(series1):
    new_series = []
    for i in range(1, len(series1)):
        new_series.append((float(series1.iloc[i]) / float(series1.iloc[i-1])) - 1)
    return new_series

def do_test(series1, series2):
#    print (len(series1), series2.shape)
    usa_freq = numpy.array(series1)
    rtsi = numpy.array(series2)
#    print (usa_freq.shape, rtsi.shape)
    input = numpy.stack((usa_freq, rtsi), 1)


    return grangercausalitytests(input, maxlag=4)

def main():
    parser  = argparse.ArgumentParser()
    parser.add_argument("--seq1")
    parser.add_argument("--seq2")
    args = parser.parse_args()


    seq1 = [float(x) for x in open(args.seq1).readlines()]
    seq2 = [float(x) for x in open(args.seq2).readlines()]
    res = do_test(seq1, seq2)
    for lag in res:
        print (lag)
        print (res[lag][1][1].params)
        print (res[lag][1][1].pvalues)
        print("*********************************************")


def new_main():
    import pandas
    pmi = pandas.read_csv("./monthly_pmi.csv")
    econ = pandas.read_csv("./monthly_rtsi.txt")
    skip = 1
    for column in pmi:
        if skip:
            skip -= 1
            continue

        print(column)
        print(do_test(get_percent_change(pmi[column][1:]), econ.iloc[:,0]))
        break

if __name__ == "__main__":
    main()
