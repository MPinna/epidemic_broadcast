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
import stat_util as su
import validationPlots as valPL
import pandas as pd
import numpy as np

from collections import Counter

BASEFILENAME = "5to1csv/star5to1_validation-p=0."
NUMOFBATCHES = 10
NUMOFREPS = 1000
NUMOFSLOTS = 10
CONFIDENCE = 0.95


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
for p in configurations:
    for i in range(NUMOFREPS):

        repetition = configurations[p][i]

        cumulativeVector = getCumulativeSleep(repetition)
        configCumulatives[p].append(cumulativeVector)

sleepDataFrameSet = {}

for p in configurations:
    sleepDataframe = pd.DataFrame(configCumulatives[p], columns=range(0, NUMOFSLOTS))
    sleepDataFrameSet[p] = sleepDataframe


#
    # each element of theoreticalProbs is like:
    #                0   1   2   3   4   5   6   7   8   9
    # key: 0, value: P00 P01 P02 P03 P04 P05 P06 P07 P08 P09
    # key: 2, value: P20 P21 P22 P23 P24 P25 P26 P27 P28 P29
    # key: 3, value: P30 P31 P32 P33 P34 P35 P36 P37 P38 P39
    # key: 4, value: P40 P41 P42 P43 P44 P45 P46 P47 P48 P49
    # key: S, value: PS0 PS1 PS2 PS3 PS4 PS5 PS6 PS7 PS8 PS9
    # key: 5, value: P50 P51 P52 P53 P54 P55 P56 P57 P58 P59
    #
    # where Pij is the theoretical prob of the system being in
    # state i at slot j

    # each element of experimentalProbs is like:
    #                0   1   2   3   4   5   6   7   8   9
    # key: 0, value: T00 T01 T02 T03 T04 T05 T06 T07 T08 T09
    # key: 2, value: T20 T21 T22 T23 T24 T25 T26 T27 T28 T29
    # key: 3, value: T30 T31 T32 T33 T34 T35 T36 T37 T38 T39
    # key: 4, value: T40 T41 T42 T43 T44 T45 T46 T47 T48 T49
    # key: S, value: TS0 TS1 TS2 TS3 TS4 TS5 TS6 TS7 TS8 TS9
    # key: 5, value: T50 T51 T52 T53 T54 T55 T56 T57 T58 T59
    #
    # where Tij is a tuple with experimental prob of the system
    # being in state i at slot j, along with relative error


theoreticalProbs = {}
experimentalProbs = {}

for p in configurations:
    theoreticalProbs[p] = {}
    experimentalProbs[p] = {}
    for state in STATES:
        theoreticalProbs[p][state] = [0] * NUMOFSLOTS
        experimentalProbs[p][state] = [0] * NUMOFSLOTS


# populate theoreticalProbs. Each row corresponds to a state.
# The i-th element of j-th row is the theoretical probability 
# of the system being in state j during the i-th slots
for index, pKey in enumerate(configurations):

    # get value of p from iteration index
    p = round((0.2*index + 0.2) ,1)
    M = np.array(getMarkovMatrix(5, p))
    for i in range(NUMOFSLOTS):
        probs = np.linalg.matrix_power(M, i)[0] # row 0 because the initial state is always 0

        # the i-th 'probs' row obtained is the i-th column
        # of the theoretical probs
        for j in range(len(probs)):
            theoreticalProbs[pKey][STATES[j]][i] = probs[j]

print("------THEORETICAL PROBABILITIES------")
for p in theoreticalProbs:
    print(p)
    for state in theoreticalProbs[p]:
        print(str(state) + ":\t", end="")
        for slot in range(NUMOFSLOTS):
            prob = round(theoreticalProbs[p][state][slot], 3)

            print(str(prob) +  "\t", end="")
        print()

# populate experimentalProbs. Each row corresponds to a state.
# The i-th element of j-th row is a tuple with the mean 
# experimental probability and the error
for p in configurations:
    for slot in range(0,NUMOFSLOTS):
        slotData = sleepDataFrameSet[p][slot]
        stateCount = slotData.value_counts().to_dict()
        for state in STATES:
            data = [0]*NUMOFREPS
            if(state in stateCount):
                occurrences = stateCount[state]
                data[0:occurrences - 1] = [1]*occurrences

            stateMeanCI = su.mean_confidence_interval(data, CONFIDENCE)

            # append tuple <mean value, mean error> to
            # corresponding experimentalProbs array
            experimentalProbs[p][state][slot] = stateMeanCI


for index, p in enumerate(experimentalProbs):
    figTitle = "p = " + str(round((0.2*index + 0.2) ,1))
    valPL.star5to1ValidationPlot("probability", experimentalProbs[p], theoreticalProbs[p], NUMOFSLOTS, STATES, index, title=figTitle, confidence=CONFIDENCE)