#!/usr/bin/env python

from inspect import currentframe
import math
from numpy.core.numeric import NaN
import scipy.stats as st
import scipy.special
import scipy.optimize as op
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import fetcher as fe

import pandas as pd
import numpy as np

from collections import Counter

BASEFILENAME = "5to1csv/star5to1_validation-p=0."
NUMOFBATCHES = 10
NUMOFREPS = 1000
NUMOFSLOTS = 10


# order of the states in the Markov stochastic matrix
STATES = [0, 2, 3, 4, 'S', 5]

# get a sort of "cumulative distribution vector" of
# the sleeping devices in a simulation
def getCumulativeSleep(repetition, numOfSlots = NUMOFSLOTS):
    sleepVector = repetition["vector"]
    stateSSlot = repetition["stateSSlot"]

    # the Counter structure optimizes counting the
    # number of occurrences of various element
    c = Counter(sleepVector)

    cumulSleep = [0]*numOfSlots
    runningSum = cumulSleep[0]

    # if state S has never been reached, the cumulative sleep
    # has to be computed up to the last slot in the vector
    if(math.isnan(stateSSlot)):
        # for every slot where some host went to sleep
        for i in range(1, numOfSlots):
            if i in c:
                runningSum += c[i]
            cumulSleep[i] = runningSum

    # otherwise the last slot to be considered is the one before
    # state S was reached (because the last host that went to sleep
    # was the one to transmit the broadcast to the target and made it
    # reach the state S, therefore the transition to consider in the DTMC
    # is the one to state S, not the one to state N+1)
    else:
        for i in range(1, numOfSlots):
            if i in c:
                runningSum += c[i]
            cumulSleep[i] = runningSum
        for i in range(int(stateSSlot), numOfSlots):
            cumulSleep[i] = ('S')

    # # if necessary pad the rest of the vector
    # # with the last state
    # if(math.isnan(stateSSlot)):
    #     for i in range(lastEmittedSlot, numOfSlots):
    #         cumulSleep.append(runningSum)
    # else:
    #     for i in range(lastEmittedSlot, numOfSlots):
    #         cumulSleep.append('S')
    
    return cumulSleep[0:numOfSlots]

def getTransitionProbability(i, j, N, p):
    """
    Returns the probability of the system with
    N hosts transitioning from  a state with
    i sleeping devices to a state with j
    sleeping devices
    """
    prob = scipy.special.comb(N - i, j - i)*(p**(j - i))*((1 - p)**(N - j))
    return round(prob, 4)

def getMarkovMatrix(N, prob):
    """
    Returns the stochastic matrix in triangular form,
    given the number of hosts and the probability prob
    """

    nStates = N + 1
    M = np.array([[0 for i in range(nStates)] for j in range(nStates)], dtype=float)
    

    # permutation matrix to reorder row and columns
    # to yield the Markov Matrix in triangular form
    P = np.array([[0 for i in range(nStates)] for j in range(nStates)])
    P[0][0] = 1
    P[nStates - 1][nStates - 1] = 1
    P[nStates - 2][1] = 1
    for j in range(1, nStates - 2):
        P[j][j+1] = 1
    
    # initialize M with probabilities
    for i in range(nStates):
        for j in range(i, nStates):
            M[i][j] = getTransitionProbability(i, j, N, prob)


    # correct probabilities FROM state S
    for j in range(nStates):
        M[1][j] = 1 if(j == 1) else 0


    # correct probabilities TO state S
    for j in range(2, nStates - 1):
        M[j][1] = getTransitionProbability(j, j + 1, N, prob)

    # permute rows
    M = np.matmul(P, M)

    # permute columns
    M = np.matmul(M, np.transpose(P))

    # correct probabilities for states that
    # differ by one (those transitions are already
    # taken care of by S)
    for i in range(1, nStates - 3):
        M[i][i+1] = 0
    M[nStates - 3][nStates - 1] = 0

    return M

M = getMarkovMatrix(5, 0.2)


# read all files and combine every batch of the same configuration
# into single dataframe. Then append the dataframe to the dataframes
# vector

configurations = {"p0.2": [],
                     "p0.4": [],
                     "p0.6": [],
                     "p0.8": []
                }

configCumulatives = {"p0.2": [],
                     "p0.4": [],
                     "p0.6": [],
                     "p0.8": []
                    }

# for each value of p, read every repetition
for i in range(2, 9, 2):
    configuration = []
    for batch in range(0, NUMOFBATCHES):
        filename = BASEFILENAME + str(i) + "_" + str(batch) + ".csv"
        configuration.extend(fe.read_sleeping_coverage(filename))
    configurations["p0." + str(i)] = configuration


# for each repetition create the cumulative sleep vector
for i in range(NUMOFREPS):

    repetition = configurations["p0.2"][i]

    cumulativeVector = getCumulativeSleep(repetition)
    configCumulatives["p0.2"].append(cumulativeVector)
    # print(i)
    # print(repetition)
    # print(cumulativeVector)
    # print()


sleepDataframe = pd.DataFrame(configCumulatives["p0.2"], columns=range(0, NUMOFSLOTS))


theoreticalProbs = {}
experimentalProbs = {}

for state in STATES:
    theoreticalProbs[state] = []
    experimentalProbs[state] = []

M = np.array(getMarkovMatrix(5, 0.2))


# populate theoreticalProbs. Each row corresponds to a state.
# The i-th element of j-th row is the theoretical probability 
# of the system being in state j during the i-th slots
for i in range(NUMOFSLOTS):
    probs = np.linalg.matrix_power(M, i)[0] # row 0 because the initial state is always 0

    for j, state in enumerate(STATES):
        theoreticalProbs[state].append(probs[j]) 


# populate experimentalProbs. Each row corresponds to a state.
# The i-th element of j-th row is the experimental probability 
# of the system being in state j during the i-th slots
for i in range(NUMOFSLOTS):
    probs = sleepDataframe[i].value_counts(normalize=True, sort=False).to_dict()

    for state in STATES:
        if(state in probs):
            experimentalProbs[state].append(probs[state])
        else:
            experimentalProbs[state].append(0)



for state in STATES:
    print(str(state) + ":\t", end="")
    for slot in range(NUMOFSLOTS):
        print(round(theoreticalProbs[state][slot], 4), end="\t")
    print()

print()

for state in STATES:
    print(str(state) + ":\t", end="")
    for slot in range(NUMOFSLOTS):
        print(round(experimentalProbs[state][slot], 4), end="\t")
    print()