"""FLOAT GATE (exploration; proves nothing) for extending the bank below ratio 1/5.
For g < 1/5 a pair needs a blue-side profile at ratio 1/g > 5, which the bank does not have. A necessary condition for
a gain is that the red side alone is already below Lu-Wang's f: for each density cap p, m_p(g) = min over validated raw
and closed profiles R with p_R <= p and g in I_R of L_R(g). Prints m_p(g) - f(g) for caps p in {1/80, 1/16, 1/4, 1/2}.
usage: ramsey_below5_gate.py bank_full.json lw_source.json"""
import sys, json, bisect, math
from fractions import Fraction as Fr
d = json.load(open(sys.argv[1]))
profs = []
for lst in ('raw', 'closed'):
    for r in d[lst]:
        xs = [float(Fr(x)) for x in r['xs']]
        if xs[0] < 0.2:
            profs.append((float(Fr(r['p'])), xs, [float(Fr(y)) for y in r['ys']]))
del d
lw = json.load(open(sys.argv[2]))
X = [float(Fr(a)) for a in lw['nodes']]; V = [float(Fr(a)) for a in lw['values']]; DV = [float(Fr(a)) for a in lw['derivatives']]
def P(t):
    i = min(max(bisect.bisect_right(X, t) - 1, 0), len(X) - 2); a, b = X[i], X[i + 1]; dl = b - a; u = t - a; D = V[i + 1] - V[i]
    return V[i] + DV[i]*u + (3*D/dl - 2*DV[i] - DV[i+1])/dl*u*u + (DV[i] + DV[i+1] - 2*D/dl)/dl**2*u**3
f = lambda s: (1+s)*math.log1p(s) - s*math.log(s) + s*math.exp(-s)*P(s)
def L(xs, ys, t):
    i = min(max(bisect.bisect_right(xs, t) - 1, 0), len(xs) - 2)
    return ys[i] + (ys[i+1] - ys[i]) * (t - xs[i]) / (xs[i+1] - xs[i])
caps = [1/80, 1/16, 1/4, 1/2, 79/80]
print('profiles reaching below 1/5:', len(profs), '; densities', sorted(set(round(p, 4) for p, _, _ in profs))[:12])
print('g      f(g)      ' + '  '.join('m_%.4f-f' % c for c in caps))
for g in [0.02, 0.03, 0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.19, 0.1975, 0.2, 0.21, 0.25, 0.3]:
    row = []
    for c in caps:
        vals = [L(xs, ys, g) for p, xs, ys in profs if p <= c + 1e-12 and xs[0] <= g <= xs[-1]]
        row.append(min(vals) - f(g) if vals else float('nan'))
    print('%.4f %.6f  ' % (g, f(g)) + '  '.join('%+.6f' % v for v in row))
