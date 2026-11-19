"""Checker B, bank objects (written separately from checker A's bankA.py): fmpq rationals, Arb for exp.
Implements the conditions of ZBS Definitions 5.4-5.5 / source covers (paper Sec. 5) in the data layout of their
DiagRamsey_V5Fast.lean (leaf, route with cells, closed density/pair pieces, source with tails and cells)."""
from bisect import bisect_left
from flint import arb, fmpq


def Q(s):
    s = str(s)
    if '/' in s:
        n, d = s.split('/'); return fmpq(int(n), int(d))
    return fmpq(int(s))


def need(c, msg):
    if not c: raise AssertionError(msg)


class NL(list):
    """refuses negative indices (written separately from checker A's NList)."""
    def __getitem__(self, i):
        if isinstance(i, int) and i < 0: raise AssertionError('negative certificate index')
        return list.__getitem__(self, i)


class PL:
    """piecewise-linear profile; value at r inside [x0, xN] by the segment containing r (left-closed search)."""
    def __init__(self, d):
        self.p = Q(d['p']); self.x = [Q(t) for t in d['xs']]; self.y = [Q(t) for t in d['ys']]
        n = len(self.x)
        need(n >= 2 and n == len(self.y), 'profile size')
        for i in range(n - 1): need(self.x[i] < self.x[i + 1], 'profile knots increase')
        self.kset = set(self.x)

    def __call__(self, r):
        x = self.x
        need(x[0] <= r <= x[-1], 'evaluation inside domain')
        i = bisect_left(x, r)
        if i < len(x) and x[i] == r: return self.y[i]
        return self.y[i - 1] + (self.y[i] - self.y[i - 1]) * (r - x[i - 1]) / (x[i] - x[i - 1])


def affine_between(knots, bp):
    """knots strictly between bp[0] and bp[-1] must all be in bp."""
    s = set(bp); lo, hi = bp[0], bp[-1]
    for k in knots:
        if lo < k < hi: need(k in s, 'knot %s missing from breakpoints' % k)


def increasing_from_to(bp, lo, hi):
    need(len(bp) >= 1 and bp[0] == lo and bp[-1] == hi and lo > 0, 'breakpoint ends')
    for i in range(len(bp) - 1): need(bp[i] < bp[i + 1], 'breakpoints increase')


def e_le(a, b):
    """certify exp(a) <= b."""
    return arb(a).exp() <= arb(b)


class Route:
    def __init__(self, us, ds):
        self.us, self.ds = us, ds
        self.pre = [fmpq(0)]
        for j, d in enumerate(ds): self.pre.append(self.pre[-1] + d * (us[j + 1] - us[j]))

    def G(self, s):
        """int_{u_0}^{s} slope, s in [u_0, u_M] (and constant beyond)."""
        us = self.us
        if s <= us[0]: return fmpq(0)
        if s >= us[-1]: return self.pre[-1]
        j = bisect_left(us, s) - 1
        if us[j + 1] == s: return self.pre[j + 1]
        return self.pre[j] + self.ds[j] * (s - us[j])


class BankB:
    def __init__(self, zbs, new, ctl_check):
        self.P = {'zr': NL(PL(d) for d in zbs['raw']), 'zc': NL(PL(d) for d in zbs['closed']),
                  'nr': NL(PL(d) for d in new['raw']), 'nc': NL(PL(d) for d in new['closed'])}
        self.srcAB = {'z': NL(zip(map(Q, zbs['A']), map(Q, zbs['B']))),
                      'n': NL((Q(s['A']), Q(s['B'])) for s in new['sources'])}
        self.lines = NL((Q(c), Q(d)) for c, d in zbs['lines'])
        self.newsrc = NL(new['sources']); self.ctl = NL(new['controls']); self.ctl_check = ctl_check; self.ctl_done = {}

    def ctrl(self, i):
        if i not in self.ctl_done:
            self.ctl_check(self.ctl[i]); self.ctl_done[i] = True
        c = self.ctl[i]
        return Q(c['p']), Q(c['mu']), Q(c['w']), Q(c['x'])

    def terminal(self, T):
        p, mu, w, x = self.ctrl(int(T['c']))
        A, B = self.srcAB[T['src'][0]][int(T['src'][1])]
        xi, nu, ys, aU, bU = (Q(T[k]) for k in ('xi', 'nu', 'ys', 'aU', 'bU'))
        need(0 < xi and xi < x, 'xi in (0, x)')
        need(arb(xi) < arb(-A).exp(), 'xi < exp(-A_sigma)')
        need(0 < nu and nu < mu and ys > 0, 'nu, ys')
        need(e_le(-aU, xi) and e_le(-bU, nu), 'aU >= -log xi, bU >= -log nu')
        return p, w, A, B, ys, aU, bU

    def leaf(self, P, L):
        p, w, A, B, ys, aU, bU = self.terminal(L)
        m, lo, hi = Q(L['margin']), Q(L['lo']), Q(L['hi']); bp = [Q(t) for t in L['bp']]
        need(p <= P.p and m > 0, 'leaf density / margin')
        increasing_from_to(bp, lo, hi); affine_between(P.x, bp)
        for r in bp:
            need(m + aU / (1 + w) + r * (m + (B + ys + w * bU) / (1 + w)) <= P(r), 'leaf height at %s' % r)
        return lo, hi

    def route(self, P, R):
        T = R['t']; p, w, A, B, ys, aU, bU = self.terminal(T)
        us = [Q(t) for t in R['us']]; ds = [Q(t) for t in R['ds']]; calls = R['calls']
        g0, hm, m, lo, hi = (Q(R[k]) for k in ('g0', 'hm', 'margin', 'lo', 'hi'))
        bp = [Q(t) for t in R['bp']]
        need(p < P.p, 'route density strictly below')
        need(len(ds) >= 1 and len(us) == len(ds) + 1 and len(calls) == len(ds), 'route sizes')
        for j in range(len(ds)): need(us[j] < us[j + 1], 'partition increases')
        th = us[0]
        need(th > 0 and g0 > 0 and hm > 0 and m > 0 and th <= lo and hi <= us[-1], 'route parameters')
        g = Route(us, ds)
        for j, cl in enumerate(calls):
            C = self.P[cl['ch'][0]][int(cl['ch'][1])]; z = Q(cl['z']); cbp = [Q(t) for t in cl['bp']]
            need(C.x[0] <= us[j] and us[j + 1] <= C.x[-1], 'child covers cell')
            need(z > 0 and z < 1 - C.p and e_le(-ds[j], z), 'cell slope > -log(1 - p_child)')
            increasing_from_to(cbp, us[j], us[j + 1]); affine_between(C.x, cbp); affine_between(us, cbp)
            for s in cbp: need(C(s) <= g0 - hm + g.G(s), 'child under route at %s' % s)
        increasing_from_to(bp, lo, hi); affine_between(P.x, bp); affine_between(us, bp)
        for r in bp:
            Gr = g.G(r)
            need(m + g0 + Gr <= P(r), 'height above route')
            need(m + (aU + w * th * bU) / (1 + w) + r * (B + ys) / (1 + w) + w / (1 + w) * Gr <= P(r), 'terminal')
        return lo, hi

    def closed_piece(self, Qp, c):
        lo, hi = Q(c['lo']), Q(c['hi']); bp = [Q(t) for t in c['bp']]
        need(c['R'][0] in ('zr', 'nr'), 'closed uses raw')
        R = self.P[c['R'][0]][int(c['R'][1])]
        need(R.x[0] <= lo and hi <= R.x[-1], 'closed R domain')
        increasing_from_to(bp, lo, hi); affine_between(R.x, bp); affine_between(Qp.x, bp)
        for r in bp: need(R(r) <= Qp(r), 'closed R <= Q')
        if c['kind'] == 'density':
            need(R.p <= Qp.p, 'density copy order')
        else:
            need(c['S'][0] in ('zr', 'nr'), 'closed uses raw')
            S = self.P[c['S'][0]][int(c['S'][1])]
            need(R.p + S.p <= 1 and S.x[0] <= 1 / hi and 1 / lo <= S.x[-1], 'pair densities / domain')
            affine_between([1 / k for k in S.x], bp)
            for r in bp: need(r * S(1 / r) <= Qp(r), 'reflected <= Q')
        return lo, hi

    def source(self, h):
        S = self.newsrc[h]; A, B = self.srcAB['n'][h]
        Lo, Hi, eps, eta = (Q(S[k]) for k in ('Lo', 'Hi', 'eps', 'eta')); kL, kR = int(S['kL']), int(S['kR'])
        need(A > 0 and B > 0 and 0 < Lo < Hi and eps > 0 and eta > 0, 'source parameters')
        def under(k, e, t):
            c, d = self.lines[k]; return c + d * t <= A + B * t - e * (1 + t)
        need(under(kL, eps, fmpq(0)) and under(kL, eps, Lo), 'left tail line')
        need(under(kR, eps, Hi) and self.lines[kR][1] <= B - eps, 'right tail line')
        pos = Lo
        for c in S['cells']:
            lo, hi = Q(c['lo']), Q(c['hi'])
            need(lo == pos and lo < hi, 'cells chain'); pos = hi
            if c['kind'] == 'grounded':
                need(under(int(c['k']), eta, lo) and under(int(c['k']), eta, hi), 'grounded cell')
            else:
                R = self.P[c['PR'][0]][int(c['PR'][1])]; Sb = self.P[c['PB'][0]][int(c['PB'][1])]
                bp = [Q(t) for t in c['bp']]
                need(R.p + Sb.p <= 1 and R.x[0] <= lo and hi <= R.x[-1] and Sb.x[0] <= 1 / hi and 1 / lo <= Sb.x[-1], 'pair')
                increasing_from_to(bp, lo, hi); affine_between(R.x, bp); affine_between([1 / k for k in Sb.x], bp)
                for t in bp:
                    need(R(t) <= (A - eta) + (B - eta) * t and t * Sb(1 / t) <= (A - eta) + (B - eta) * t, 'pair cell')
        need(pos == Hi, 'cells end at Hi')

    def profile(self, P, pieces, mn, raw):
        mn = Q(mn)
        need(0 < P.p < 1 and P.x[0] > 0 and mn > 0, 'profile ok')
        for r in P.x: need(P(r) >= mn, 'profile min')
        pos = P.x[0]
        for c in pieces:
            lo, hi = (self.leaf(P, c) if c['kind'] == 'leaf' else self.route(P, c)) if raw else self.closed_piece(P, c)
            need(lo == pos and lo < hi, 'pieces chain'); pos = hi
        need(pos == P.x[-1], 'pieces end')
