#!/usr/bin/env python

import scipy.stats as st
import scipy.optimize as op
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
def analyze_file(file):
    df = pd.read_csv(file, dtype={"name":"string", "count":int})
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
    m, se = np.mean(a), st.sem(a)
    h = se * st.t.ppf((1 + confidence) / 2., n-1)
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
def x_y_plots(ylabel, serie, errors):
    plt.figure(1)
    for j in range(1, 10):
        plt.errorbar(x=np.arange(1,20,1), y=serie[j-1], yerr=errors[j-1], capsize=3, linestyle="solid",
               marker='s', markersize=3, mfc="black", mec="black", label=str(j/10))
    if "%" in ylabel:
        plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
    plt.legend(title="Values of P")
    plt.xlabel("Transmission range (R)")
    plt.xticks(np.arange(1,20))
    plt.ylabel(ylabel)
    plt.figure(2)
    for i in range(1, 20):
        plt.errorbar(x=np.arange(0.1,1,0.1), y=np.array(serie[:,i-1]), yerr=errors[:,i-1], capsize=3, linestyle="solid",
              marker='s', markersize=3, mfc="black", mec="black", label=str(i))
    plt.legend(title="Values of R", loc='upper left', bbox_to_anchor=(1,1))
    plt.xlabel("Bernullian base (P)")
    plt.xticks(np.arange(0.1,1,0.1))
    plt.ylabel(ylabel)
    plt.ylabel("Duration (s)")
    if "%" in ylabel:
        plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
    plt.show()


serie=[]
errors=[]
for j in range(1, 10, 1):
    serie.append([])
    errors.append([])
    for i in range(1, 20):
        users, repetitions, collisions, coverage, time= analyze_file('big_csv/big-p'+str(j/10)+'R'+str(i)+'.csv')
        mean, err=mean_confidence_interval(time, 0.9)
        serie[j-1].append(mean)
        errors[j-1].append(err)
        #plt.figure(j+3)
        #plt.scatter(x=np.arange(i,i+0.5,0.5/len(time)), y=time)
plt.show()
serie=np.array(serie)
errors=np.array(errors)
#x_y_plots("Duration (s)", serie, errors)

# objective function
def objective(x,  b, c,d):
	return b*np.power(x,2)+c*x+d
    
    #popt, _ = op.curve_fit(objective, np.arange(1,10,1), np.array(serie[:,i-1]))
    #x_line = np.arange(1,10,1)
    #b, c,d = popt
    # calculate the output for the range
    #y_line = objective(x_line,  b, c,d)
    #plt.plot(x_line, y_line, '--')
# scatterplot example





# histograms
bins= plt.hist(x=collisions, bins="auto", color='#0504aa',
                            alpha=0.7, rwidth=0.85)
plt.grid(axis='y', alpha=0.75)
plt.xlabel('Value')
plt.ylabel('Frequency')
plt.title('My Very Own Histogram')
#plt.show()

#lorenz curve
lorenz_curve(collisions)
#plt.show()

# QQ plots
st.probplot(collisions,dist=st.chi2(df=40) , plot=plt)
#plt.show()
st.probplot(collisions,dist=st.erlang(a=44) , plot=plt)
st.probplot(collisions,dist=st.poisson(mu=mean, loc=100) , plot=plt)
st.probplot(collisions, fit=False,dist=st.norm(loc=mean, scale=np.std(collisions)) , plot=plt)


print("REPETITIONS: " + str(repetitions))
print("USERS: " + str(users) + "\n")
print("COLLISIONS MEAN:")
print(mean)
print("+-"+str(err))
