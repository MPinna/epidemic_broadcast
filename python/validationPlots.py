
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
import os

figpath="fig/"
title="star5to1"

cmap=cm.get_cmap("rainbow")

def replacefig(fig):
    if(os.path.isfile(figpath+fig)):
        os.remove(figpath+fig)
    plt.savefig(figpath+fig)


# Plot experimental probabilities as function of slot number, for each possible state
# X axis: slot number
#   One line per state
#
# Dashed lines represent theoretical predictions.
def star5to1ValidationPlot(yLabel, data, prediction, numOfSlots, states, figIndex, title, asim=False, confidence=0.95):
    plt.figure(figIndex)
    plt.title(title + " (" + str(int(confidence*100)) + "% CI)")
    plt.xlabel("Slot number")
    plt.ylabel(yLabel)
    plt.xticks(range(numOfSlots))
    state_colors=cmap(np.linspace(0, 1 ,len(states)))

    # insert experimental data
    for index, state in enumerate(states):
        expSeries = [x[0] for x in data[state]]
        expErrors = [x[1] for x in data[state]]
        plt.errorbar(x=range(0, numOfSlots), y=expSeries, yerr=expErrors, capsize=3, linestyle="solid", marker='s', markersize=3, mfc="black", mec="black", label=str(state),color=state_colors[index])
    plt.legend(title = "States", bbox_to_anchor=(1, 1), loc='upper left', borderaxespad=0.2)

    for index, state in enumerate(states):
        theoreticalSeries = (prediction[state])[0:numOfSlots]
        plt.errorbar(x=range(0, numOfSlots), y=theoreticalSeries, linestyle="--", color="black", linewidth=0.7)

    replacefig("star5to1" + title + "validation.pdf")