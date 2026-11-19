"""FLOAT probe (proves nothing): can LEAF pieces (Definition 5.4(1)) built from the bank's existing validated controls
and terminal data give blue-side profiles at ratios 5-8 cheap enough for pairs at gamma in [0.125, 0.2]?
Leaf value at ratio t for terminal data (aU = A, bU = B, nu, control w): (A + t (B + w (-log nu))) / (1 + w).
Blue side of the pair at gamma: gamma * leaf(1/gamma) = (gamma A + B + w b) / (1 + w); needs the control density
p_c <= 1 - p_R. Red side: min L_R(gamma) over profiles with p_R <= cap. Lu-Wang f for reference.
usage: ramsey_leafext_probe.py bank_full.json lw_source.json"""
import sys, json, bisect, math
from fractions import Fraction as Fr
d = json.load(open(sys.argv[1]))
ctl = [(float(Fr(c['p'])), float(Fr(c['w']))) for c in d['controls']]
terms = {}
for r in d['raw']:
    for pc in r.get('pieces') or []:
        t = pc.get('t')
        if not t: continue
        key = (t['c'], t['aU'], t['bU'], t['nu'])
        if key not in terms:
            pcn, w = ctl[t['c']]
            terms[key] = (pcn, w, float(Fr(t['aU'])), float(Fr(t['bU'])), -math.log(float(Fr(t['nu']))))
profs = [(float(Fr(r['p'])), [float(Fr(x)) for x in r['xs']], [float(Fr(y)) for y in r['ys']]) for lst in ('raw', 'closed') for r in d[lst]]
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
print('distinct terminals', len(terms))
print('g       f(g)      best pair over p_R (red, blue-leaf)            gain over f')
for g in [0.12, 0.125, 0.13, 0.14, 0.15, 0.16, 0.175, 0.19, 0.1975, 0.2, 0.21, 0.25]:
    best = (float('inf'), None)
    for cap in sorted(set(p for p, _, _ in profs)):
        reds = [L(xs, ys, g) for p, xs, ys in profs if p <= cap + 1e-12 and xs[0] <= g <= xs[-1]]
        if not reds: continue
        rv = min(reds)
        bl = [(g * A + B + w * b) / (1 + w) for pc, w, A, B, b in terms.values() if pc <= 1 - cap + 1e-12]
        if not bl: continue
        bv = min(bl)
        v = max(rv, bv)
        if v < best[0]: best = (v, (cap, rv, bv))
    v, (cap, rv, bv) = best
    print('%.4f %.6f  %.6f (p_R %.4f: red %.6f, blue %.6f)  %+.6f' % (g, f(g), v, cap, rv, bv, f(g) - v))
