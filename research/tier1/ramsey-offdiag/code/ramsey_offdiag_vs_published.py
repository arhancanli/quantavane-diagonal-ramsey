"""Exact comparison of our certified off-diagonal function Phi with what the PUBLISHED banks give (record check).

For each cell j = [lo, hi] of our certificate let U_j = max(v_lo, v_hi) (Phi <= U_j on the cell; Phi is affine there)
and W_j = max_{i <= j} U_i. Published claims checked to exceed W_j on cell j (so that also the monotone published
bound inf_{g' >= g} E_pub(g') exceeds Phi(g) on the cell):
  - ZBS P0r12 sources (2,713) and EvolvingPrograms' three new sources: both orientations, min over [lo, hi]
    (A + g B increasing): exact;
  - every pair of ZBS claims (1,902 raw, 1,003 closed) and EP profile literals (205; treated as valid claims, which
    only lowers the baseline) with p_R + p_S <= 1: the pair bound max(L_R(g), g L_S(1/g)) exceeds W_j on the cell
    whenever min_{cell n I_R} L_R > W_j or min_{cell n 1/I_S} g L_S(1/g) > W_j: exact on candidates (a float
    pre-filter keeps every claim whose float minimum is <= W_j + 1e-9; float error here is < 1e-13);
  - the published diagonals (EP 625145177/500000000, ZBS 626184844701/500000000000): exact;
Non-bank curves (Lu-Wang f, GNNW Thm 1, Erdos-Szekeres) are checked in floats on 20 points per cell with a slope
margin (reported separately; FLOAT).
usage: ramsey_offdiag_vs_published.py zbs_bank.json ep_extra.json lw_source.json offdiag_cert.json out.tsv
"""
import sys, json, bisect, math, hashlib
from fractions import Fraction as Fr

ZBS_SHA = '2946c6561f562ea01a5f9b60ac0812c689af71985c60378e11c89e8cdc003bf0'
EP_SOURCES = [
    ('1086180879838687/1000000000000000',
     '11640399543290787172985714354555752537/36367644171000000000000000000000000000'),
    ('523723367013/500000000000', '659232501933912836000511047884943/1949512210000000000000000000000000'),
    ('2956367223781/1000000000000', '53408694539/1000000000000'),
]
DIAGS = [Fr(625145177, 500000000), Fr(626184844701, 500000000000)]


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


class Prof:
    def __init__(self, r, tag):
        self.tag = tag
        self.p = Fr(r['p'])
        ys = ['625145177/500000000' if y == 'rawExponent' else y for y in r['ys']]
        self.X = [Fr(x) for x in r['xs']]; self.Y = [Fr(y) for y in ys]
        self.x = [float(v) for v in self.X]; self.y = [float(v) for v in self.Y]
        assert all(a < b for a, b in zip(self.X, self.X[1:])) and len(self.X) == len(self.Y) >= 2

    def Lf(self, t):
        x, y = self.x, self.y
        i = min(max(bisect.bisect_right(x, t) - 1, 0), len(x) - 2)
        return y[i] + (y[i + 1] - y[i]) * (t - x[i]) / (x[i + 1] - x[i])

    def Lq(self, t):
        X, Y = self.X, self.Y
        i = min(max(bisect.bisect_right(X, t) - 1, 0), len(X) - 2)
        assert X[i] <= t <= X[i + 1]
        return Y[i] + (Y[i + 1] - Y[i]) * (t - X[i]) / (X[i + 1] - X[i])

    def minR(self, lo, hi, exact):
        # min of L over [lo, hi] n I (None if empty)
        X = self.X
        a, b = max(lo, X[0]), min(hi, X[-1])
        if a > b:
            return None
        pts = [a, b] + [v for v in X if a < v < b]
        if exact:
            return min(self.Lq(t) for t in pts)
        return min(self.Lf(float(t)) for t in pts)

    def minS(self, lo, hi, exact):
        # min of g L(1/g) over g in [lo, hi] with 1/g in I
        X = self.X
        a, b = max(lo, 1 / X[-1]), min(hi, 1 / X[0])
        if a > b:
            return None
        pts = [a, b] + [1 / v for v in X if 1 / b < v < 1 / a]
        if exact:
            return min(t * self.Lq(1 / t) for t in pts)
        return min(float(t) * self.Lf(1 / float(t)) for t in pts)


def lw_curves(path):
    d = json.load(open(path))
    X = [float(Fr(a)) for a in d['nodes']]; V = [float(Fr(a)) for a in d['values']]
    DV = [float(Fr(a)) for a in d['derivatives']]

    def P(t):
        i = min(max(bisect.bisect_right(X, t) - 1, 0), len(X) - 2)
        a, b = X[i], X[i + 1]; dl = b - a; u = t - a; D = V[i + 1] - V[i]
        return (V[i] + DV[i] * u + (3 * D / dl - 2 * DV[i] - DV[i + 1]) / dl * u * u
                + (DV[i] + DV[i + 1] - 2 * D / dl) / dl ** 2 * u ** 3)
    H = lambda s: (1 + s) * math.log1p(s) - s * math.log(s)
    return {'LWf': lambda s: H(s) + s * math.exp(-s) * P(s),
            'GNNW': lambda s: H(s) + (-0.25 * s + 0.03 * s * s + 0.08 * s ** 3) * math.exp(-s),
            'ES': H}


def main():
    zbs_p, ep_p, lw_p, cert_p, out = sys.argv[1:6]
    assert sha(zbs_p) == ZBS_SHA, 'zbs_bank.json hash'
    zb = json.load(open(zbs_p))
    profs = [Prof(r, 'zbs_raw') for r in zb['raw']] + [Prof(r, 'zbs_closed') for r in zb['closed']]
    profs += [Prof(r, 'ep') for r in json.load(open(ep_p))]
    src = [(Fr(a), Fr(b)) for a, b in zip(zb['A'], zb['B'])] + [(Fr(a), Fr(b)) for a, b in EP_SOURCES]
    srcf = [(float(a), float(b)) for a, b in src]
    curves = lw_curves(lw_p)
    cert = json.load(open(cert_p))
    cells = cert['cells']
    W, rows, ok_cells = Fr(0), [], []
    for j, c in enumerate(cells):
        lo, hi = Fr(c['lo']), Fr(c['hi'])
        U = max(Fr(c['v_lo']), Fr(c['v_hi']))
        W = max(W, U)
        Wf = float(W)
        # sources (increasing in g): exact min at lo over float candidates
        vals = [min(a + float(lo) * b, b + float(lo) * a) for a, b in srcf]
        fmin = min(vals)
        cand = [i for i, v in enumerate(vals) if v <= fmin + 1e-9]
        src_min = min(min(src[i][0] + lo * src[i][1], src[i][1] + lo * src[i][0]) for i in cand)
        # pairs
        fR = [(P, P.minR(lo, hi, False)) for P in profs]
        fS = [(P, P.minS(lo, hi, False)) for P in profs]
        Rlow = [P for P, m in fR if m is not None and m <= Wf + 1e-9]
        Slow = [P for P, m in fS if m is not None and m <= Wf + 1e-9]
        Rlow = [P for P in Rlow if P.minR(lo, hi, True) <= W]
        Slow = [P for P in Slow if P.minS(lo, hi, True) <= W]
        pair_violation = any(R.p + S.p <= 1 for R in Rlow for S in Slow)
        # float value of the published pair lower bound (reporting only)
        Rv = sorted((P.p, m) for P, m in fR if m is not None)
        Sv = sorted((float(P.p), m) for P, m in fS if m is not None)
        pair_lb = float('inf')
        if Rv and Sv:
            ps = [s[0] for s in Sv]; pref, mm = [], float('inf')
            for s in Sv:
                mm = min(mm, s[1]); pref.append(mm)
            for p, m in Rv:
                k = bisect.bisect_right(ps, 1.0 - float(p) + 1e-15) - 1
                if k >= 0:
                    pair_lb = min(pair_lb, max(m, pref[k]))
        diag_ok = all(z > W for z in DIAGS)
        exact_ok = (src_min > W) and (not pair_violation) and diag_ok
        # non-bank curves, FLOAT: 20 points per cell, margin 3 * slope bound * spacing (slope <= 3 on [0.2, 1])
        n = 20; sp = (float(hi) - float(lo)) / n
        lit_min = min(f(float(lo) + i * sp) for f in curves.values() for i in range(n + 1))
        float_ok = lit_min > Wf + 3 * 3 * sp
        ok = exact_ok and float_ok
        ok_cells.append(ok)
        rows.append('%s\t%s\t%.9f\t%.9f\t%.9f\t%.9f\t%.9f\t%d\t%d' % (
            c['lo'], c['hi'], float(U), float(W), float(src_min), pair_lb, lit_min, int(exact_ok), int(float_ok)))
    hdr = 'lo\thi\tU_ours\tW_ours\tpub_src_min\tpub_pair_lb(float)\tlit_min(float)\texact_ok\tfloat_ok'
    open(out, 'w').write(hdr + '\n' + '\n'.join(rows) + '\n')
    # report the maximal final run of cells that pass
    k = len(cells)
    while k > 0 and ok_cells[k - 1]:
        k -= 1
    print('cells', len(cells), 'passing', sum(ok_cells))
    print('final run of passing cells starts at cell', k, 'g =', cells[k]['lo'] if k < len(cells) else None)
    bad = [i for i in range(k, len(cells)) if not ok_cells[i]]
    print('failures inside the run:', bad[:10])
    print('first failing cells overall:', [cells[i]['lo'] for i in range(len(cells)) if not ok_cells[i]][-5:])


if __name__ == '__main__':
    main()
