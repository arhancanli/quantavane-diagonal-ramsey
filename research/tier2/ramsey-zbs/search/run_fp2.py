"""Driver for the piece-consistent operator. usage: python3 run_fp2.py <scratch> <rounds>"""
import sys, time, numpy as np
from bankfloat import load
from fixedpoint import Model
S = sys.argv[1]; R = int(sys.argv[2])
bank, lw = load(S + '/zbsdata/zbs_bank.json', S + '/lwdata/source.json')
m = Model(S + '/ctltable.npz', lw)
nP, nS = len(m.PP), len(m.S)
L = np.full((nP, nS), np.inf)
for Pf in bank['raw'] + bank['closed']:
    j = int(np.searchsorted(m.PP, Pf.p - 1e-12)); v = Pf(m.S); v = np.where(np.isnan(v), np.inf, v); L[j] = np.minimum(L[j], v)
L = np.minimum.accumulate(L, axis=0)
if len(sys.argv) > 4: L = np.load(sys.argv[4])      # e.g. ZBS + EP extra profiles
i1 = int(np.argmin(abs(m.S - 1.0))); jh = int(np.argmin(abs(m.PP - 0.5)))
A, B = bank['A'], bank['B']; order = np.argsort(A); As, Bs = A[order], np.minimum.accumulate(B[order])
def Bzbs(a):
    a = np.atleast_1d(a); k = np.searchsorted(As, a, 'right') - 1
    return np.where(k >= 0, Bs[np.maximum(k, 0)], np.inf)
kp = int(sys.argv[3]) if len(sys.argv) > 3 else 5
for r in range(R):
    t0 = time.time()
    Bst = Bzbs if r == 0 else m.Bstar_fn(L)[0]
    knots, Rr, Ll = m.piece_values(L, Bst, kp=kp)
    # knot values: max(right req of piece ending here, left req of piece starting here); first knot S[0] only left req
    kv = np.full((nP, len(knots) + 1), np.inf)
    kv[:, 0] = Ll[:, 0]
    for k in range(len(knots)):
        kv[:, k + 1] = Rr[:, k] if k + 1 >= len(knots) else np.maximum(Rr[:, k], Ll[:, k + 1])
    xs = np.array([m.S[0]] + [m.S[i] for i in knots])
    Z = np.array([np.interp(m.S, xs, np.where(np.isfinite(kv[j]), kv[j], 1e9)) for j in range(nP)])
    # a new PL profile replaces the old one only where its whole piece is better: keep it simple: pointwise min of
    # the two PL families is realised by keeping both (old ZBS/previous profiles stay in the bank as children)
    Lnew = np.minimum(L, Z)
    Lnew = np.minimum.accumulate(Lnew, axis=0)
    Lnew = np.minimum(Lnew, m.U_of(Lnew)[None, :])
    Bn = m.Bstar_fn(Lnew)[0]
    Zr, _ = m.route_values(Lnew, Bn, [i1])            # root needs only ratio 1 (point domain, as EP's root)
    print('round %d: L_1/2(1) %.9f -> %.9f ; piece profile (1/2,1) %.9f ; ROOT (point) %.9f ; %.0fs' % (
        r, L[jh, i1], Lnew[jh, i1], Z[jh, i1], Zr[jh, 0], time.time() - t0), flush=True)
    L = Lnew
    np.savez(S + '/fp2_state_kp%d.npz' % kp, L=L, S=m.S, PP=m.PP)
