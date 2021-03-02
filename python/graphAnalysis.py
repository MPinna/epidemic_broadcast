#!/usr/bin/env python

import networkx as nx
import scipy.stats as st
import scipy.optimize as op
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def readHostCoordsFromFile(file):
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

def getEccentricity(G: nx.Graph):
    connectComp = nx.node_connected_component(G, 0)
    S = G.subgraph(connectComp)
    e = nx.eccentricity(S, 0)
    return e

def getNumOfReachableNodes(G: nx.Graph):
    connectComp = nx.node_connected_component(G, 0)
    n = len(connectComp)
    return n

def drawGraph(G: nx.Graph):
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

NUM_OF_REPS = 200
NUM_OF_NODES = 100

R=5
filename = "./big_csv/big-p0.1R" + str(R) + ".csv"

Xs, Ys = readHostCoordsFromFile(filename)

# create new graph
G = nx.Graph()

coords = []


for i in range(NUM_OF_NODES):
    # first index is repetition, second index is host
    coord = (Xs[0][i], Ys[0][i])
    G.add_node(i, pos=coord)
    coords.append(coord)


for i in range(len(coords)):
    for j in range(i + 1, len(coords)):
        # if they are closer than R
        if(np.linalg.norm(np.array(coords[i]) - np.array(coords[j])) < R):
            G.add_edge(i, j)

n = getNumOfReachableNodes(G)
print("Reachable nodes:")
print(n)

e = getEccentricity(G)
print("Eccentricity:")
print(e)

drawGraph(G)
