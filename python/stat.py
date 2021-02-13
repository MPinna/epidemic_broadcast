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

df = pd.read_csv('results-500.csv')

# average number of collisions
collisionsDF = df[df['name'] == 'packetDropIncorrectlyReceived:count']
collisionsDF = collisionsDF[['run', 'module', 'name', 'value']]
collisionsDF = collisionsDF.groupby(["run", "module"], as_index = False)["value"].first()
usersDF = collisionsDF.groupby(["module"], as_index = False)["value"].first()
users = len(usersDF.index)
collisionsDF = collisionsDF.groupby(["run"], as_index = False)["value"].sum()
a, b, c = mean_confidence_interval(collisionsDF['value'])

# percentage of covered users
coverageDF = df[df['name'] == 'timeCoverageStat:vector']
coverageDF = coverageDF[['run', 'module', 'name', 'value', 'vectime', 'vecvalue']]
vectimeDF = coverageDF.groupby(["run"], as_index = False)["vectime"].first()
repetitions = len(vectimeDF.index)
vecvalueDF = coverageDF.groupby(["run"], as_index = False)["vecvalue"].first()
totalCoverage = []
totalCoverageSlot = []
for i in range(len(vecvalueDF.index)):
    coverageList = list(map(int, vecvalueDF["vecvalue"][i].split()))
    coverage = len(coverageList)
    totalCoverage.append(coverage/float(users))
    totalCoverageSlot.append(coverageList[len(coverageList)-1])

d, e, f = mean_confidence_interval(totalCoverage)
g, h, i = mean_confidence_interval(totalCoverageSlot)

print("REPETITIONS: " + str(repetitions))
print("USERS: " + str(users) + "\n")
print("COLLISIONS MEAN:")
print(a)
print(b)
print(c)
print("\nCOVERAGE MEAN:")
print(d)
print(e)
print(f)
print("\nTOTAL BROADCAST TIME:")
print(g)
print(h)
print(i)
