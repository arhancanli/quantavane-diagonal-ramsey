"""Float comparison of the off-diagonal exponent E(g) (log R(k, g k) <= E(g) k + o(k)) that each bank yields.

Exploration only; proves nothing. Two bounds per bank:
  src(g)  = min over source pairs (A, B) of min(A + g B, B + g A)       [claim (SOURCE_h), both colour namings]
  pair(g) = min over raw profiles R, S with p_R + p_S <= 1, g in I_R, 1/g in I_S of max(L_R(g), g L_S(1/g))
            [complementary pair, the off-diagonal form of Corollary 5.10]
usage: python3 -I ramsey_offdiag_float.py zbs_bank.json certCD3.json out.tsv
"""
import sys, json, bisect
from fractions import Fraction as Fr


def fl(s):
    return float(Fr(s))


def load_profiles(raws):
    out = []
    for r in raws:
        xs = [fl(x) for x in r['xs']]; ys = [fl(y) for y in r['ys']]
        out.append((fl(r['p']), xs, ys))
    return out


def L(prof, t):
    p, xs, ys = prof
    if t < xs[0] - 1e-15 or t > xs[-1] + 1e-15:
        return None
    i = bisect.bisect_right(xs, t) - 1
    i = min(max(i, 0), len(xs) - 2)
    a, b = xs[i], xs[i + 1]
    return ys[i] + (ys[i + 1] - ys[i]) * (t - a) / (b - a)


def src_bound(AB, g):
    return min(min(A + g * B, B + g * A) for A, B in AB)


def pair_bound(profs, g):
    # g(p): best L_R(g) over R with p_R <= p ; h(q): best g L_S(1/g) over S with p_S <= q
    lr = [(p, L((p, xs, ys), g)) for p, xs, ys in profs]
    ls = [(p, L((p, xs, ys), 1.0 / g)) for p, xs, ys in profs]
    lr = sorted((p, v) for p, v in lr if v is not None)
    ls = sorted((p, g * v) for p, v in ls if v is not None)
    if not lr or not ls:
        return None
    # prefix minima
    pr, vr = [], []; m = 1e9
    for p, v in lr:
        m = min(m, v); pr.append(p); vr.append(m)
    ps, vs = [], []; m = 1e9
    for p, v in ls:
        m = min(m, v); ps.append(p); vs.append(m)
    best = None
    for i, p in enumerate(pr):
        q = 1.0 - p + 1e-12
        j = bisect.bisect_right(ps, q) - 1
        if j < 0:
            continue
        val = max(vr[i], vs[j])
        best = val if best is None or val < best else best
    return best


if __name__ == '__main__':
    zb = json.load(open(sys.argv[1]))
    zAB = [(fl(a), fl(b)) for a, b in zip(zb['A'], zb['B'])]
    zraw = load_profiles(zb['raw'])
    cd = json.load(open(sys.argv[2]))
    nAB = [(fl(s['A']), fl(s['B'])) for s in cd['sources']]
    nraw = load_profiles(cd['raw'])
    print('ZBS sources', len(zAB), 'raw', len(zraw), '| new sources', len(nAB), 'raw', len(nraw))
    gs = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9,
          0.92, 0.94, 0.96, 0.97, 0.98, 0.99, 0.995, 1.0]
    rows = []
    hdr = 'g\tzbs_src\tzbs_pair\tnew_src\tnew_pair\tunion_best\tzbs_best\tgain'
    print(hdr)
    for g in gs:
        a = src_bound(zAB, g); b = pair_bound(zraw, g)
        c = src_bound(nAB, g); d = pair_bound(nraw + zraw, g)
        zbest = min(x for x in (a, b) if x is not None)
        ubest = min(x for x in (a, b, c, d) if x is not None)
        row = '%.3f\t%.6f\t%s\t%.6f\t%s\t%.6f\t%.6f\t%.6f' % (g, a, '%.6f' % b if b else 'NA', c,
              '%.6f' % d if d else 'NA', ubest, zbest, zbest - ubest)
        print(row); rows.append(row)
    open(sys.argv[3], 'w').write(hdr + '\n' + '\n'.join(rows) + '\n')
