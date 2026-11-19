"""Driver: rounds of the float fixed point starting from the ZBS bank. usage: python3 run_fp.py <scratch> <rounds>"""
import sys, time, json, numpy as np
from bankfloat import load, LWf
from fixedpoint import Model
S = sys.argv[1]; R = int(sys.argv[2])
bank, lw = load(S + '/zbsdata/zbs_bank.json', S + '/lwdata/source.json')
m = Model(S + '/ctltable.npz', lw)
nP, nS = len(m.PP), len(m.S)
L = np.full((nP, nS), np.inf)
for Pf in bank['raw'] + bank['closed']:
    j = int(np.searchsorted(m.PP, Pf.p - 1e-12))
    v = Pf(m.S); v = np.where(np.isnan(v), np.inf, v)
    L[j] = np.minimum(L[j], v)
L = np.minimum.accumulate(L, axis=0)
i1 = int(np.argmin(abs(m.S - 1.0))); jh = int(np.argmin(abs(m.PP - 0.5)))
print('ZBS bank as loaded: L_1/2(1) = %.9f' % L[jh, i1], flush=True)
# ZBS's own source lines
A, B = bank['A'], bank['B']
order = np.argsort(A); As, Bs = A[order], np.minimum.accumulate(B[order])
def Bzbs(a):
    a = np.atleast_1d(a); k = np.searchsorted(As, a, 'right') - 1
    return np.where(k >= 0, Bs[np.maximum(k, 0)], np.inf)
rho_idx = list(range(0, nS, 5))
L0 = L.copy()
hist = []
for r in range(R):
    t0 = time.time()
    if r == 0:
        Bst = Bzbs; Bm, U = m.Bstar_fn(L)
        print('round 0 uses ZBS source lines; model B*(1.0862)=%.6f vs ZBS %.6f' % (Bm(1.0862)[0], Bzbs(1.0862)[0]), flush=True)
    else:
        Bst, U = m.Bstar_fn(L)
    Z, arg = m.route_values(L, Bst, rho_idx)
    Zf = np.empty((nP, nS))
    for j in range(nP):
        Zf[j] = np.interp(m.S, m.S[rho_idx], Z[j])      # crude: interpolate between computed ratios
    Lnew = np.minimum(L, Zf)
    Lnew = np.minimum.accumulate(Lnew, axis=0)
    Unew = m.U_of(Lnew); Lnew = np.minimum(Lnew, Unew[None, :])
    k1 = rho_idx.index(i1) if i1 in rho_idx else None
    print('round %d: L_1/2(1) %.9f -> %.9f ; route-only value at (1/2,1) %.9f ; arg %s ; %.0fs' % (
        r, L[jh, i1], Lnew[jh, i1], Z[jh, k1] if k1 is not None else np.nan, arg.get(i1, [None]*nP)[jh], time.time() - t0), flush=True)
    gain = L0 - Lnew; fin = np.isfinite(gain)
    for pj in [10, 20, 30, 40, 50, 60, 70]:
        rowg = np.where(np.isfinite(gain[pj]), gain[pj], np.nan)
        print('   p=%.4f gain vs ZBS: max %.5f at s=%.3f; at s=1: %.5f; at s=3: %.5f' % (m.PP[pj], np.nanmax(rowg), m.S[np.nanargmax(rowg)], rowg[i1], rowg[int(np.argmin(abs(m.S-3)))]), flush=True)
    L = Lnew; hist.append(L[jh, i1])
    np.savez(S + '/fp_state.npz', L=L, S=m.S, PP=m.PP, hist=np.array(hist))
