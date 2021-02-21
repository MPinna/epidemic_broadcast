#!/usr/bin/env python

import scipy.stats as st
import scipy.optimize as op
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import math
import sys
import io

path="results/big_csv"

# return the mesurements of the number of collisions
def read_collisions(file):
    df = pd.read_csv(file, dtype={"name":"string", "count":int})
    collisionsDF = df[df['name'] == 'packetDropIncorrectlyReceived:count']
    collisionsDF = collisionsDF[['run', 'module', 'name', 'value']]
    collisionsDF = collisionsDF.groupby(["run", "module"], as_index = False)["value"].first()
    collisionsDF = collisionsDF.groupby(["run"], as_index = False)["value"].sum()
    collisions=np.array(collisionsDF['value'])
    return collisions

# return the mesurements of the number of users covered at the end of the simulation
def read_final_coverage(file):  
    df = pd.read_csv(file, dtype={"name":"string", "count":int})
    collisionsDF = df[df['name'] == 'packetDropIncorrectlyReceived:count']
    collisionsDF = collisionsDF[['run', 'module', 'name', 'value']]
    collisionsDF = collisionsDF.groupby(["run", "module"], as_index = False)["value"].first()
    usersDF = collisionsDF.groupby(["module"], as_index = False)["value"].first()
    collisionsDF = collisionsDF.groupby(["run"], as_index = False)["value"].sum()
    coverageDF = df[df['name'] == 'timeCoverageStat:vector']
    coverageDF = coverageDF[['run', 'module', 'name', 'value', 'vectime', 'vecvalue']]
    vecvalueDF = coverageDF.groupby(["run"], as_index = False)["vecvalue"].first()
    users = len(usersDF.index)
    totalCoverage = []
    for i in range(len(vecvalueDF.index)):
        coverageList = list(map(int, vecvalueDF["vecvalue"][i].split()))
        coverage = len(coverageList)
        totalCoverage.append(coverage/float(users))
    return totalCoverage

# return the mesurements of the duration (in slots) of the simulation
def read_duration(file):
    df = pd.read_csv(file, dtype={"name":"string", "count":int})
    coverageDF = df[df['name'] == 'timeCoverageStat:vector']
    coverageDF = coverageDF[['run', 'module', 'name', 'value', 'vectime', 'vecvalue']]
    vecvalueDF = coverageDF.groupby(["run"], as_index = False)["vecvalue"].first()
    totalCoverageSlot = []
    for i in range(len(vecvalueDF.index)):
        coverageList = list(map(int, vecvalueDF["vecvalue"][i].split()))
        totalCoverageSlot.append(coverageList[len(coverageList)-1])
    return totalCoverageSlot

# compute the samlpe mean and the mean error (simmetric) for a given confidence
def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), st.sem(a)
    h = se * st.t.ppf((1 + confidence) / 2., n-1)
    return m, h

# compute the samlpe median and the median range (asimmetric) for a given confidence 
def median_confidence_interval(array, confidence=0.95):
    median=np.median(array)
    n=len(array)
    ni=st.norm.ppf((1+confidence)/2)
    k=math.floor((n*0.5)-(ni*np.sqrt(n*0.5*0.1)))
    w=math.floor((n*0.5)+(ni*np.sqrt(n*0.5*0.1)))+1
    array=np.sort(array)
    min=array[k]
    max=array[w]
    return median, max, min

# drow 2 2D plots with different corves representing the behaveour in funciotn of 2 differents parameters
# set asim=True if confidence intervals are asimmetric
def x_y_plots(ylabel, serie, errors, asim=False, confidence=0.95, title="", p_log=False):
    plt.figure(1)
    for j in range(1, 10):
        plt.errorbar(x=np.arange(1,20), y=serie[j-1], yerr=errors[j-1], capsize=3, linestyle="solid",
               marker='s', markersize=3, mfc="black", mec="black", label=str(j/10))
    if "%" in ylabel:
        plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
    plt.legend(title="Values of P")
    plt.xlabel("Transmission Range (m)")
    plt.xticks(np.arange(1,20))
    plt.ylabel(ylabel)
    plt.title(title+" confidence= "+str(confidence*100)+"%")
    plt.figure(2)
    plt.title(title+" confidence= "+str(confidence*100)+"%")
    for i in range(1, 20):
        if asim:
            err=np.transpose(errors[:,:,i-1])
        else:
            err=errors[:,i-1]
        plt.errorbar(x=np.arange(0.1,1,0.1), y=np.array(serie[:,i-1]), yerr=err, capsize=3, linestyle="solid",
              marker='s', markersize=3, mfc="black", mec="black", label=str(i))
    plt.legend(title="Values of R (m)", loc='upper left', bbox_to_anchor=(1,1))
    plt.xlabel("Bernullian base (P)")
    plt.xticks(np.arange(0.1,1,0.1))
    if(p_log):
        plt.xscale("log")
    plt.ylabel(ylabel)
    if "%" in ylabel:
        plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))

# print pki plots fo a given confidence, with a given index of central tentencies (pki), with a gven number of samples n<=200
def print_PKI_plots(pki, ict="mean", confidence=0.9, n=200):
    if not pki in ["collisions", "duration (s)", "coverage (%)"] :
        return
    if not(ict in ["median", "mean"]):
        return
    if not(n>20 and n<201):
        return
    if not(confidence>0.7 and confidence<0.996):
        return
    serie=[]
    errors=[]
    for j in range(1, 10, 1):
        serie.append([])
        errors.append([])
        if(ict=="median"):
            errors[j-1].append([])
            errors[j-1].append([])
        for i in range(1, 20):
            if(pki=="collisions"):
                datas= read_collisions(path+'/big-p'+str(j/10)+'R'+str(i)+'.csv')
            if(pki=="duration (s)"):
                datas= read_duration(path+'/big-p'+str(j/10)+'R'+str(i)+'.csv')
            if(pki=="coverage (%)"):
                datas= read_final_coverage(path+'/big-p'+str(j/10)+'R'+str(i)+'.csv')
            if(ict=="median"):
                cent, max, min=median_confidence_interval(datas[:n], confidence)
                errors[j-1][0].append(cent-min)
                errors[j-1][1].append(max-cent)
            else:
                cent, err=mean_confidence_interval(datas[:n], confidence)
                errors[j-1].append(err)
            serie[j-1].append(cent)
        print("status:"+str(j)+"/"+str(10) )
    serie=np.array(serie)
    errors=np.array(errors)
    if(ict=="median"):
        x_y_plots(pki, serie, errors, True, confidence=confidence, title="median values")
    else:
        x_y_plots(pki, serie, errors,confidence=confidence, title="mean values")
    plt.show()

def print_coverage_drop(ict="mean", confidence=0.9):
    if not(ict in ["median", "mean"]):
        return
    if not(confidence>0.7 and confidence<0.996):
        return
    print("R: max(p=0.1) min(p=0.9) drop(%)\n")
    for j in range(1, 20):
        for i in range(1, 10,8):
            datas= read_final_coverage(path+'/big-p'+str(i/10)+'R'+str(j)+'.csv')
            if(ict=="median"):
                cent, max, min=median_confidence_interval(datas, confidence)
            else:
                cent, err=mean_confidence_interval(datas, confidence)
            if i==1:
                prec=cent
            else:
                print(str(j)+": "+str(prec)+" "+str(cent)+" "+str((cent-prec)*100/prec)+"%")

# drow an ECDF
def makeECDF(array, num_bins=20):
    counts, bin_edges = np.histogram(array, bins=num_bins, normed=True)
    cdf = np.cumsum(counts)
    plt.plot(bin_edges[1:], cdf)

#drow a lotrenz curve
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

# print ECDFs of a giver pki
def print_ECFDs(pki,R_range, p_range, bins ):
    for j in p_range:
        for i in R_range:
            if(pki=="collisions"):
                datas= read_collisions(path+'/big-p'+str(j/10)+'R'+str(i)+'.csv')
            if(pki=="duration (s)"):
                datas= read_duration(path+'/big-p'+str(j/10)+'R'+str(i)+'.csv')
            if(pki=="coverage (%)"):
                datas= read_final_coverage(path+'/big-p'+str(j/10)+'R'+str(i)+'.csv')
            plt.figure(i)
            makeECDF(datas, bins)
        print("status:"+str(j)+"/"+str(10) )
    plt.show()

# print standard devation of a given pki in funcion of the number of samples
def print_STDs(pki,R_range=np.arange(1, 20), p_range=np.arange(1, 10) ):
    for j in p_range:
        plt.figure(j)
        for i in R_range:
            if(pki=="collisions"):
                datas= read_collisions(path+'/big-p'+str(j/10)+'R'+str(i)+'.csv')
            if(pki=="duration (s)"):
                datas= read_duration(path+'/big-p'+str(j/10)+'R'+str(i)+'.csv')
            if(pki=="coverage (%)"):
                datas= read_final_coverage(path+'/big-p'+str(j/10)+'R'+str(i)+'.csv')
            stds=[]
            for h in range(19, 200, 20):
               stds.append(np.std(datas[:h]))
            plt.plot(np.arange(10,200,20), stds)
        print("status:"+str(j)+"/"+str(10) )
    plt.show()

def plot_fit(x, target, objective):
    popt, _ = op.curve_fit(objective, x, target)
    # calculate the output for the range
    y = objective(x,  popt)
    plt.plot(x, y, '--')

# print an histogrm and a QQ plot for the given distribution
def dist_analisis(pki,r, p):
    data=[]
    if(pki=="collisions"):
        data= read_collisions(path+'/big-p'+str(p)+'R'+str(r)+'.csv')
    if(pki=="duration (s)"):
        data= read_duration(path+'/big-p'+str(p)+'R'+str(r)+'.csv')
    if(pki=="coverage (%)"):
        data= read_final_coverage(path+'/big-p'+str(p)+'R'+str(r)+'.csv')
    if(len(data)==0):
        return
    plt.figure(0)
    bins= plt.hist(x=data, bins="auto", color='#0504aa', alpha=0.7, rwidth=0.85)
    plt.grid(axis='y', alpha=0.75)
    plt.xlabel(pki)
    if "%" in pki:
        plt.gca().xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
    start=bins[1][0]
    pace=bins[1][1]-start
    start=(bins[1][1]+start)/2.
    plt.xticks(np.arange(start, 1,pace))
    plt.ylabel('Frequency')
    plt.title('p='+str(p)+' R='+str(r))
    plt.figure(1)
    st.probplot(data, dist="norm", plot=plt)
    plt.title('QQ plot: '+pki+' p='+str(p)+' R='+str(r)+' vs Normal')
    plt.show()

def print_sigmoid_parameters(file="sigmoid_parameters.txt"):
    def sigmoid(x, a,b):
        return (1+np.tanh((a*x)-b))/2.
    for j in range(1, 10):
        y=[]
        errs=[]
        for i in range(1, 20):
            datas= read_final_coverage(path+'/big-p'+str(j/10)+'R'+str(i)+'.csv')
            mean, err=mean_confidence_interval(datas)
            y.append(mean)
            errs.append(err)
        plt.figure(j)
        plt.errorbar(x=np.arange(1,20), y=np.array(y), yerr=err, capsize=3, linestyle="solid",
              marker='s', markersize=3, mfc="black", mec="black")

        popt, _ = op.curve_fit(sigmoid, np.arange(1,20), np.array(y))
        x_line = np.arange(1,20)
        a,b = popt
        # calculate the output for the range
        y_line = sigmoid(x_line,  a,b)
        plt.plot(x_line, y_line, '--')
        flex=(b-np.arctanh(1-(2*0.5)))/a
        with open(file, "a") as f:
            f.write('p'+str(j/10)+' '+str(a)+" "+str(b)+" flex: "+str(flex)+"\n")
    plt.show()
def print_iperbole_parameters(file="iperbole_parameters.txt"):
    def iperbole(x, a,b):
        return (a/x)+b
    for j in range(1, 20):
        y=[]
        errs=[]
        for i in range(1, 10):
            datas= read_duration(path+'/big-p'+str(i/10)+'R'+str(j)+'.csv')
            mean, err=mean_confidence_interval(datas)
            y.append(mean)
            errs.append(err)
        plt.figure(j)
        plt.errorbar(x=np.arange(1,10), y=np.array(y), yerr=err, capsize=3, linestyle="solid",
              marker='s', markersize=3, mfc="black", mec="black")

        popt, _ = op.curve_fit(iperbole, np.arange(1,10), np.array(y))
        x_line = np.arange(1,20)
        a,b = popt
        # calculate the output for the range
        y_line = iperbole(x_line,  a,b)
        plt.plot(x_line, y_line, '--')
        with open(file, "a") as f:
            f.write('R'+str(j)+' '+str(a)+" "+str(b)+"\n")
    plt.show()

def print_sec_parameters(file="sec_parameters.txt"):
    def sec(x, a,b, c): # this is the derivative of the sigmoid, scaled up by a factor c
        return (a*c)/(np.cosh((2*b)-(2*a*x))+1)
    for j in range(1, 10):
        y=[]
        errs=[]
        for i in range(1, 20):
            datas= read_duration(path+'/big-p'+str(j/10)+'R'+str(i)+'.csv')
            mean, err=mean_confidence_interval(datas)
            y.append(mean)
            errs.append(err)
        plt.figure(j)
        plt.errorbar(x=np.arange(1,20), y=np.array(y), yerr=err, capsize=3, linestyle="solid",
              marker='s', markersize=3, mfc="black", mec="black")

        popt, _ = op.curve_fit(sec, np.arange(1,20), np.array(y))
        x_line = np.arange(1,20)
        a,b,c= popt
        # calculate the output for the range
        y_line = sec(x_line, a,b,c)
        plt.plot(x_line, y_line, '--')
        #max=(b-np.arctanh(1-(2*0.5)))/a
        with open(file, "a") as f:
            f.write('p'+str(j/10)+' '+str(a)+" "+str(b)+" "+str(c)+"\n")
    plt.show()

#print_coverage_drop()
#print_sec_parameters()
#exit()
print("Usage:")
print("[duration (s) | coverage (%) | collisions] [ mean | median ] [confidence interval (def=0.99)]")
print(len(sys.argv))
if(len(sys.argv)==3):
    print_PKI_plots(str(sys.argv[1]), str(sys.argv[2]), 0.99)
if(len(sys.argv)==4):
    print_PKI_plots(sys.argv[1], sys.argv[2], float(sys.argv[3]))
exit()

#dist_analisis("collisions",11, 0.6)
#exit()
# objective function

	#return b*np.power(x,2)+c*x+d

#popt, _ = op.curve_fit(objective, np.arange(1,10,1), np.array(serie[:,i-1]))
#x_line = np.arange(1,10,1)
#b, c,d = popt
# calculate the output for the range
#y_line = objective(x_line,  b, c,d)
#plt.plot(x_line, y_line, '--')





# histograms
#bins= plt.hist(x=collisions, bins="auto", color='#0504aa',
                            #alpha=0.7, rwidth=0.85)
#plt.grid(axis='y', alpha=0.75)
#plt.xlabel('Value')
#plt.ylabel('Frequency')
#plt.title('My Very Own Histogram')
#plt.show()


# QQ plots
#st.probplot(collisions,dist=st.chi2(df=40) , plot=plt)
#plt.show()
#st.probplot(collisions,dist=st.erlang(a=44) , plot=plt)
#st.probplot(collisions,dist=st.poisson(mu=mean, loc=100) , plot=plt)
#st.probplot(collisions, fit=False,dist=st.norm(loc=mean, scale=np.std(collisions)) , plot=plt)

