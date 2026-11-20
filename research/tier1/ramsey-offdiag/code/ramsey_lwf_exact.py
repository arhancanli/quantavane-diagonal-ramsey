"""Exact (Arb ball) check that Lu-Wang's f exceeds the comparison threshold T_j on every claimed cell (referee 20 Nov,
finding 3: on [0.165, 0.2] the float margin after the slope allowance was only 1.9e-5).
f(t) = (1+t) log(1+t) - t log t + t e^{-t} P(t), P the cubic Hermite interpolant of source.json (rational data, P(t)
evaluated exactly at rational t); f is increasing on (0, 1] (f-hat concave, SC Lemma 2.3 / P4.5, and f'(1) > 0), so
min of f on a cell is f(lo_j). T_j as in ramsey_offdiag_vs_published3.py (exact rationals from the certificate).
usage: <flint python> -I ramsey_lwf_exact.py lw_source.json offdiag_cert.json g_claim"""
import sys, json
from fractions import Fraction as Fr
import flint
from flint import arb, fmpq, ctx
assert flint.__version__ == '0.9.0'
ctx.prec = 200
d = json.load(open(sys.argv[1]))
X = [Fr(a) for a in d['nodes']]; V = [Fr(a) for a in d['values']]; DV = [Fr(a) for a in d['derivatives']]
def Pq(t):
    import bisect
    i = min(max(bisect.bisect_right(X, t) - 1, 0), len(X) - 2)
    a, b = X[i], X[i + 1]; assert a <= t <= b
    dl = b - a; u = t - a; D = V[i + 1] - V[i]
    return V[i] + DV[i]*u + (3*D/dl - 2*DV[i] - DV[i+1])/dl*u*u + (DV[i] + DV[i+1] - 2*D/dl)/dl**2*u**3
def A(q):
    return arb(fmpq(q.numerator, q.denominator))
def f_lower(t):
    ta = A(t)
    v = (1 + ta) * (1 + ta).log() - ta * ta.log() + ta * (-ta).exp() * A(Pq(t))
    return v.lower()          # arb lower end (an arb with zero radius)
cert = json.load(open(sys.argv[2])); cells = cert['cells']
g_claim = Fr(sys.argv[3])
n = len(cells)
lo_ = [Fr(c['lo']) for c in cells]; hi_ = [Fr(c['hi']) for c in cells]
vlo = [Fr(c['v_lo']) for c in cells]; vhi = [Fr(c['v_hi']) for c in cells]
i0 = next(i for i in range(n) if lo_[i] >= g_claim)
rat = [max(vlo[i] / lo_[i], vhi[i] / hi_[i]) for i in range(n)]
suf = [Fr(0)] * (n + 1)
for i in range(n - 1, i0 - 1, -1):
    suf[i] = max(suf[i + 1], rat[i])
R0 = suf[i0]; W = Fr(0); worst = None; bad = []
for j in range(n):
    if j >= i0:
        W = max(W, vlo[j], vhi[j]); T = max(W, hi_[j] * suf[j + 1])
    else:
        T = hi_[j] * R0
    fl = f_lower(lo_[j])
    gap = fl - A(T)
    ok = bool(gap > 0)
    if not ok: bad.append(cells[j]['lo'])
    m = float(gap.mid())
    if worst is None or m < worst[0]: worst = (m, cells[j]['lo'])
print('cells', n, 'claim from', cells[i0]['lo'], '; f(lo_j) > T_j (Arb, 200 bits) fails at', bad[:10], '; smallest margin %.3e at g = %s' % worst)
print('LWF_EXACT_OK', not bad)
