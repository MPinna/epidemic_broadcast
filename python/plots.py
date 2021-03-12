
import stat_util as st
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

path="results/big_csv/"
figpath="fig/"
title="big"
cmap=cm.get_cmap("rainbow")
p_values=np.arange(0.1, 1., 0.1)
r_values=np.arange(1, 20, 1)
p_colors=cmap(np.linspace(0, 1 ,len(p_values)))
r_colors=cmap(np.linspace(0, 1, len(r_values)))

def replacefig(fig):
    if(os.path.isfile(figpath+fig)):
        os.remove(figpath+fig)
    plt.savefig(figpath+fig)

def get_file(p, r,l_path=path):
    return l_path+title+"-p"+str(round(p, 1))+'R'+str(round(r, 1))+'.csv'

    
# draw 2 2D plots with different curves representing the behaviour in function of 2 differents parameters
# set asim=True if confidence intervals are asimmetric
def x_y_plots(ylabel, serie, errors, asim=False, confidence=0.95, title="", p_log=False):
    plt.figure(1)
    for j in range(0,len(p_values)):
        plt.errorbar(x=np.arange(1,20), y=serie[j], yerr=errors[j], capsize=3, linestyle="solid",
               marker='s', markersize=3, mfc="black", mec="black", label=str(round(p_values[j],1)), color=p_colors[j])
    if "%" in ylabel:
        plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
    plt.legend(title="Values of P")
    plt.xlabel("Transmission Range (m)")
    plt.xticks(np.arange(1,20))
    plt.ylabel(ylabel)
    plt.title(title+" confidence= "+str(confidence*100)+"%")
    plt.figure(2)
    plt.title(title+" confidence= "+str(confidence*100)+"%")
    for i in range(0, len(r_values)):
        start=round(serie[0,i], 2)
        end=round(serie[len(p_values)-1,i],2)
        loss=round((start-end)*100/start, 2)
        print("R"+str(r_values[i])+": "+str(start)+" "+str(end)+" "+str(loss)+"%")
        if asim:
            err=np.transpose(errors[:,:,i])
        else:
            err=errors[:,i]
        plt.errorbar(x=p_values, y=np.array(serie[:,i]), yerr=err, capsize=3, linestyle="solid",
              marker='s', markersize=3, mfc="black", mec="black", label=str(r_values[i]),color=r_colors[i])
    plt.legend(title="Values of R (m)", loc='center left', bbox_to_anchor=(1,0.5))
    plt.subplots_adjust(right=0.8)
    plt.xlabel("Retransmission probability(P)")
    plt.xticks(p_values)
    if(p_log):
        plt.xscale("log")
    plt.ylabel(ylabel)
    if "%" in ylabel:
        plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))

# print pki plots for a given confidence, with a given index of central tendencies (pki), with a given number of samples n<=200
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
    for j in range(0, len(p_values)):
        serie.append([])
        errors.append([])
        if(ict=="median"):
            errors[j].append([])
            errors[j].append([])
        for i in range(0, len(r_values)):
            if(pki=="collisions"):
                datas=fe.read_collisions(get_file(p_values[j], r_values[i]))
            if(pki=="duration (s)"):
                datas= fe.read_duration(get_file(p_values[j], r_values[i]))
            if(pki=="coverage (%)"):
                datas= fe.read_final_coverage(get_file(p_values[j], r_values[i]))
            if(ict=="median"):
                cent, max, min=st.median_confidence_interval(datas[:n], confidence)
                errors[j][0].append(cent-min)
                errors[j][1].append(max-cent)
            else:
                cent, err=st.mean_confidence_interval(datas[:n], confidence)
                errors[j].append(err)
            serie[j].append(cent)
        print("status:"+str(j)+"/"+str(len(p_values)))
    serie=np.array(serie)
    errors=np.array(errors)
    if(ict=="median"):
        x_y_plots(pki, serie, errors, True, confidence=confidence, title="median values")
    else:
        x_y_plots(pki, serie, errors,confidence=confidence, title="mean values")
    plt.figure(1)
    replacefig(title+"_"+pki+"_r_"+ict+"_"+str(confidence*100)+".pdf")
    plt.figure(2)
    replacefig(title+"_"+pki+"_p_"+ict+"_"+str(confidence*100)+".pdf")

try:
    os.mkdir(figpath)
except:
    pass
if(len(sys.argv)==3):
    print_PKI_plots(str(sys.argv[1]), str(sys.argv[2]), 0.99)
    exit()
if(len(sys.argv)==4):
    print_PKI_plots(sys.argv[1], sys.argv[2], float(sys.argv[3]))
    exit()
print("Usage:")
print("[duration (s) | coverage (%) | collisions] [ mean | median ] [confidence interval (def=0.99)]")