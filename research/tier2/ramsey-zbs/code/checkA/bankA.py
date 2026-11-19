"""Checker A, bank objects: exact re-implementation of ZBS's Boolean checks (Lemmas/DiagRamsey_V5Fast.lean at
c2875f33: ProfF.ok, LeafF.check, TermF.check, RouteF.check + cellCheck, ClosedPF.check, SourceF.check) on Fractions,
with ivA enclosures for exp.  A profile reference is ('zr', i) / ('zc', i) for ZBS raw/closed profile i, or
('nr', i) / ('nc', i) for our new raw/closed profile i.  A source reference is ('z', h) or ('n', h)."""
if not __debug__:
    raise SystemExit('checker A is written with assert statements; refusing to run under python -O')
from fractions import Fraction as Fr
from bisect import bisect_left
import ivA


class NList(list):
    """list that refuses negative indices (a certificate index must name an object, never count from the end)."""
    def __getitem__(self, i):
        if isinstance(i, int) and i < 0: raise IndexError('negative index in certificate')
        return list.__getitem__(self, i)


class Prof:
    __slots__ = ('p', 'xs', 'ys')
    def __init__(self, d):
        self.p = Fr(d['p']); self.xs = [Fr(t) for t in d['xs']]; self.ys = [Fr(t) for t in d['ys']]
    def at(self, r):
        """ZBS evalF on sorted nodes: first segment whose right end is >= r, clamped interpolation."""
        xs, ys = self.xs, self.ys
        k = bisect_left(xs, r, 1)          # first segment i = k - 1 whose right end xs[k] >= r (same as a linear scan)
        if k >= len(xs): return ys[-1]
        i = k - 1
        x0, x1, y0, y1 = xs[i], xs[i + 1], ys[i], ys[i + 1]
        return y0 + (y1 - y0) / (x1 - x0) * max(Fr(0), min(r, x1) - x0)


def prof_ok(P, m):
    xs, ys = P.xs, P.ys
    return (0 < P.p < 1 and len(xs) >= 2 and len(xs) == len(ys) and all(xs[i] < xs[i + 1] for i in range(len(xs) - 1))
            and xs[0] > 0 and m > 0 and all(m <= P.at(x) for x in xs))


def no_knot(knots, bp):
    """every knot strictly inside (bp[0], bp[-1]) is a breakpoint (so the PL function is affine between bp)."""
    s = set(bp)
    return all((k in s) for k in knots if bp[0] < k < bp[-1])


def no_knot_refl(knots, bp):
    s = set(bp)
    return all((1 / k in s) for k in knots if k > 0 and bp[0] < 1 / k < bp[-1])


def bp_ok(bp, lo, hi):
    return len(bp) >= 1 and all(bp[i] < bp[i + 1] for i in range(len(bp) - 1)) and bp[0] == lo and bp[-1] == hi and bp[0] > 0


def gL(us, ds, s):
    return sum(d * max(Fr(0), min(s, us[j + 1]) - us[j]) for j, d in enumerate(ds))


class GL:
    """the same function as gL(us, ds, .) (sum over cells of d_j * clamp), with prefix sums (us increasing)."""
    def __init__(self, us, ds):
        self.us, self.ds = us, ds; self.pre = [Fr(0)]
        for j, d in enumerate(ds): self.pre.append(self.pre[-1] + d * (us[j + 1] - us[j]))
    def __call__(self, s):
        us = self.us
        if s <= us[0]: return Fr(0)
        if s >= us[-1]: return self.pre[-1]
        j = bisect_left(us, s) - 1                 # us[j] < s <= us[j + 1]
        return self.pre[j] + self.ds[j] * (s - us[j])


def exp_le(a, b):
    """e^a <= b, certified (ZBS expLeB)."""
    return ivA.exp(Fr(a)).hif() <= b


class Bank:
    def __init__(self, zbs, new, ctl_ok):
        """zbs: parsed ZBS tables (dict, strings); new: our certificate dict; ctl_ok(c) -> bool (control check)."""
        self.zr = NList(Prof(d) for d in zbs['raw']); self.zc = NList(Prof(d) for d in zbs['closed'])
        self.zA = NList(Fr(a) for a in zbs['A']); self.zB = NList(Fr(b) for b in zbs['B'])
        self.lines = NList((Fr(c), Fr(d)) for c, d in zbs['lines'])
        self.zctl = zbs['ctl']
        self.nr = NList(Prof(d) for d in new['raw']); self.nc = NList(Prof(d) for d in new['closed'])
        self.nA = NList(Fr(s['A']) for s in new['sources']); self.nB = NList(Fr(s['B']) for s in new['sources'])
        self.ctl = NList(new['controls']); self.ctl_ok = ctl_ok; self._ctlres = {}
        self.newsrc = NList(new['sources'])

    def prof(self, ref):
        k, i = ref[0], int(ref[1])
        return {'zr': self.zr, 'zc': self.zc, 'nr': self.nr, 'nc': self.nc}[k][i]

    def raw_prof(self, ref):        # closed pieces may only use RAW profiles
        assert ref[0] in ('zr', 'nr'); return self.prof(ref)

    def src(self, ref):
        k, h = ref[0], int(ref[1])
        return (self.zA[h], self.zB[h]) if k == 'z' else (self.nA[h], self.nB[h])

    def control(self, i):
        if i not in self._ctlres: self._ctlres[i] = self.ctl_ok(self.ctl[i])
        assert self._ctlres[i], 'control %d' % i
        c = self.ctl[i]
        return Fr(c['p']), Fr(c['mu']), Fr(c['w']), Fr(c['x'])

    def term_ok(self, T):
        p, mu, w, x = self.control(int(T['c']))
        A, B = self.src(T['src'])
        xi, nu, ys, aU, bU = (Fr(T[k]) for k in ('xi', 'nu', 'ys', 'aU', 'bU'))
        assert 0 < xi < x, 'xi'
        assert xi < ivA.exp(-A).lof(), 'xi < e^{-A_sigma}'
        assert 0 < nu < mu and ys > 0, 'nu, ys'
        assert exp_le(-aU, xi) and exp_le(-bU, nu), 'aU, bU'
        return p, mu, w, x, A, B, xi, nu, ys, aU, bU

    def leaf_ok(self, P, L):
        p, mu, w, x, A, B, xi, nu, ys, aU, bU = self.term_ok(L)
        mg, lo, hi = Fr(L['margin']), Fr(L['lo']), Fr(L['hi']); bp = [Fr(t) for t in L['bp']]
        assert p <= P.p and mg > 0 and lo > 0 and bp_ok(bp, lo, hi) and no_knot(P.xs, bp), 'leaf shape'
        c = mg + aU / (1 + w); d = mg + (B + ys + w * bU) / (1 + w)
        assert all(c + d * t <= P.at(t) for t in bp), 'leaf inequality'
        return lo, hi

    def route_ok(self, P, R):
        p, mu, w, x, A, B, xi, nu, ys, aU, bU = self.term_ok(R['t'])
        us = [Fr(t) for t in R['us']]; ds = [Fr(t) for t in R['ds']]
        g0, hm, mg, lo, hi = (Fr(R[k]) for k in ('g0', 'hm', 'margin', 'lo', 'hi'))
        bp = [Fr(t) for t in R['bp']]; th = us[0]
        assert p < P.p and len(us) == len(ds) + 1 and len(ds) > 0, 'route shape'
        assert all(us[i] < us[i + 1] for i in range(len(ds))) and th > 0 and g0 > 0, 'us'
        assert th <= lo and hi <= us[-1] and hm > 0 and mg > 0, 'route range'
        gf = GL(us, ds)
        for j, cl in enumerate(R['calls']):
            Pc = self.prof(cl['ch']); z = Fr(cl['z']); cbp = [Fr(t) for t in cl['bp']]
            assert Pc.xs[0] <= us[j] and us[j + 1] <= Pc.xs[-1], 'child domain %d' % j
            assert 0 < z and exp_le(-ds[j], z) and z < 1 - Pc.p, 'child slope %d' % j
            assert bp_ok(cbp, us[j], us[j + 1]) and no_knot(Pc.xs, cbp) and no_knot(us, cbp), 'child bp %d' % j
            assert all(Pc.at(t) <= g0 - hm + gf(t) for t in cbp), 'child below route %d' % j
        assert len(R['calls']) == len(ds), 'one call per cell'
        assert bp_ok(bp, lo, hi) and no_knot(P.xs, bp) and no_knot(us, bp), 'route bp'
        assert all(mg + g0 + gf(t) <= P.at(t) for t in bp), 'profile above route'
        c0 = mg + (aU + w * th * bU) / (1 + w); c1 = (B + ys) / (1 + w); c2 = w / (1 + w)
        assert all(c0 + c1 * t + c2 * gf(t) <= P.at(t) for t in bp), 'route terminal inequality'
        return lo, hi

    def closed_piece_ok(self, Q, pc):
        lo, hi = Fr(pc['lo']), Fr(pc['hi']); bp = [Fr(t) for t in pc['bp']]
        R = self.raw_prof(pc['R'])
        assert R.xs[0] <= lo and hi <= R.xs[-1] and bp_ok(bp, lo, hi), 'closed dom'
        assert no_knot(R.xs, bp) and no_knot(Q.xs, bp) and all(R.at(t) <= Q.at(t) for t in bp), 'closed R <= Q'
        if pc['kind'] == 'density':
            assert R.p <= Q.p, 'density copy'
        else:
            S = self.raw_prof(pc['S'])
            assert R.p + S.p <= 1 and lo > 0 and S.xs[0] <= 1 / hi and 1 / lo <= S.xs[-1], 'pair'
            assert no_knot_refl(S.xs, bp) and all(t * S.at(1 / t) <= Q.at(t) for t in bp), 'reflected'
        return lo, hi

    def line_le(self, k, A, B, eta, t):
        c, d = self.lines[k]
        return c + d * t <= A + B * t - eta * (1 + t)

    def source_ok(self, h):
        S = self.newsrc[h]
        A, B = self.nA[h], self.nB[h]
        Lo, Hi, eps, eta = (Fr(S[k]) for k in ('Lo', 'Hi', 'eps', 'eta')); kL, kR = int(S['kL']), int(S['kR'])
        assert A > 0 and B > 0 and 0 < Lo < Hi and eps > 0 and eta > 0, 'source shape'
        assert self.line_le(kL, A, B, eps, Fr(0)) and self.line_le(kL, A, B, eps, Lo), 'left tail'
        assert self.line_le(kR, A, B, eps, Hi) and self.lines[kR][1] <= B - eps, 'right tail'
        cur = Lo
        for cell in S['cells']:
            lo, hi = Fr(cell['lo']), Fr(cell['hi'])
            assert lo == cur and lo < hi, 'source chain'; cur = hi
            if cell['kind'] == 'grounded':
                k = int(cell['k']); assert self.line_le(k, A, B, eta, lo) and self.line_le(k, A, B, eta, hi), 'grounded'
            else:
                R, Sb = self.prof(cell['PR']), self.prof(cell['PB']); bp = [Fr(t) for t in cell['bp']]
                assert R.p + Sb.p <= 1 and R.xs[0] <= lo and hi <= R.xs[-1], 'pair dom R'
                assert Sb.xs[0] <= 1 / hi and 1 / lo <= Sb.xs[-1] and lo > 0 and bp_ok(bp, lo, hi), 'pair dom S'
                assert no_knot(R.xs, bp) and no_knot_refl(Sb.xs, bp), 'pair knots'
                assert all(R.at(t) <= (A - eta) + (B - eta) * t for t in bp), 'pair R'
                assert all(t * Sb.at(1 / t) <= (A - eta) + (B - eta) * t for t in bp), 'pair S'
        assert cur == Hi, 'source chain end'
        return True

    def profile_ok(self, P, pieces, m, kind):
        assert prof_ok(P, Fr(m)), 'profile ok'
        cur = P.xs[0]
        for pc in pieces:
            if kind == 'raw':
                lo, hi = self.leaf_ok(P, pc) if pc['kind'] == 'leaf' else self.route_ok(P, pc)
            else:
                lo, hi = self.closed_piece_ok(P, pc)
            assert lo == cur and lo < hi, 'piece chain'; cur = hi
        assert cur == P.xs[-1], 'pieces cover domain'
        return True
