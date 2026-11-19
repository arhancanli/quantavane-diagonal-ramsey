"""Float values of the non-bank published off-diagonal exponents at g (exploration only).
LW f (Lu-Wang arXiv:2609.14525, source.json @ 5ec98f47), GNNW Thm 1 (arXiv:2407.19026v2), Erdos-Szekeres H.
usage: ramsey_lit_curves.py source.json compare.tsv"""
import sys, json, math, bisect
from fractions import Fraction as Fr
d = json.load(open(sys.argv[1]))
X = [float(Fr(a)) for a in d['nodes']]; V = [float(Fr(a)) for a in d['values']]; DV = [float(Fr(a)) for a in d['derivatives']]
def P(t):
    i = min(max(bisect.bisect_right(X, t) - 1, 0), len(X) - 2)
    a, b = X[i], X[i + 1]; dl = b - a; u = t - a; D = V[i + 1] - V[i]
    return V[i] + DV[i]*u + (3*D/dl - 2*DV[i] - DV[i+1])/dl*u*u + (DV[i] + DV[i+1] - 2*D/dl)/dl**2*u**3
H = lambda s: (1+s)*math.log1p(s) - s*math.log(s)
f = lambda s: H(s) + s*math.exp(-s)*P(s)
gn = lambda s: H(s) + (-0.25*s + 0.03*s*s + 0.08*s**3)*math.exp(-s)
rows = [l.split('\t') for l in open(sys.argv[2]).read().split('\n')[1:] if l]
print('g\tES\tGNNW\tLWf\tpub_bank\tours\tours-min(all published)')
for r in rows:
    g = float(r[0]); pb = float(r[3]); o = float(r[6])
    allpub = min(pb, f(g), gn(g))
    print('%.2f\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%+.6f' % (g, H(g), gn(g), f(g), pb, o, o - allpub))
