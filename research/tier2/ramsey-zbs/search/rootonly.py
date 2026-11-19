"""Root-only float evaluation (exploration). Route at density 1/2, ratio 1, over a given profile state L.
usage: python3 rootonly.py <scratch>"""
import sys, numpy as np, time
from bankfloat import load
from fixedpoint import Model
from fastcert import xmax
S = sys.argv[1]
bank, lw = load(S + '/zbsdata/zbs_bank.json', S + '/lwdata/source.json')
m = Model(S + '/ctltable.npz', lw)
nP, nS = len(m.PP), len(m.S)
L = np.full((nP, nS), np.inf)
for Pf in bank['raw'] + bank['closed']:
    j = int(np.searchsorted(m.PP, Pf.p - 1e-12)); v = Pf(m.S); v = np.where(np.isnan(v), np.inf, v); L[j] = np.minimum(L[j], v)
L = np.minimum.accumulate(L, axis=0)
i1 = int(np.argmin(abs(m.S - 1.0)))
MU = np.linspace(0.30, 0.50, 41); W = np.linspace(0.25, 0.70, 46)
t = time.time()
acl = np.array([[-np.log(xmax(0.5 - 1e-9, mu, w, tol=1e-11, n=600)) for w in W] for mu in MU])
print('p=1/2 control grid %.0fs; min a %.5f' % (time.time() - t, acl.min()), flush=True)
A, B = bank['A'], bank['B']; order = np.argsort(A); As, Bs = A[order], np.minimum.accumulate(B[order])
def Bzbs(a):
    a = np.atleast_1d(a); k = np.searchsorted(As, a, 'right') - 1
    return np.where(k >= 0, Bs[np.maximum(k, 0)], np.inf)
Bmod, U = m.Bstar_fn(L)
C = -np.log(MU)
col = L[:, i1]; Gs = np.linspace(1.20, 1.30, 4001)
# descent table with this mu grid
m.C = C
M = m.descent_table(L, i1, Gs)
for nm, Bf in [('ZBS source lines', Bzbs), ('model sources from ZBS profiles', Bmod)]:
    best = (np.inf,)
    for e in np.linspace(0, 0.1, 201):
        a = acl + e; b = Bf(a.ravel()).reshape(a.shape); rhs = a + b
        for im in range(len(MU)):
            for iw in range(len(W)):
                Phi = np.maximum.accumulate(Gs + W[iw] * M[:, im])
                if rhs[im, iw] > Phi[-1] or not np.isfinite(rhs[im, iw]): continue
                G = np.interp(rhs[im, iw], Phi, Gs)
                if G < best[0]: best = (G, MU[im], W[iw], e, a[im, iw], b[im, iw])
    print('%-32s root route value %.6f  (mu %.4f w %.4f extra %.4f a %.5f b %.5f)' % ((nm,) + best), flush=True)
print('ZBS R* 1.252369589, EP z 1.250290354; model B*(1.0862): ZBS %.5f model %.5f' % (Bzbs(1.0862)[0], Bmod(1.0862)[0]))
