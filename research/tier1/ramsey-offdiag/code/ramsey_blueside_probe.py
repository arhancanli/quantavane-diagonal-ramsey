"""FLOAT probe (proves nothing): slack of the blue side of the pair near ratio 5, to judge an extension of the bank to
ratios 5-8. For g in [0.2, 0.3]: red(p) = min L_R(g) over profiles with p_R <= p; blue(q) = min g L_S(1/g) over profiles
with p_S <= q. Prints red(1/80), blue(q) for q in {0.95, 0.9875} and the best pair.
usage: ramsey_blueside_probe.py bank_full.json"""
import sys, json, bisect
from fractions import Fraction as Fr
d = json.load(open(sys.argv[1]))
profs = [(float(Fr(r['p'])), [float(Fr(x)) for x in r['xs']], [float(Fr(y)) for y in r['ys']]) for lst in ('raw', 'closed') for r in d[lst]]
del d
def L(xs, ys, t):
    i = min(max(bisect.bisect_right(xs, t) - 1, 0), len(xs) - 2)
    return ys[i] + (ys[i+1] - ys[i]) * (t - xs[i]) / (xs[i+1] - xs[i])
def red(g, cap):
    v = [L(xs, ys, g) for p, xs, ys in profs if p <= cap + 1e-12 and xs[0] <= g <= xs[-1]]
    return min(v) if v else float('inf')
def blue(g, cap):
    t = 1 / g
    v = [g * L(xs, ys, t) for p, xs, ys in profs if p <= cap + 1e-12 and xs[0] <= t <= xs[-1]]
    return min(v) if v else float('inf')
print('max right end of any profile:', max(xs[-1] for _, xs, _ in profs))
print('g      red(1/80)  blue(0.95)  blue(0.9875)  blue(0.9)  blue(0.75)  slack(red - blue(0.95))')
for g in [0.2, 0.2025, 0.205, 0.21, 0.22, 0.25, 0.3]:
    r = red(g, 1/80)
    print('%.4f %.6f  %.6f  %.6f  %.6f  %.6f  %+.6f' % (g, r, blue(g, 0.95), blue(g, 0.9875), blue(g, 0.9), blue(g, 0.75), r - blue(g, 0.95)))
