"""Control table: a = -log x_max(p, mu, w) with beta = 1 - 1e-7 (EP form). Exploration only.
usage: python3 ctltable.py out.npz"""
import sys, time, numpy as np
from fastcert import xmax
P = np.array([j/80 - 1e-6 for j in range(1, 77)])
MU = np.linspace(0.05, 0.80, 24)
W = np.exp(np.linspace(np.log(0.125), np.log(4.0), 20))
a = np.full((len(P), len(MU), len(W)), np.nan)
t0 = time.time(); print('START', time.ctime(), flush=True)
for i, p in enumerate(P):
    for j, mu in enumerate(MU):
        for k, w in enumerate(W):
            x = xmax(p, mu, w, tol=1e-9, n=400)
            if x is not None: a[i, j, k] = -np.log(x)
    np.savez(sys.argv[1], P=P, MU=MU, W=W, a=a)
    print('p %.4f done  %.0fs' % (p, time.time()-t0), flush=True)
print('END', time.ctime(), flush=True)
