#!/usr/bin/env python

import scipy.stats
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
def analyze_file(file):
    df = pd.read_csv(file)
    collisionsDF = df[df['name'] == 'packetDropIncorrectlyReceived:count']
    collisionsDF = collisionsDF[['run', 'module', 'name', 'value']]
    collisionsDF = collisionsDF.groupby(["run", "module"], as_index = False)["value"].first()
    usersDF = collisionsDF.groupby(["module"], as_index = False)["value"].first()
    users = len(usersDF.index)
    collisionsDF = collisionsDF.groupby(["run"], as_index = False)["value"].sum()
    collisions=np.array(collisionsDF['value'])
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
    return users, repetitions, collisions, totalCoverage, totalCoverageSlot
def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, h

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

# autocorrelation plot
def show_correlogram(mesurements):
    pd.plotting.autocorrelation_plot(mesurements)
    plt.show()

plt.figure(1)
serie=[]
errors=[]
for j in range(1, 10, 1):
    serie.append([])
    errors.append([])
    for i in range(6, 20):
        users, repetitions, collisions, coverage, time= analyze_file('csv/big-p'+str(j/10)+'R'+str(i)+'.csv')
        mean, err=mean_confidence_interval(collisions)
        serie[j-1].append(mean)
        errors[j-1].append(err)
        #plt.figure(2)
        #plt.scatter(x=np.arange(i,i+0.5,0.5/len(collisions)), y=collisions)
    plt.errorbar(x=np.arange(6,20,1), y=serie[j-1], yerr=errors[j-1], capsize=3, linestyle="solid",
              marker='s', markersize=3, mfc="black", mec="black", label=str(j))
plt.figure(2)
serie=np.array(serie)
errors=np.array(errors)
for i in range(6, 20):
    plt.errorbar(x=np.arange(1,10,1), y=np.array(serie[:,i-6]), yerr=errors[:,i-6], capsize=3, linestyle="solid",
              marker='s', markersize=3, mfc="black", mec="black", label=str(i))
plt.show()
# scatterplot example



# showing confidence inetrvals
plt.show()

# histograms
bins= plt.hist(x=collisions, bins="auto", color='#0504aa',
                            alpha=0.7, rwidth=0.85)
plt.grid(axis='y', alpha=0.75)
plt.xlabel('Value')
plt.ylabel('Frequency')
plt.title('My Very Own Histogram')
plt.show()

#lorenz curve
lorenz_curve(collisions)
plt.show()

# QQ plots
scipy.stats.probplot(collisions,dist=scipy.stats.chi2(df=40) , plot=plt)
plt.show()
scipy.stats.probplot(collisions,dist=scipy.stats.erlang(a=44) , plot=plt)
scipy.stats.probplot(collisions,dist=scipy.stats.poisson(mu=mean, loc=100) , plot=plt)
scipy.stats.probplot(collisions, fit=False,dist=scipy.stats.norm(loc=mean, scale=np.std(collisions)) , plot=plt)


print("REPETITIONS: " + str(repetitions))
print("USERS: " + str(users) + "\n")
print("COLLISIONS MEAN:")
print(mean)
print("+-"+str(err))
