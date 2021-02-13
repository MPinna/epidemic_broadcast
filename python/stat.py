#!/usr/bin/env python

import scipy.stats
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, m-h, m+h

df = pd.read_csv('results.csv')

# number of collisions
collisionsDF = df[df['name'] == 'packetDropIncorrectlyReceived:count']
collisionsDF = collisionsDF[['run', 'module', 'name', 'value']]
collisionsDF = collisionsDF.groupby(["run", "module"], as_index = False)["value"].first()
collisionsDF = collisionsDF.groupby(["run"], as_index = False)["value"].sum()
print("COLLISIONS MEAN: " + str(collisionsDF['value'].mean()) + "\n")
m, l, u = mean_confidence_interval(collisionsDF['value'])
print(m)
print(l)
print(u)

# percentage of covered users
coverageDF = df[df['name'] == 'timeCoverageStat:vector']
coverageDF = coverageDF[['run', 'module', 'name', 'value', 'vectime', 'vecvalue']]
vectimeDF = coverageDF.groupby(["run"], as_index = False)["vectime"].first()
vecvalueDF = coverageDF.groupby(["run"], as_index = False)["vecvalue"].first()
totalCoverage = 0
for i in range(len(vecvalueDF.index)):
    coverageList = list(map(int, vecvalueDF["vecvalue"][i].split()))
    coverage = len(coverageList)
    totalCoverage += coverage/100
    plt.plot(coverageList)
    plt.show()
print("\nCOVERAGE MEAN: " + str(totalCoverage/len(vecvalueDF.index)))
