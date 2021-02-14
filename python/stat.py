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
def lorenz_curve(X):
    X_lorenz = X.cumsum() / X.sum()
    X_lorenz = np.insert(X_lorenz, 0, 0) 
    X_lorenz[0], X_lorenz[-1]
    fig, ax = plt.subplots(figsize=[6,6])
    ## scatter plot of Lorenz curve
    ax.scatter(np.arange(X_lorenz.size)/(X_lorenz.size-1), X_lorenz, 
               marker='.', color='darkgreen', s=100)
    ## line plot of equality
    ax.plot([0,1], [0,1], color='k')
df = pd.read_csv('results-500.csv')

# average number of collisions
collisionsDF = df[df['name'] == 'packetDropIncorrectlyReceived:count']
collisionsDF = collisionsDF[['run', 'module', 'name', 'value']]
collisionsDF = collisionsDF.groupby(["run", "module"], as_index = False)["value"].first()
usersDF = collisionsDF.groupby(["module"], as_index = False)["value"].first()
users = len(usersDF.index)
collisionsDF = collisionsDF.groupby(["run"], as_index = False)["value"].sum()
a, b, c = mean_confidence_interval(collisionsDF['value'])

mes=np.array(collisionsDF['value'])
print(np.std(mes))
bins= plt.hist(x=mes, bins="auto", color='#0504aa',
                            alpha=0.7, rwidth=0.85)
plt.grid(axis='y', alpha=0.75)
plt.xlabel('Value')
plt.ylabel('Frequency')
plt.title('My Very Own Histogram')
plt.show()
#lorenz_curve(np.array(collisionsDF['value']))
#plt.show()
#scipy.stats.probplot(np.array(collisionsDF['value']),dist=scipy.stats.chi2(df=40) , plot=plt)
#scipy.stats.probplot(np.array(collisionsDF['value']),dist=scipy.stats.erlang(a=44) , plot=plt)
#scipy.stats.probplot(np.array(collisionsDF['value']),dist=scipy.stats.poisson(mu=a, loc=100) , plot=plt)
#mes=np.array(collisionsDF['value'])
#scipy.stats.probplot(mes, fit=False,dist=scipy.stats.norm(loc=a, scale=np.std(mes)) , plot=plt)


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
#mes=np.array(totalCoverage)
#scipy.stats.probplot(mes,dist= , plot=plt)
#plt.show()
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
