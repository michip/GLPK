#!/usr/bin/python3

# Import sparse matrix out-#.mat as M

import numpy as np
from scipy import sparse
import sys

try:
    nv = int(sys.argv[1])
except (ValueError, IndexError):
    print("Usage " + sys.argv[0] + " iteration-number")
    exit()

data = np.loadtxt("out-"+str(nv)+".mat")
rows = list(map(lambda x: int(x-1),data[1:,0]))
cols = list(map(lambda x: int(x-1),data[1:,1]))
shp = (int(data[0][0]), int(data[0][1]))
M = sparse.coo_matrix((data[1:,2],(rows,cols)),shape=shp)

# OK, this is stupid, but what the heck.
# Maybe try this, or do something smart: https://stackoverflow.com/questions/43281468/condition-number-of-sparse-matrix

print(np.linalg.cond(M.todense()))
