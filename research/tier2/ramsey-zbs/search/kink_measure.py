"""Measure the piece-width (kink) loss in a gen2 state (exploration): at sampled knots, compare the latest profile
value of each density bucket with the point optimum (zero-width piece) computed against the same final pool.
usage: python3 kink_measure.py state.pkl"""
import sys, pickle      # pickle: our own local model state
import numpy as np
from gen2 import Gen

g = pickle.load(open(sys.argv[1], 'rb'))
EX = np.array([0, 0.001, 0.002, 0.004, 0.007, 0.01, 0.015, 0.02, 0.03, 0.045, 0.06, 0.08, 0.1, 0.13, 0.17, 0.22, 0.3, 0.4, 0.5, 0.6])
L = g.envelope()
buckets = [j for j in range(1, g.nB) if 0.27 <= g.PP[j] <= 0.75]
rows = []
for s in [0.40, 0.42, 0.45, 0.6, 0.75, 0.9, 0.95, 0.99, 1.2, 1.6, 2.0, 2.3, 2.4, 2.5, 2.7]:
    r = int(round((s - g.S[0]) / 0.0025))
    recs = g.knot(r, EX, L[:, r], point=True)
    for j in buckets:
        if recs[j] is None or not np.isfinite(L[j, r]): continue
        zstar = recs[j]['vals'][-1]
        rows.append((s, g.PP[j], L[j, r], zstar, L[j, r] - zstar))
gaps = np.array([x[4] for x in rows])
print('knots x buckets sampled:', len(rows))
print('gap = profile value - point optimum: mean %.3e  median %.3e  90%% %.3e  max %.3e  min %.3e' % (
    gaps.mean(), np.median(gaps), np.quantile(gaps, 0.9), gaps.max(), gaps.min()))
for s in sorted(set(x[0] for x in rows)):
    gs = np.array([x[4] for x in rows if x[0] == s])
    print('ratio %.2f: mean gap %.3e  max %.3e' % (s, gs.mean(), gs.max()))
