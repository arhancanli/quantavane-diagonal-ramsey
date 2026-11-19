"""Builder (float search; PROVES NOTHING) of an off-diagonal certificate over a validated bank.

For each cell [lo, hi] of [g_lo, 1] it picks ONE bank claim set and an affine majorant Phi_i on the cell:
  kind 'src'  : source h, orientation 'AB' (A_h + g B_h) or 'BA' (B_h + g A_h)
  kind 'pair' : claims R, S (raw or closed) with p_R + p_S <= 1, [lo, hi] in I_R, [1/hi, 1/lo] in I_S,
                bound max(L_R(g), g L_S(1/g))
v_lo, v_hi are rounded UP to multiples of 1e-12 (plus 2e-12); the exact checkers decide.
usage: ramsey_offdiag_build.py bank_full.json out_cert.json [step_den (2000)] [g_lo (1/5)]
"""
import sys, json, bisect, hashlib, math
from fractions import Fraction as Fr

ROUND = 10 ** 12


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''):
            h.update(b)
    return h.hexdigest()


def up(x):
    return Fr(math.ceil(x * ROUND) + 2, ROUND)


def Lv(xs, ys, t):
    i = min(max(bisect.bisect_right(xs, t) - 1, 0), len(xs) - 2)
    a, b = xs[i], xs[i + 1]
    return ys[i] + (ys[i + 1] - ys[i]) * (t - a) / (b - a)


def main():
    bank, out = sys.argv[1], sys.argv[2]
    den = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
    g_lo = Fr(sys.argv[4]) if len(sys.argv) > 4 else Fr(1, 5)
    d = json.load(open(bank))
    claims = []  # (list, idx, p, xs, ys)
    for lst in ('raw', 'closed'):
        for i, r in enumerate(d[lst]):
            claims.append((lst, i, float(Fr(r['p'])), [float(Fr(x)) for x in r['xs']], [float(Fr(y)) for y in r['ys']]))
    AB = [(float(Fr(s['A'])), float(Fr(s['B']))) for s in d['sources']]
    root_closed = d['root']['closed']
    del d
    # cells: uniform grid of step 1/den from g_lo to 1 - 1/den, then [1 - 1/den, 1 - 1e-10], [1 - 1e-10, 1]
    edges = []
    k0 = math.ceil(g_lo * den)
    edges.append(g_lo)
    for k in range(k0 if Fr(k0, den) > g_lo else k0 + 1, den):
        edges.append(Fr(k, den))
    edges += [1 - Fr(1, 10 ** 10), Fr(1)]
    cells = []
    for lo_q, hi_q in zip(edges[:-1], edges[1:]):
        lo, hi = float(lo_q), float(hi_q)
        best = None
        # sources: affine, increasing (A, B > 0): value at hi decides; Phi = the line itself
        for o, f in (('AB', lambda A, B: (A + lo * B, A + hi * B)), ('BA', lambda A, B: (B + lo * A, B + hi * A))):
            h = min(range(len(AB)), key=lambda j: f(*AB[j])[1])
            a, b = f(*AB[h])
            cand = (max(a, b), {'kind': 'src', 'h': h, 'orient': o}, a, b, [])
            if best is None or cand[0] < best[0]:
                best = cand
        # pairs
        Rs, Ss = [], []
        for c in claims:
            lst, i, p, xs, ys = c
            if xs[0] <= lo and hi <= xs[-1]:
                pts = [lo, hi] + [x for x in xs if lo < x < hi]
                Rs.append((max(Lv(xs, ys, t) for t in pts), p, c))
            if xs[0] <= 1 / hi and 1 / lo <= xs[-1]:
                pts = [lo, hi] + [1 / y for y in xs if 1 / hi < y < 1 / lo]
                Ss.append((max(t * Lv(xs, ys, 1 / t) for t in pts), p, c))
        if Rs and Ss:
            Ss.sort(key=lambda s: s[1])
            ps = [s[1] for s in Ss]
            pref, m, mi = [], float('inf'), None
            for j, s in enumerate(Ss):
                if s[0] < m:
                    m, mi = s[0], j
                pref.append((m, mi))
            for vR, pR, cR in sorted(Rs, key=lambda r: r[0])[:400]:
                j = bisect.bisect_right(ps, 1.0 - pR + 1e-15) - 1
                if j < 0:
                    continue
                vS, jS = pref[j]
                cS = Ss[jS][2]
                if max(vR, vS) >= best[0]:
                    continue
                # affine majorant of max(L_R, g L_S(1/g)) over the check points
                pts = sorted(set([lo, hi] + [x for x in cR[3] if lo < x < hi] + [1 / y for y in cS[3] if 1 / hi < y < 1 / lo]))
                vals = [max(Lv(cR[3], cR[4], t), t * Lv(cS[3], cS[4], 1 / t)) for t in pts]
                a, b = vals[0], vals[-1]
                dlt = max(v - (a + (b - a) * (t - lo) / (hi - lo)) for t, v in zip(pts, vals))
                dlt = max(dlt, 0.0)
                cand = (max(a, b) + dlt, {'kind': 'pair', 'R': [cR[0], cR[1]], 'S': [cS[0], cS[1]]}, a + dlt, b + dlt, [])
                if cand[0] < best[0]:
                    best = cand
        _, obj, a, b, _ = best
        obj.update({'lo': str(lo_q), 'hi': str(hi_q), 'v_lo': str(up(a)), 'v_hi': str(up(b))})
        cells.append(obj)
    res = {'bank': bank, 'bank_sha256': sha256(bank), 'g_lo': str(g_lo), 'cells': cells,
           'note': 'built by ramsey_offdiag_build.py (float search); validity is decided only by the exact checkers'}
    json.dump(res, open(out, 'w'))
    kinds = {}
    for c in cells:
        kinds[c['kind']] = kinds.get(c['kind'], 0) + 1
    print('cells', len(cells), kinds)
    for c in cells:
        if float(Fr(c['hi'])) in (0.25, 0.5, 0.75, 0.9, 1.0) or float(Fr(c['lo'])) in (0.2,):
            print(c['lo'], c['hi'], c['kind'], float(Fr(c['v_lo'])), float(Fr(c['v_hi'])))


if __name__ == '__main__':
    main()
