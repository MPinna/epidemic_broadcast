import scipy.stats as st
import scipy.special
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

    print("Perm matrix:")
    for row in P:
        print(row)
    
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

# Stochastic Matrix for a scenario with 5 hosts
M = getMarkovMatrix(5, 0.9)

print("Markov Matrix:")
for row in M:
    for element in row:
        print(str(element) + "\t", end="")
    print()

print("20th power:")
M20 = np.linalg.matrix_power(M, 20)

for element in M20[0]:
    print(round(element, 4) , end="\t")