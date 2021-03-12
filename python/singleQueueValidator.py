from numpy.lib.index_tricks import _fill_diagonal_dispatcher
import scipy.stats as st
import scipy.special
import scipy.optimize as op
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import fetcher as fe

NUMOFHOPS = 10

def getFilename(p):
    filename = "singleQueue\singleQueue_validation-p=" + str(p) + ".csv"
    return filename


def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, m-h, m+h

pValues = np.arange(0.1, 1.0, 0.1)

for p in pValues:
    p = round(p, 1)
    expectedTime = (1/p)*10 + 1
    filename = getFilename(p)
    durationData = fe.read_duration(filename)
    MCF = mean_confidence_interval(durationData)

    print("p = " + str(p))
    print("Expected time:\t" + str(round(expectedTime, 4)))

    print("Experimental result (mean, <confidence range>):")
    print(mean_confidence_interval(durationData))
    print("Relative error:")
    error = (abs(expectedTime - mean_confidence_interval(durationData)[0]))/expectedTime
    print(str(round(error*100, 2)))