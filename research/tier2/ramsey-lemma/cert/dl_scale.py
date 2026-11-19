"""Float (exploration; proves nothing). Usage: dl_scale.py control.json da. For bump deficits of growing size at the
saturated box: the L1 linearised bound of dl_robust_float.py (exact grid right region) against the TRUE change of V
(exact chain LP of dprime_float.py on the same grid drift)."""
import sys, json
import numpy as np
from fractions import Fraction as Fr
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import dl_robust_float as M
from dprime_float import DPrime
from explore1 import a_of
ctl = {k: float(Fr(s)) for k, s in json.load(open(sys.argv[1])).items()}
da = float(sys.argv[2]); c = dict(ctl); c['x'] = ctl['x'] * np.exp(-da); w = c['w']
below = np.geomspace(1e-5, 0.03, 40)[:-1]; chain = np.geomspace(0.03, 1, 101)
v = np.concatenate([below, chain]); b = int(np.searchsorted(v, 0.03 - 1e-15))
Q, Y, E, z, Dl, sig, F = M.reference(c, v, b)
D = DPrime(c, v, v[b], nq=6000)
qg, M0 = D.qg[D.ok0], D.M0[D.ok0]; Ht = qg * M0; dHt = np.gradient(Ht, qg)
uu = np.geomspace(1e-14, v[b], 20000); du = np.diff(np.concatenate([[0], uu]))
ILp = np.sum(np.maximum(-w * (1 + np.log(uu)) - np.interp(Q, qg, dHt), 0) * du)
yg = np.linspace(-w - 0.01, sig.max() + 0.01, 40001); Hg = np.array([np.max(Ht - qg * y) for y in yg])
A = M.Adv(c, v, b, ILp, Y, E, z, 0.0, Dl, sig, None, True, lambda y: np.interp(y, yg, Hg))
V0, Q0 = D.V(v, -w * v * np.log(v))
lv = np.log(v)
print('da %+.1e: saturated V %.3e Q %.5f' % (da, V0, Q0))
for frac in [1e-3, 3e-3, 1e-2, 3e-2, 0.1, 0.3]:
    best = (-1, None)
    for cen in np.linspace(np.log(v[b + 1]), np.log(0.9), 25):
        for s in [0.1, 0.2, 0.4, 0.8, 1.6, 3.2]:
            for shape in ('par', 'gau'):
                xx = (lv - cen) / s
                bmp = (np.maximum(0, 1 - xx ** 2) if shape == 'par' else np.exp(-xx ** 2)) * A.gv
                m = np.zeros(len(v)); m[A.idx] = bmp[A.idx]
                if m.max() <= 0: continue
                m *= frac * 0.168 / m.max()            # peak = frac * g(1/e)
                if not A.feasible(m): continue
                pr = A.profit(m)
                if pr > best[0]: best = (pr, m)
    pr, m = best
    if m is None: print('  frac %.0e: none feasible' % frac); continue
    Vt, Qt = D.V(v, -w * v * np.log(v) - m)
    print('  peak %.2e (v %.3f): L1 bound dV %+.3e (S %.3e: Q drop bound %.3e)   TRUE dV %+.3e (Q drop %.3e)'
          % (m.max(), v[np.argmax(m)], pr, A.S(m), A.S(m), Vt - V0, Q0 - Qt))
