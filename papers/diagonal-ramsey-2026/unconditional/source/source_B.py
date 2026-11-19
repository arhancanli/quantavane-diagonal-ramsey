"""Program B for Lu-Wang's source certificate (UNCONDITIONAL_PLAN item L4), written separately from source_A.py.

Same claim as source_A.py: on [ALPHA, 1], with Lu-Wang's per-cell controls (r, w) used as data, mu = r s,
p0 = 1 - e^{-f'(s)}, X = (1 - mu)^w p0^{1/(1 - mu)}, A = -log X, Y = e^{-b(A)}, b(A) = sup_l (f-hat(l) - A l):
    Delta(s) = (w + 1) f(s) + log X - s b(A) + w s log mu > 0,   0 < mu < 1, 0 < p0 < 1, b(A) > 0,
plus f'(1) > 0 and 2 f'(1) > f(1).
Differences from program A (independent implementation):
  * arithmetic: python-flint 0.9.0 (pinned) Arb balls at 300 bits and fmpq;
  * b(A) is evaluated through the TANGENCY PARAMETER, not through a concave tangent bound: on the left branch
    (A >= f'(1)) the tangency point t solves f'(t) = A and b = psi(t) := f(t) - t f'(t); on the right branch
    (A <= f(1) - f'(1)) the reflected tangency point u = 1/lambda* solves psi(u) = A and b = f'(u); in the corner
    lambda* = 1 and b = f(1) - A. A certified bracket of t (or u) gives b by monotonicity (psi increasing, f'
    decreasing), so b(A) lies between the values at the bracket ends;
  * brackets are found by bisection on rationals (no floating point at all);
  * the mean-value bound uses the derivative Delta'(s) = (w+1) f'(s) + l'(s)(1 - s lambda*) - b(A(s)) + w log(r s) + w
    with lambda* and b over the cell enclosed from the brackets at the two ends of the A-range of the cell.
usage: <flint-python> -I source_B.py <source.json> <source_cells.json> <out.json> [--alpha=p/q] [--from=i --to=j --partial=yes]
       [--require=p/q] (margin probe: certify Delta(s) > (p/q) s instead of Delta(s) > 0)"""
import sys, os, json, hashlib, time, bisect
import flint
from flint import arb, fmpq

if flint.__version__ != '0.9.0':
    raise SystemExit('pinned to python-flint 0.9.0')
flint.ctx.prec = 300
TAU = fmpq(0)      # margin probe: certify Delta(s) - TAU s > 0 (0 for the claim itself)
SRC_SHA = 'f3e4a4eaf3f778ae125466eb6d47647a38fd38430fdcdffe8c5f774f9718c08c'
CELLS_SHA = '055d86954ba7bc4e636ded1c0bb603a142ca738174e79a997f17b0c51c524bff'


class Refuse(Exception):
    pass


def need(ok, why):
    if not ok:
        raise Refuse(why)


def sha(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def Q(s):
    s = str(s)
    if '/' in s:
        n, d = s.split('/'); return fmpq(int(n), int(d))
    return fmpq(int(s))


def ball(lo, hi):
    return arb(lo).union(arb(hi))


def _exact(x):
    """the exact rational value of an arb with zero radius (an endpoint from .lower() or .upper())."""
    m, e = x.man_exp()
    m, e = int(m), int(e)
    return fmpq(m * 2 ** e) if e >= 0 else fmpq(m, 2 ** (-e))


def lowq(x):
    return _exact(x.lower())


def upq(x):
    return _exact(x.upper())


class Source:
    def __init__(self, path):
        need(sha(path) == SRC_SHA, 'source.json pin')
        d = json.load(open(path))
        self.t = [Q(x) for x in d['nodes']]
        v = [Q(x) for x in d['values']]; dv = [Q(x) for x in d['derivatives']]
        need(len(self.t) == 2280 and self.t[0] == 0 and self.t[-1] == 1, 'nodes')
        self.k = []
        for i in range(2279):
            a, b = self.t[i], self.t[i + 1]; dl = b - a; D = (v[i + 1] - v[i]) / dl
            self.k.append((a, v[i], dv[i], (3 * D - 2 * dv[i] - dv[i + 1]) / dl, (dv[i] + dv[i + 1] - 2 * D) / (dl * dl)))

    def idx(self, x):
        lo, hi = 0, 2278
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if self.t[mid] <= x: lo = mid
            else: hi = mid - 1
        return lo

    def Pd(self, i, X):
        a, c0, c1, c2, c3 = self.k[i]; u = X - a
        return (c0 + u * (c1 + u * (c2 + u * c3)), c1 + u * (2 * c2 + 3 * c3 * u), 2 * c2 + 6 * c3 * u)

    def ff1(self, x):
        """arb f(x), f'(x) at rational x in (0, 1]."""
        P, P1, _ = self.Pd(self.idx(x), x)
        X = arb(x); L1 = (1 + X).log(); Lx = X.log(); E = (-X).exp()
        return (1 + X) * L1 - X * Lx + X * E * arb(P), L1 - Lx + E * arb((1 - x) * P + x * P1)

    def psi(self, x):
        f, f1 = self.ff1(x)
        return f - arb(x) * f1

    def f12_cell(self, i, s1, s2):
        Sb = ball(s1, s2)
        P, P1, P2 = self.Pd(i, Sb)
        E = (-Sb).exp()
        f1 = (1 + Sb).log() - Sb.log() + E * ((1 - Sb) * P + Sb * P1)
        f2 = -1 / (Sb * (1 + Sb)) + E * ((Sb - 2) * P + (2 - 2 * Sb) * P1 + Sb * P2)
        return f1, f2


class Tangency:
    def __init__(self, S):
        self.S = S
        f1, d1 = S.ff1(fmpq(1))
        self.f1, self.d1 = f1, d1
        need(d1 > 0, "f'(1) > 0")
        need(2 * d1 - f1 > 0, "2 f'(1) > f(1)")
        self.r1 = f1 - d1

    def _bisect(self, F, A, decreasing, width):
        """rational bracket [lo, hi] in (0, 1] of the root of F(x) = A (F monotone), by bisection on rationals."""
        lo, hi = fmpq(0), fmpq(1)
        # move lo off 0 geometrically: need a certified side at lo
        x = fmpq(1, 2)
        while True:
            v = F(x)
            side_lo = (v > A) if decreasing else (v < A)
            side_hi = (v < A) if decreasing else (v > A)
            if side_lo:
                lo = x; break
            if side_hi:                                   # hi moves only to a point with a CERTIFIED opposite sign
                hi = x
            x = x / 2 ** 8
            need(x > fmpq(1, 10 ** 300), 'bracket below 1e-300')
        while hi - lo > width * lo:
            mid = (lo + hi) / 2
            v = F(mid)
            if (v > A) if decreasing else (v < A): lo = mid
            elif (v < A) if decreasing else (v > A): hi = mid
            else:
                break                                   # sign undecided: the root is within the enclosure; keep [lo, hi]
        return lo, hi

    def bracket(self, A):
        """returns (kind, lo, hi, b_lo, b_hi): lambda* in [L, U] and b(A) in [b_lo, b_hi] (arb lower/upper)."""
        Aa = arb(A)
        W = fmpq(1, 2 ** 45)
        if self.d1 < Aa:                                  # left: f'(t) = A, f' decreasing
            lo, hi = self._bisect(lambda x: self.S.ff1(x)[1], Aa, True, W)
            b = self.S.psi(lo).union(self.S.psi(hi))     # psi increasing in t
            return lo, hi, b
        if Aa < self.r1:                                  # right: psi(u) = A, psi increasing; lambda = 1/u
            lo, hi = self._bisect(self.S.psi, Aa, False, W)
            b = self.S.ff1(lo)[1].union(self.S.ff1(hi)[1])   # f' decreasing in u
            return 1 / hi, 1 / lo, b
        if self.r1 < Aa and Aa < self.d1:                 # corner
            return fmpq(1), fmpq(1), self.f1 - Aa
        # undecided near a branch boundary: lambda* near 1; enclose b by the corner value and both one-sided cases
        lo_l, hi_l = self._bisect(lambda x: self.S.ff1(x)[1], Aa, True, W) if not (Aa < self.d1) else (fmpq(1), fmpq(1))
        lo_r, hi_r = self._bisect(self.S.psi, Aa, False, W) if not (self.r1 < Aa) else (fmpq(1), fmpq(1))
        L = min(lo_l, 1 / hi_r); U = max(hi_l, 1 / lo_r)
        b = (self.f1 - Aa).union(self.S.psi(lo_l)).union(self.S.ff1(lo_r)[1])
        return L, U, b


def certify(S, T, i, s1, s2, r, w, depth, st):
    st['n'] += 1
    m = (s1 + s2) / 2
    need(r * s2 < 1, 'mu < 1')
    f, f1 = S.ff1(m)
    p0 = 1 - (-f1).exp()
    need(p0 > 0 and p0 < 1, 'p0 in (0,1)')
    mu = arb(r * m)
    lX = arb(w) * (1 - mu).log() + p0.log() / (1 - mu)
    A = -lX
    _, _, b_m = T.bracket(lowq(A))               # b decreasing in A: b(A) <= b(lower end of A)
    need(b_m > 0, 'b > 0')
    Dm = arb(w + 1) * f + lX - arb(m) * b_m.upper() + arb(w * m) * mu.log() - arb(TAU * m)
    # derivative over the cell
    f1S, f2S = S.f12_cell(i, s1, s2)
    Sb = ball(s1, s2); Mu = arb(r) * Sb
    E = (-f1S).exp(); P0 = 1 - E
    need(P0 > 0, 'p0 > 0 on the cell')
    om = 1 - Mu
    LXS = arb(w) * om.log() + P0.log() / om
    AS = -LXS
    A_lo, A_hi = lowq(AS), upq(AS)
    need(A_lo > 0, 'A > 0')
    L1, U1, b_hi_end = T.bracket(A_hi)                    # lambda*, b at the large-A end (small lambda*, small b)
    L2, U2, b_lo_end = T.bracket(A_lo)
    Lam = ball(L1, U2)
    Bc = b_hi_end.union(b_lo_end)
    lp = -arb(w * r) / om + (E * f2S / P0) / om + arb(r) * P0.log() / (om * om)
    dD = arb(w + 1) * f1S + lp * (1 - Sb * Lam) - Bc + arb(w) * Mu.log() + w - arb(TAU)
    bound = Dm - abs(dD) * arb((s2 - s1) / 2)
    if bound > 0:
        q = Dm.lower() / arb(m)
        if st['min'] is None or q.mid() < st['min'][0].mid():
            st['min'] = (q, m)
        return True
    need(depth < 60, 'cell [%s, %s] not certified' % (s1, s2))
    return certify(S, T, i, s1, m, r, w, depth + 1, st) and certify(S, T, i, m, s2, r, w, depth + 1, st)


def parse_opts(args, known):
    """strict options: only --key=value with a known key, each at most once; anything else is refused (audit S-1)."""
    opts = {}
    for a in args:
        if not a.startswith('--') or '=' not in a:
            raise SystemExit('refusing malformed option %r (use --key=value)' % a)
        k, v = a.split('=', 1)
        if k not in known:
            raise SystemExit('refusing unknown option %r (known: %s)' % (k, ', '.join(sorted(known))))
        if k in opts:
            raise SystemExit('option %s given twice' % k)
        opts[k] = v
    return opts


def main(argv):
    src, cellsp, outp = argv[:3]
    opts = parse_opts(argv[3:], {'--alpha', '--from', '--to', '--require', '--partial'})
    alpha = Q(opts.get('--alpha', '1/10000000000000000'))
    global TAU
    TAU = Q(opts.get('--require', '0'))
    t0 = time.time()
    S = Source(src); T = Tangency(S)
    need(sha(cellsp) == CELLS_SHA, 'source_cells.json pin')
    lw = json.load(open(cellsp))
    lefts = [Q(c['left']) for c in lw]; ctl = [(Q(c['r']), Q(c['w'])) for c in lw]
    need(all(r > 0 and w > 0 for r, w in ctl), 'controls positive')

    def controls(x):
        lo, hi = 0, len(lefts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if lefts[mid] <= x: lo = mid
            else: hi = mid - 1
        return ctl[lo]
    # own cell list (independent of program A's): geometric with ratio 1 + 2^-11 below 1/8, pieces above,
    # always split at Hermite nodes; geometric points rounded to multiples of 2^-(k+60) near x = 2^-k
    work = []
    ratio = fmpq(2049, 2048)
    for i in range(2279):
        a, b = S.t[i], S.t[i + 1]
        if b <= alpha:
            continue
        x = a if a > alpha else alpha
        while x < b:
            if x < fmpq(1, 8):
                y = x * ratio
                if y < b:
                    den = 2 ** 60
                    while fmpq(1, den) > y / 2 ** 40:
                        den *= 2 ** 20
                    y = fmpq((y.p * den) // y.q + 1, den)
                    if not (x < y < b):
                        y = b
                else:
                    y = b
            else:
                y = b
            work.append((i, x, y)); x = y
    N = len(work)
    i0 = int(opts.get('--from', 0)); i1 = int(opts.get('--to', N))
    if not (0 <= i0 < i1 <= N):
        raise SystemExit('refusing the empty or out-of-range cell range %d..%d of %d' % (i0, i1, N))
    full = (i0 == 0 and i1 == N)
    if not full and opts.get('--partial') != 'yes':
        raise SystemExit('cells %d..%d is only part of the %d cells; pass --partial=yes to run a partial range' % (i0, i1, N))
    st = {'n': 0, 'min': None}
    ok, why = True, None
    try:
        for k, (i, x, y) in enumerate(work[i0:i1]):
            r, w = controls((x + y) / 2)
            certify(S, T, i, x, y, r, w, 0, st)
            if (k + 1) % 5000 == 0:
                print('%d/%d cells, %d evaluations, %.0f s' % (k + 1, i1 - i0, st['n'], time.time() - t0), flush=True)
    except Refuse as e:
        ok, why = False, str(e)
    res = {'program': 'source_B', 'alpha': str(alpha), 'require_tau': str(TAU), 'cells_total': N, 'cells': [i0, i1], 'full_range': full, 'ok': ok,
           'why': why, 'evaluations': st['n'],
           'min_Delta_over_s': st['min'][0].str(6) if st['min'] else None, 'argmin': str(st['min'][1]) if st['min'] else None,
           'seconds': round(time.time() - t0, 1)}
    json.dump(res, open(outp, 'w'))
    print('SOURCE B: %s; cells %d..%d of %d; %d evaluations; min Delta/s %s' % (
        ('ALL CELLS CERTIFIED' if full else 'ALL CELLS OF THE PARTIAL RANGE CERTIFIED (not a full certificate)') if ok
        else 'REFUSED: %s' % why, i0, i1, len(work), st['n'],
        st['min'][0].str(5, radius=False) if st['min'] else '-'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
