import numpy as np

blist = np.array(
    [[ 0, -1, 1], 
     [ 1,  0, 1], 
     [ 0,  1, 1], 
     [-1,  0, 1], 
     [-1,  1, 0],
     [-1, -1, 0],
     [1,0,0],
     [0,1,0],
     [0,0,1]]
    )
nlist = np.array(
    [[ 1,  1, 1],
     [-1,  1, 1], 
     [-1, -1, 1], 
     [ 1, -1, 1],
     [1,0,0],
     [0,1,0],
     [0,0,1],
     [ 0, -1, 1], 
      [ 1,  0, 1], 
      [ 0,  1, 1], 
      [-1,  0, 1], 
      [-1,  1, 0],
      [-1, -1, 0]]
    )
nsign = np.array([1, -1, 1, -1])
ztol = 1e-1
ss = [(0, 0),
      (1, 0), 
      (1, 1),
      (2, 1),
      (2, 2),
      (3, 2),
      (3, 3),
      (0, 3),
      (0, 4),
      (2, 4),
      (1, 5),
      (3, 5)]

def getslip(i):
    return nlist[ss[i][0],:], blist[ss[i][1],:]
def bdot(b1,b2):
    return np.round(b1.dot(b2) / np.abs(b1.dot(b2)))
def bwedge(b1,b2):
    return b1.cross(b2) * bdot(b1,b2)
def normalize(b):
    b = np.array(b)
    b[np.abs(b) < ztol] = 0
    if all(np.abs(b) < ztol):
        return b
    return np.round(b/min(np.abs(b[np.abs(b) > ztol]))).astype(int)    
def which(A,Alist):
    A = normalize(A)
    for i in range(len(Alist)):
        if all([abs(Ai + Aj) < ztol for (Ai,Aj) in zip(A,Alist[i])]):
            return i, 1
        if all([abs(Ai - Aj) < ztol for (Ai,Aj) in zip(A,Alist[i])]):
            return i, -1
    return None, None
def whichslip(slip_fingerprint):
    if any(map(lambda x: x is None, slip_fingerprint)):
        return 15
    elif slip_fingerprint in ss:
        return ss.index(slip_fingerprint)
    elif slip_fingerprint[1] > 5:
        return 12
    elif slip_fingerprint[0] > 3:
        return 13
    else:
        return None
    
def whichb(b):
    return which(b,blist)
def whichn(n):
    return which(n,nlist)
def isHirth(b):
    i, _ = whichb(b)
    return (i is not None and i >=6 )
def isLomer(n):
    i, _ = whichn(n)
    return (i is not None and i >=4 )

