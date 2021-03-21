#!/usr/bin/env python

import math
import networkx as nx
from networkx.algorithms.distance_measures import eccentricity
from collections import Counter
import scipy.stats as st
import scipy.optimize as op
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import copy
import fetcher as fe
import stat_util as su
import os.path
import sys

NUM_OF_REPS = 200
NUM_OF_NODES = 100

R_MAX = 141
R_VALUES = range(1, R_MAX + 1)

RAWDATAFILENAME = "./big_csv/big-p0.1R1.csv"

REACH_DF_FILENAME = "DF_reach.csv"
ECCENTRICITY_DF_FILENAME = "DF_eccentricity.csv"
SAFENODES_DF_FILENAME = "DF_safeNodes.csv"
FIGPATH="fig/"

def read_host_coords_from_file(file):
    df = pd.read_csv(file, dtype={"name":"string", "count":int})
    df = df[df["type"] == "scalar"]


    # probably not the most pythonish or pandas-ish way
    # to retrieve data. Feel free to improve the function
    XcoordDF = df[df['name'] == 'hostXstat:last']
    YcoordDF = df[df['name'] == 'hostYstat:last']
    
    XcoordDF = XcoordDF[["run", "module", "value"]]
    XcoordDF = XcoordDF.groupby(["run"])["value"].apply(list)

    YcoordDF = YcoordDF[["run", "module", "value"]]
    YcoordDF = YcoordDF.groupby(["run"])["value"].apply(list)

    return XcoordDF, YcoordDF

def get_eccentricity(G: nx.Graph):
    connectComp = nx.node_connected_component(G, 0)
    S = G.subgraph(connectComp)
    e = nx.eccentricity(S, 0)
    return e


def get_connected_component_complement(G: nx.Graph, connComp):

    connectedNodesComplement = []

    for node in list(G.nodes):
        if node not in connComp:
            connectedNodesComplement.append(node)
    return connectedNodesComplement


def get_connected_component_graph(G: nx.Graph, connComp):

    # get nodes not reachable from node[0]
    notConnectedNodes = get_connected_component_complement(G, connComp)
    
    # create graph with only nodes reachable from zero
    H = copy.deepcopy(G)
    for node in notConnectedNodes:
        H.remove_node(node)

    return H

def get_surely_reached_nodes(H: nx.Graph):
    currentlyListening = list(H.nodes)
    currentlyTransmitting = [0]
    currentlyListening.remove(0)
    currentlySleeping = []

    reachedNodes = []

    # every iteration of the while is a slot
    while(True):
        activeInNextSlot = []
        collectiveNeighborhood = []
        for transmitting in currentlyTransmitting:

            reachedNodes.append(transmitting)

            # get neighbors from every transmitting node
            # but only those who are still listening
            neighborhood = H.neighbors(transmitting)

            neighborhood = list(set(neighborhood) & set(currentlyListening))
            # set of all currently reachable nodes, with repetitions.
            # If a node appears more than once, it means that it
            # would detect a collision in the next slot
            collectiveNeighborhood.extend(neighborhood)

            # collective neighborhood now contains listening nodes
            # that will receive the message on next slot or will detect a collision

        # count how many times a node appears in the neighborhood
        count = Counter(collectiveNeighborhood)

        for node in count:
            # if it appears just once, it won't detect a collision
            if(count[node] == 1):
                activeInNextSlot.append(node)

        # next slot arrives

        # who transmitted, goes to sleep
        currentlySleeping.extend(currentlyTransmitting)

        # who went to sleep is not listening any more
        currentlyListening = list(set(currentlyListening) - set(currentlySleeping))
 
        # who is now going to transmit is not listening any more too
        currentlyListening = list(set(currentlyListening) - set(activeInNextSlot))

        # who was reached is now transmitting
        currentlyTransmitting = activeInNextSlot
        reachedNodes = list(set(reachedNodes) | set(activeInNextSlot))

        if(len(currentlyListening) == 0 or len(currentlyTransmitting) == 0):
            break

    return reachedNodes


def draw_graph(G: nx.Graph):
    # take "pos" attribute from nodes in graph
    # and use it to create a dictionary to be
    # passed to the draw function to position
    # each nodes in the right spot
    pos = nx.get_node_attributes(G, 'pos')

    order = G.number_of_nodes()
    
    # node[0] is green, all the others are yellow
    nodeColorsMap = []
    for i in range(order):
        if(i == 0):
            nodeColorsMap.append("green")
        else:
            nodeColorsMap.append("yellow")

    nx.draw(G, pos=pos,
        with_labels = True,
        node_size = 150,
        font_size = 10,
        node_color = nodeColorsMap)
    plt.show()

    return


def get_graph_properties_from_reps(Xs, Ys):

    reachMatrix = []
    eccentricityMatrix = []
    safeNodesMatrix = []

    for rep in range(NUM_OF_REPS):
        print("Analyzing repetition n. " + str(rep + 1) + "/" + str(NUM_OF_REPS) + "...")
        # create new graph
        G = nx.Graph()

        coords = []

        # insert nodes into graph
        for i in range(NUM_OF_NODES):
            # first index is repetition, second index is host
            coord = (Xs[rep][i], Ys[rep][i])
            G.add_node(i, pos=coord)
            coords.append(coord)

        reachRow = []
        eccentricityRow = []
        safeNodesRow = []


        for R in R_VALUES:
            for i in range(len(coords)):
                for j in range(i + 1, len(coords)):
                    # if they are closer than R
                    if(np.linalg.norm(np.array(coords[i]) - np.array(coords[j])) < R):
                        G.add_edge(i, j)

            # get list of nodes reachable from node 0
            connectedComponent = nx.node_connected_component(G, 0)

            # get reach
            reach = len(connectedComponent)
            reachRow.append(reach)

            # get eccentricity
            ecc = get_eccentricity(G)
            eccentricityRow.append(ecc)

            # get number of nodes
            connectedGraph = get_connected_component_graph(G, connectedComponent)
            safeNodesNumber = len(get_surely_reached_nodes(connectedGraph))
            safeNodesRow.append(safeNodesNumber)


        reachMatrix.append(reachRow)
        eccentricityMatrix.append(eccentricityRow)
        safeNodesMatrix.append(safeNodesRow)

    return reachMatrix, eccentricityMatrix, safeNodesMatrix

def replacefig(fig):
    if(os.path.isfile(FIGPATH+fig)):
        os.remove(FIGPATH+fig)
    plt.savefig(FIGPATH+fig)


def plot_graph_properties(yLabel, data, title: str, Rmax, figIndex, plotErrorBars=True, xTick=10, shadowFill=False, asim=False, confidence=0.95, interpolate=False, interpolationData=None):

    if(interpolate == True):
        assert interpolationData != None

    plt.figure(figIndex)
    plt.title(title + " (" + str(int(confidence*100)) + "% CI)")
    plt.xlabel("R (m)")
    plt.ylabel(yLabel)
    plt.xticks(range(Rmax)[0::xTick])

    # insert experimental data

    values = []
    errors = []
    lowerValues = []
    upperValues = []
    for tuple in data:
        values.append(tuple[0])
        errors.append(tuple[1])
        lowerValues.append(tuple[0] - tuple[1])
        upperValues.append(tuple[0] + tuple[1])

    if(plotErrorBars == False or shadowFill == True):
        errors = None
    plt.errorbar(x=range(1, Rmax + 1), y=values, yerr=errors, capsize=3, linestyle="solid", marker='s', ecolor="black", elinewidth=0.8, capthick=0.8,markersize=1, mfc="black", mec="black")

    if(shadowFill == True and plotErrorBars == True):
        plt.fill_between(range(1, Rmax + 1), lowerValues, upperValues, alpha=0.4, facecolor='#FF9848')

    if(interpolate == True):
        plt.errorbar(x=range(1, Rmax + 1), y=interpolationData, linestyle="--", color="black", linewidth=0.7)

    replacefig("graphAnalysis" + title.replace(" ", "_") + "validation.pdf")

def sigmoid(x, a, b, N):
    y = (1/N + ((N-1)/N)*(1/(1 + math.exp(b*(a - x)))))*100
    return y

def sigmoid2(x, a, b, N):
    y = (1/N + ((N-1)/N)*(1 + math.tanh(b*(x - a)))/2)*100
    return y

def get_sigmoid_points(xValues, a, b, N):
    points = []

    for x in xValues:
        y = sigmoid2(x, a, b, N)
        points.append(y)
    return points

reachDF =  pd.DataFrame()
eccentricityDF = pd.DataFrame()
safeNodesDF= pd.DataFrame()


# if files already exist, no need to recompute everything
if(os.path.isfile(REACH_DF_FILENAME) and os.path.isfile(ECCENTRICITY_DF_FILENAME) and os.path.isfile(SAFENODES_DF_FILENAME)):
    print("Files found. Reading graph properties from csv...")
    reachDF = pd.read_csv(REACH_DF_FILENAME)
    eccentricityDF = pd.read_csv(ECCENTRICITY_DF_FILENAME)
    safeNodesDF = pd.read_csv(SAFENODES_DF_FILENAME)
else:
    #otherwise compute everthing and save into files for the next time
    print("Files not found. Reading simulation data from files and computing graph properties...")
    
    Xdata, Ydata = read_host_coords_from_file(RAWDATAFILENAME)

    reachMatrix, eccentricityMatrix, safeNodesMatrix = get_graph_properties_from_reps(Xdata, Ydata)
    reachDF = pd.DataFrame(reachMatrix, columns=R_VALUES)
    reachDF.to_csv(REACH_DF_FILENAME)

    eccentricityDF = pd.DataFrame(eccentricityMatrix, columns=R_VALUES)
    eccentricityDF.to_csv(ECCENTRICITY_DF_FILENAME)

    safeNodesDF = pd.DataFrame(safeNodesMatrix, columns=R_VALUES)
    safeNodesDF.to_csv(SAFENODES_DF_FILENAME)

# print("--- REACH DATAFRAME ---")
# print(reachDF)
# print()
# print("--- ECCENTRICITY DATAFRAME ---")
# print(eccentricityDF)
# print()
# print("--- SAFENODES DATAFRAME ---")
# print(safeNodesDF)

avgReachMCI = []
eccentricityMCI = []
safeNodesMCI = []

# print(reachDF)


for col in reachDF.columns:
    list = reachDF[col].tolist()
    tuple = su.mean_confidence_interval(list)
    avgReachMCI.append(tuple)

avgReachMCI = avgReachMCI[1:]

figureIndex = 1
# print("Saving avg reach plot")
# plot_graph_properties("Reach", avgReachMCI, "Total reach", R_MAX, figureIndex, plotErrorBars=False)

figureIndex += 1

sigmoid_a = 12
# sigmoid_b = 0.335
sigmoid_b = 1/(math.e)

if(len(sys.argv) > 1):
    sigmoid_b = float(sys.argv[1])

sigmoidPoints = get_sigmoid_points(R_VALUES[0:30], sigmoid_a, sigmoid_b, NUM_OF_NODES)


# min_err = 1
# min_b = None
# for b in np.arange(0.330, 0.340, 0.0001):

#     sigmoidPointsFull = get_sigmoid_points(R_VALUES, sigmoid_a, b, NUM_OF_NODES)


#     sumOfSqErrs = 0
#     # print("Mean squared error:")
#     for i in range(len(avgReachMCI)):
#         sumOfSqErrs += ((avgReachMCI[i][0] - sigmoidPointsFull[i])/sigmoidPointsFull[i])**2
#     MSE = sumOfSqErrs/(len(avgReachMCI))
#     if(MSE < min_err):
#         min_err = MSE
#         min_b = b
# print("Best approximation: b, MSE")
# print(str(min_b) + ", " + str(min_err))




print("Saving avgReach plot up to R = 30, with interpolation")
plot_graph_properties("Reach", avgReachMCI[0:30], "Total reach (up to R=30)", 30, figureIndex, xTick=5, interpolate=True, interpolationData=sigmoidPoints)



figureIndex += 1


for col in eccentricityDF.columns:
    list = eccentricityDF[col].tolist()
    tuple = su.mean_confidence_interval(list)
    eccentricityMCI.append(tuple)

eccentricityMCI = eccentricityMCI[1:]


print("Saving eccentricity plot")
plot_graph_properties("Eccentricity", eccentricityMCI, "Eccentricity", R_MAX, figureIndex, shadowFill=False)
figureIndex += 1


for col in safeNodesDF.columns:
    list = safeNodesDF[col].tolist()
    tuple = su.mean_confidence_interval(list)
    safeNodesMCI.append(tuple)

figureIndex += 1

print("Saving eccentricity plot up to R = 19")
plot_graph_properties("Eccentricity", eccentricityMCI[0:19], "Eccentricity (up to R=19)", 19, figureIndex, xTick=1)

figureIndex += 1

safeNodesMCI = safeNodesMCI[1:]

print("Saving safe nodes plot")
plot_graph_properties("Safe nodes", safeNodesMCI, "Safe nodes", R_MAX, figureIndex, shadowFill=False)

