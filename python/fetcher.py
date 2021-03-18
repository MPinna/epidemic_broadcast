import pandas as pd
import numpy as np
from scipy.optimize.zeros import results_c
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

# return a list of couples containing the sleep coverage (vector) and the
# current slot number when the target host received the message (namely
# the slot where the system transitioned to state S)
def read_sleeping_coverage(file):  
    df = pd.read_csv(file, dtype={"name":"string", "count":int})
    stateS_DF = df[df['name'] == 'stateSTransitionStat:last']
    stateS_DF = stateS_DF[['run', 'name', 'value']]
    stateS_DF = stateS_DF.groupby(["run"], as_index = False)["value"].first()
    stateS_DF = list(stateS_DF['value'])
    # usersDF = stateSDF.groupby(["module"], as_index = False)["value"].first()
    # stateSDF = stateSDF.groupby(["run"], as_index = False)["value"].sum()
    sleepDF = df[df['name'] == 'sleepCoverageStat:vector']
    sleepDF = sleepDF[['run', 'name', 'value', 'vecvalue']]
    vecvalueDF = sleepDF.groupby(["run"], as_index = False)["vecvalue"].first()
    vecvalueDF = list(vecvalueDF['vecvalue'])

    iterations = len(vecvalueDF)
    result = []
    for i in range(iterations):
        couple = {}
        
        # all the slots where hosts went to sleep, similar to timeCoverageStat
        couple["vector"] = list(map(int, vecvalueDF[i].split()))

        # slot number where the system transitioned to state S
        # (NaN if the target was never reached by the broadcast)
        couple["stateSSlot"] = stateS_DF[i]
        result.append(couple)
    return result
