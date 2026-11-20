"""v3 (20 Nov): v2 with two RELAXATIONS of over-conservative points, still sufficient (PROOF.md Section 7):
(i) on cell j the ratio term uses cells i > j only (same-cell pairs are covered by W_j: for y and g in one cell,
E(y) > U_j gives both E(y) > Phi(g) and E(y) > y Phi(g)/g); (ii) published claims at ratios y below the FIRST CELL
(g_lo), not below 1/5, are the ones tested against y * max_{i >= i0} Phi_i/g. v2 header follows.
v2 (after the 19 Nov referee, findings 1-2). Exact comparison of our certified off-diagonal function Phi with what the PUBLISHED banks give (record check).

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
v2: the baseline is the fully generous one, inf over a >= 1, b >= g of a E(b/a) (monotone in k and in l, and ratios
above 1 by symmetry). A published claim at ratio y must satisfy E(y) > Phi(g) for y >= g and E(y)/y > Phi(g)/g for
y < g. Phi_i(g)/g = c_i/g + s_i is monotone on a cell, so on cell j the published claims are tested against
T_j = max(W_j, hi_j * max_{i >= j, i in claim} max(v_lo_i/lo_i, v_hi_i/hi_i)) with W_j = max_{i0 <= i <= j} U_i (claim region from
cell i0, lo >= g_claim); cells below i0 against hi_j * max_{i >= i0} v_lo_i / lo_i; ratios below 1/5: sources exactly
(E(y)/y is decreasing for a line), curves in floats on a log grid. Non-bank curves (Lu-Wang f, GNNW Thm 1, GNNW Thm 5
at its optimal p in closed form, GNNW Cor 6, NSS, ES) are FLOAT on 21 points per cell with a slope margin.
usage: ramsey_offdiag_vs_published3.py zbs_bank.json ep_extra.json lw_source.json nss_cert.json offdiag_cert.json out.tsv [g_claim]
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
    PHI = (1 + 5 ** 0.5) / 2
    def thm5(s):
        p = (0.5 * PHI + s / PHI) / (PHI * (s + 0.5))   # stationary point of a convex function of p
        assert (5 ** 0.5 - 1) / (5 ** 0.5 + 1) < p < 1
        return -0.5 * math.log(PHI * p - 1 / PHI) - s * math.log(1 - p)
    return {'GNNW5': thm5, 'GNNWc6': lambda s: s * math.log((5 ** 0.5 + 1) * (1 + 2 * s) / (4 * s)) + 0.5 * math.log(1 + 2 * s),
            'LWf': lambda s: H(s) + s * math.exp(-s) * P(s),
            'GNNW': lambda s: H(s) + (-0.25 * s + 0.03 * s * s + 0.08 * s ** 3) * math.exp(-s),
            'ES': H}


def nss_curve(path):
    nd = json.load(open(path)); SC = nd['meta']['SC']; FS = nd['meta']['FS']
    lam = [int(n[0]) / SC for n in nd['nodes']]; Fv = [int(n[1]) / FS for n in nd['nodes']]
    Dv = [int(n[2]) / SC for n in nd['nodes']]

    def F(s):
        i = min(max(bisect.bisect_right(lam, s) - 1, 0), len(lam) - 2); a, b = lam[i], lam[i + 1]; u = s - a
        return Fv[i] + Dv[i] * u + 0.5 * (Dv[i + 1] - Dv[i]) / (b - a) * u * u
    return F, lam[0], lam[-1]


def main():
    zbs_p, ep_p, lw_p, nss_p, cert_p, out = sys.argv[1:7]
    g_claim = Fr(sys.argv[7]) if len(sys.argv) > 7 else Fr(201, 1000)
    assert sha(zbs_p) == ZBS_SHA, 'zbs_bank.json hash'
    zb = json.load(open(zbs_p))
    profs = [Prof(r, 'zbs_raw') for r in zb['raw']] + [Prof(r, 'zbs_closed') for r in zb['closed']]
    profs += [Prof(r, 'ep') for r in json.load(open(ep_p))]
    assert max(P.X[-1] for P in profs) <= 5, 'a published profile reaches beyond ratio 5: pairs below 1/5 possible'
    src = [(Fr(a), Fr(b)) for a, b in zip(zb['A'], zb['B'])] + [(Fr(a), Fr(b)) for a, b in EP_SOURCES]
    srcf = [(float(a), float(b)) for a, b in src]
    curves = lw_curves(lw_p)
    nssF, nlo, nhi = nss_curve(nss_p)
    cert = json.load(open(cert_p))
    cells = cert['cells']
    n = len(cells)
    lo_ = [Fr(c['lo']) for c in cells]; hi_ = [Fr(c['hi']) for c in cells]
    vlo = [Fr(c['v_lo']) for c in cells]; vhi = [Fr(c['v_hi']) for c in cells]
    assert all(v > 0 for v in vlo + vhi)
    i0 = next(i for i in range(n) if lo_[i] >= g_claim)
    # Phi_i(g)/g = c_i/g + s_i is monotone on the cell, so its maximum is at an end (any sign of the intercept c_i)
    rat = [max(vlo[i] / lo_[i], vhi[i] / hi_[i]) for i in range(n)]
    suf = [Fr(0)] * (n + 1)
    for i in range(n - 1, i0 - 1, -1):
        suf[i] = max(suf[i + 1], rat[i])
    R0 = suf[i0]
    T, W = [], Fr(0)
    for j in range(n):
        if j >= i0:
            W = max(W, vlo[j], vhi[j])
            T.append(max(W, hi_[j] * suf[j + 1]))   # v3: cells i > j only
        else:
            T.append(hi_[j] * R0)
    rows, ok_cells = [], []
    for j, c in enumerate(cells):
        lo, hi, Tj = lo_[j], hi_[j], T[j]
        Tf = float(Tj)
        vals = [min(a + float(lo) * b, b + float(lo) * a) for a, b in srcf]
        fmin = min(vals)
        cand = [i for i, v in enumerate(vals) if v <= fmin + 1e-9]
        src_min = min(min(src[i][0] + lo * src[i][1], src[i][1] + lo * src[i][0]) for i in cand)
        fR = [(P, P.minR(lo, hi, False)) for P in profs]
        fS = [(P, P.minS(lo, hi, False)) for P in profs]
        Rlow = [P for P, m in fR if m is not None and m <= Tf + 1e-9]
        Slow = [P for P, m in fS if m is not None and m <= Tf + 1e-9]
        Rlow = [P for P in Rlow if P.minR(lo, hi, True) <= Tj]
        Slow = [P for P in Slow if P.minS(lo, hi, True) <= Tj]
        pair_violation = any(R.p + S.p <= 1 for R in Rlow for S in Slow)
        exact_ok = (src_min > Tj) and (not pair_violation)
        m = 20; sp = (float(hi) - float(lo)) / m
        pts = [float(lo) + i * sp for i in range(m + 1)]
        lit = [f(t) for f in curves.values() for t in pts] + [nssF(t) for t in pts if nlo <= t <= nhi]
        lit_min = min(lit)
        float_ok = lit_min > Tf + 3 * 3 * sp
        ok_cells.append(exact_ok and float_ok)
        rows.append('%s\t%s\t%.9f\t%.9f\t%.9f\t%d\t%d' % (c['lo'], c['hi'], Tf, float(src_min), lit_min, int(exact_ok), int(float_ok)))
    diag_ok = all(z > T[-1] for z in DIAGS)
    # ratios below 1/5: sources exactly at y = 1/5 (E(y)/y decreasing for each line); curves on a log grid (float)
    y5 = lo_[0]                                   # v3: below the first cell (g_lo), not below 1/5
    assert y5 <= Fr(1, 5)
    src_low_ok = min(min(a + y5 * b, b + y5 * a) for a, b in src) / y5 > R0
    ys = [10 ** (-4 + 4 * i / 20000) * float(y5) for i in range(20001)]
    low_min = min(min(f(y) for f in curves.values()) / y for y in ys)
    low_min = min(low_min, min(nssF(y) / y for y in ys if nlo < y <= nhi))
    low_ok = low_min > float(R0) + 1e-3
    hdr = 'lo\thi\tT_j\tpub_src_min\tlit_min(float)\texact_ok\tfloat_ok'
    open(out, 'w').write(hdr + '\n' + '\n'.join(rows) + '\n')
    claim = ok_cells[i0:]
    print('claim region from cell', i0, 'g =', cells[i0]['lo'], '; max Phi(g)/g there =', float(R0))
    print('cells in claim region', len(claim), 'passing', sum(claim), '; failing:', [cells[i0 + k]['lo'] for k, v in enumerate(claim) if not v][:10])
    print('cells below the claim region (tested as ratios y < g):', i0, 'passing', sum(ok_cells[:i0]))
    print('published diagonals above T_last:', diag_ok)
    print('ratios below g_lo = %s: sources (exact)' % lo_[0], src_low_ok, '; curves (float, min f(y)/y) %.6f vs %.6f' % (low_min, float(R0)), low_ok)
    print('ALL_OK', all(claim) and all(ok_cells[:i0]) and diag_ok and src_low_ok and low_ok)


if __name__ == '__main__':
    main()
