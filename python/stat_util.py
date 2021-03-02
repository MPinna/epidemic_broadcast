#!/usr/bin/env python

import scipy.stats as st
import fetcher as fe
import scipy.optimize as op
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.cm as cm
import itertools
import math
import sys
import io

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
        plt.errorbar(x=np.arange(0.1, 1, 0.1), y=np.array(y), yerr=err, capsize=3, linestyle="solid",
              marker='s', markersize=3, mfc="black", mec="black")

        popt, _ = op.curve_fit(iperbole, np.arange(0.1, 1, 0.1), np.array(y))
        x_line = np.arange(0.1, 1, 0.1)
        a,b = popt
        # calculate the output for the range
        y_line = iperbole(x_line,  a,b)
        plt.plot(x_line, y_line, '--')
        with open(file, "a") as f:
            f.write('R'+str(j)+' '+str(a)+" "+str(b)+" "+str(iperbole(1, a, b))+"\n")
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

#print_iperbole_parameters()
#print_sec_parameters()
#exit()


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

