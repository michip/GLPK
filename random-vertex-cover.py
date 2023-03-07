#!/usr/bin/python3

# For creating huge LPs to play around

import numpy as np
import pulp as lp
from numpy import linalg as LA
from pulp import *
import networkx as nx
import random
import sys


try:
    nv = int(sys.argv[1])
except (ValueError, IndexError):
    print("Usage " + sys.argv[0] + " number-of-vertices")
    exit()

# Generate random graph

#g = nx.random_geometric_graph(20000, radius = 1)
g = nx.binomial_graph(nv, .5)

#print(g)

#rint(len(g.edges()))
w = []

for i in range(0, len(g.edges())):
    w.append(random.randint(1,50))

# print(w)

for i in range(0, len(g.nodes())):
    g.add_node(i, weight = w[i])


weights = dict(g.nodes(data ='weight', default=1))

nx.get_node_attributes(g, 'weight')
# print(weights)

# Define problem

prob = LpProblem("VertexCoverProblem", LpMinimize)

# Variables

x = LpVariable.dicts("x", g.nodes(), cat ='LpBinary')


# Add constraints

prob += lpSum([weights[i]*x[i] for i in g.nodes()]), "obj"

for (i,j) in g.edges():
    prob += x[i] + x[j] >= 1

for i in g.nodes():
    prob += 0 <= x[i] <= 1


data = prob.to_dict()

prob.writeMPS("VertexCover"+str(nv)+".mps")
