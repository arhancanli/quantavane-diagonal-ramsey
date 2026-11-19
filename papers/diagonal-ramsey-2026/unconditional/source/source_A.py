"""Program A for Lu-Wang's source certificate (UNCONDITIONAL_PLAN item L4), written from their Appendix B text.

What is certified, for Lu-Wang's f (data/source.json, SHA-256 pinned) on [ALPHA, 1]:
  (S0) f(0) = 0 (by the formula), f'(1) > 0 and 2 f'(1) > f(1), and (S0') f is C^1 on (0, 1] with f'' < 0 on every
       Hermite piece (certified here, independently of lines_B.py of stage 2a), so f-hat is concave on (0, infinity);
  (S1) for every s in [ALPHA, 1], with controls (r, w) rational (Lu-Wang's per-cell values used as data), mu = r s,
       p0 = 1 - e^{-f'(s)}, X = (1 - mu)^w p0^{1/(1 - mu)}, A = -log X and Y = e^{-b(A)} where
       b(A) = sup_{lambda > 0} (f-hat(lambda) - A lambda)  (so (X, Y) is in B_f: f-hat(lambda) <= A lambda + b(A)),
       the inequality (31):  Delta(s) := (w + 1) f(s) + log X + s log Y + w s log mu > 0,
       together with 0 < mu < 1 and 0 < p0 < 1 and b > 0 (so X, Y, mu are in (0, 1)).
This is the hypothesis of Lu-Wang's Lemma B.1 on [ALPHA, 1]; Lemma B.1's proof needs it only for s >= alpha with
h(alpha) < eps/2 (ES handles s <= alpha), where eps is the one fixed margin used by ZBS's Theorem 5.7.

Method (per cell [s1, s2] inside one Hermite piece, controls constant on the cell):
  Delta(s) >= Delta(m) - sup_{cell} |Delta'| (s2 - s1)/2,  m the midpoint, with (b'(A) = -lambda*(A), Danskin)
  Delta'(s) = (w+1) f'(s) + l'(s) (1 - s lambda*) - b(A(s)) + w log(r s) + w,   l = log X,
  l'(s) = -w r/(1 - mu) + (e^{-f'} f''/p0)/(1 - mu) + r log(p0)/(1 - mu)^2.
  lambda*(A) (the maximiser; f-hat strictly concave) is bracketed by certified sign changes of the decreasing function
  f-hat'(lambda) - A, with the reflected parameter t' = 1/lambda on lambda > 1 (f-hat'(lambda) = f(t') - t' f'(t')).
  b(A) <= phi(l0) + max over the bracket of phi'(l0)(lambda - l0) (phi = f-hat - A lambda concave), b(A) >= phi(l0).
  Cells are bisected (depth <= 60) until the bound is > 0.
Arithmetic: exact Fractions and the lab's own dyadic intervals (ivA.py, 256 bits, pinned). Floats are used ONLY to
propose bracket points; every bracket is accepted only after exact interval sign checks.
usage: python3 -I source_A.py <source.json> <source_cells.json> <out.json> [--alpha=p/q] [--from=i --to=j --partial=yes]
       [--require=p/q] (margin probe: certify Delta(s) > (p/q) s instead of Delta(s) > 0)"""
if not __debug__:
    raise SystemExit('refusing to run under python -O')
import sys, os, json, hashlib, time, math, bisect
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
IVA_DIR = os.path.join(REPO, 'research', 'tier2', 'ramsey-zbs', 'code', 'checkA')
IVA_SHA = 'f6fe4408e2899fcfb39eab8ec2a4cba6f05ef6c2ba6855b97644a252b4579ee8'
SRC_SHA = 'f3e4a4eaf3f778ae125466eb6d47647a38fd38430fdcdffe8c5f774f9718c08c'
CELLS_SHA = '055d86954ba7bc4e636ded1c0bb603a142ca738174e79a997f17b0c51c524bff'


def sha(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


assert sha(os.path.join(IVA_DIR, 'ivA.py')) == IVA_SHA
sys.path.insert(0, IVA_DIR)
import ivA
from ivA import Iv
ONE = ivA.ONE
TAU = Fr(0)        # margin probe: certify Delta(s) - TAU s > 0 (0 for the claim itself)


def rng(x1, x2):
    return Iv(Iv.q(x1).lo, Iv.q(x2).hi)


def up(iv):
    return max(-iv.lo, iv.hi)


def lof(iv):
    return Fr(iv.lo, ONE)


def hif(iv):
    return Fr(iv.hi, ONE)


class Piece:
    __slots__ = ('a', 'b', 'k', 'kf')

    def __init__(self, a, b, Pa, Pb, Da, Db):
        d = b - a; D = (Pb - Pa) / d
        self.a, self.b = a, b
        self.k = (Pa, Da, (3 * D - 2 * Da - Db) / d, (Da + Db - 2 * D) / (d * d))
        self.kf = tuple(float(x) for x in self.k)

    def P(self, t):
        c0, c1, c2, c3 = self.k; u = t - self.a
        return (c0 + u * (c1 + u * (c2 + u * c3)), c1 + u * (2 * c2 + 3 * c3 * u), 2 * c2 + 6 * c3 * u)

    def P_iv(self, t1, t2):
        U = rng(t1 - self.a, t2 - self.a)
        c0, c1, c2, c3 = (Iv.q(x) for x in self.k)
        return (c0 + U * (c1 + U * (c2 + U * c3)), c1 + U * (Iv.q(2) * c2 + Iv.q(3) * c3 * U), Iv.q(2) * c2 + Iv.q(6) * c3 * U)

    def Pf(self, t):
        c0, c1, c2, c3 = self.kf; u = t - float(self.a)
        return c0 + u * (c1 + u * (c2 + u * c3)), c1 + u * (2 * c2 + 3 * c3 * u), 2 * c2 + 6 * c3 * u


class Src:
    def __init__(self, path):
        assert sha(path) == SRC_SHA, 'source.json is not the pinned Lu-Wang file'
        d = json.load(open(path))
        t = [Fr(x) for x in d['nodes']]; v = [Fr(x) for x in d['values']]; dv = [Fr(x) for x in d['derivatives']]
        assert len(t) == 2280 and t[0] == 0 and t[-1] == 1 and all(t[i] < t[i + 1] for i in range(2279))
        self.t = t; self.tf = [float(x) for x in t]
        self.p = [Piece(t[i], t[i + 1], v[i], v[i + 1], dv[i], dv[i + 1]) for i in range(2279)]
        self.cache = {}

    def piece(self, x):
        i = bisect.bisect_right(self.t, x) - 1
        return self.p[min(max(i, 0), 2278)]

    # exact-interval point values
    def ff1(self, x):
        """(f(x), f'(x)) enclosures at a rational 0 < x <= 1."""
        if x in self.cache:
            return self.cache[x]
        P, P1, _ = self.piece(x).P(x)
        L1 = ivA.log(1 + x); Lx = ivA.log(x); E = ivA.exp(-x)
        f = Iv.q(1 + x) * L1 - Iv.q(x) * Lx + Iv.q(x) * E * Iv.q(P)
        f1 = L1 - Lx + E * Iv.q((1 - x) * P + x * P1)
        if len(self.cache) > 200000:
            self.cache.clear()
        self.cache[x] = (f, f1)
        return f, f1

    def f12_iv(self, pc, s1, s2):
        """enclosures of f', f'' over [s1, s2] inside piece pc (0 < s1)."""
        S = rng(s1, s2)
        P, P1, P2 = pc.P_iv(s1, s2)
        E = ivA.exp(-S)
        f1 = ivA.log(Iv.q(1) + S) - ivA.log(S) + E * ((Iv.q(1) - S) * P + S * P1)
        f2 = Iv.q(1) / (Iv.q(1) + S) - Iv.q(1) / S + E * ((S - Iv.q(2)) * P + (Iv.q(2) - Iv.q(2) * S) * P1 + S * P2)
        return f1, f2

    # floats, only to propose points
    def f1_float(self, x):
        P, P1, _ = self.piece_f(x).Pf(x)
        return math.log1p(x) - math.log(x) + math.exp(-x) * ((1 - x) * P + x * P1)

    def f_float(self, x):
        P, _, _ = self.piece_f(x).Pf(x)
        return (1 + x) * math.log1p(x) - x * math.log(x) + x * math.exp(-x) * P

    def f2_float(self, x):
        P, P1, P2 = self.piece_f(x).Pf(x)
        return -1 / (x * (1 + x)) + math.exp(-x) * ((x - 2) * P + (2 - 2 * x) * P1 + x * P2)

    def piece_f(self, x):
        i = bisect.bisect_right(self.tf, x) - 1
        return self.p[min(max(i, 0), 2278)]


class Conj:
    """the conjugate b(A) = sup_lambda (f-hat(lambda) - A lambda) of the concave f-hat, with certified brackets."""
    def __init__(self, S):
        self.S = S
        f1v, f1d = S.ff1(Fr(1))
        self.f1 = f1v; self.fp1 = f1d                    # f(1), f'(1)
        self.right1 = f1v - f1d                          # right derivative of f-hat at 1: f(1) - f'(1)
        assert f1d.lo > 0, "f'(1) > 0"
        assert (Iv.q(2) * f1d - f1v).lo > 0, "2 f'(1) > f(1) (concavity of f-hat across 1)"
        self.fp1f = float(hif(f1d)); self.r1f = float(hif(self.right1))

    def psi(self, t):
        """f-hat'(1/t) = f(t) - t f'(t) for 0 < t <= 1 (enclosure)."""
        f, f1 = self.S.ff1(t)
        return f - Iv.q(t) * f1

    def _float_root(self, F, Fp, lo, hi, target, increasing):
        x = math.sqrt(lo * hi) if lo > 0 else hi / 2
        for _ in range(200):                             # safeguarded Newton in floats (proposal only)
            v = F(x) - target
            if (v > 0) == increasing: hi = x
            else: lo = x
            d = Fp(x)
            xn = x - v / d if d != 0 else None
            if xn is None or not (lo < xn < hi):
                xn = math.sqrt(lo * hi) if lo > 0 and hi / lo > 4 else (lo + hi) / 2
            if abs(xn - x) <= 1e-17 * abs(x):
                x = xn; break
            x = xn
        return x

    def bracket(self, A):
        """certified enclosure [L, U] (Fractions) of lambda*(A), A > 0 rational."""
        S = self.S
        Ai = Iv.q(A)
        if self.fp1.hi < Ai.lo:                          # left branch: f'(t) = A, t in (0, 1)
            x = self._float_root(S.f1_float, S.f2_float, 1e-300, 1.0, float(A), increasing=False)
            rel = Fr(1, 10 ** 13)
            for _ in range(12):
                xq = Fr(x).limit_denominator(10 ** 30)
                tl = max(xq * (1 - rel), Fr(1, 10 ** 300)); tu = min(xq * (1 + rel), Fr(1))
                okl = S.ff1(tl)[1].lo > Ai.hi
                oku = tu == 1 or S.ff1(tu)[1].hi < Ai.lo
                if okl and oku:
                    return tl, tu
                rel *= 100
            raise ArithmeticError('left bracket failed at A = %s' % A)
        if Ai.hi < self.right1.lo:                       # right branch: psi(t') = A, lambda = 1/t'
            Ff = lambda t: S.f_float(t) - t * S.f1_float(t)
            Fpf = lambda t: -t * S.f2_float(t)
            x = self._float_root(Ff, Fpf, 1e-300, 1.0, float(A), increasing=True)
            rel = Fr(1, 10 ** 13)
            for _ in range(12):
                xq = Fr(x).limit_denominator(10 ** 30)
                tl = max(xq * (1 - rel), Fr(1, 10 ** 300)); tu = min(xq * (1 + rel), Fr(1))
                okl = self.psi(tl).hi < Ai.lo
                oku = tu == 1 or self.psi(tu).lo > Ai.hi
                if okl and oku:
                    return 1 / tu, 1 / tl
                rel *= 100
            raise ArithmeticError('right bracket failed at A = %s' % A)
        if self.right1.hi < Ai.lo and Ai.hi < self.fp1.lo:   # corner: lambda* = 1
            return Fr(1), Fr(1)
        # A within an enclosure of f'(1) or f(1) - f'(1): bracket around 1
        lo, hi = Fr(1), Fr(1)
        if not (Ai.hi < self.fp1.lo):                    # lambda* <= 1: find t < 1 with f'(t) > A
            d = Fr(1, 10 ** 20)
            while not (S.ff1(1 - d)[1].lo > Ai.hi):
                d *= 10
            lo = 1 - d
        if not (self.right1.hi < Ai.lo):                 # lambda* >= 1: find t' < 1 with psi(t') < A
            d = Fr(1, 10 ** 20)
            while not (self.psi(1 - d).hi < Ai.lo):
                d *= 10
            hi = 1 / (1 - d)
        return lo, hi

    def fhat(self, lam):
        """enclosures of f-hat(lam), f-hat'(lam) at a rational lam > 0 (lam != 1 uses the smooth branch)."""
        if lam <= 1:
            return self.S.ff1(lam)
        t = 1 / lam
        f, f1 = self.S.ff1(t)
        return Iv.q(lam) * f, f - Iv.q(t) * f1

    def b_bounds(self, A):
        """(lower, upper) Fractions with lower <= b(A) <= upper; also returns the bracket of lambda*."""
        L, U = self.bracket(A)
        if L == U:                                       # corner, exactly lambda* = 1
            v = self.f1 - Iv.q(A)
            return lof(v), hif(v), (L, U)
        l0 = (L + U) / 2
        if L < 1 < U:
            # unreachable: it would need A inside the enclosures of both f'(1) and f(1) - f'(1), which are disjoint
            raise ArithmeticError('bracket straddles 1 at A = %s' % A)
        fv, fd = self.fhat(l0)
        phi = fv - Iv.q(A * l0)
        g = fd - Iv.q(A)
        ext = max((g * Iv.q(L - l0)).hi, (g * Iv.q(U - l0)).hi, 0)
        return lof(phi), hif(phi) + Fr(ext, ONE), (L, U)


def certify_f_concave_C1(S):
    """(S0') f is C^1 on (0, 1] (exact Hermite identities at every node) and f'' < 0 on every piece (ivA intervals with
    bisection; on the first piece (0, t1] it suffices that sup j'' < 1/(t1 (1 + t1)), as -1/(t(1+t)) <= -1/(t1(1+t1)))."""
    for i, pc in enumerate(S.p[:-1]):
        nxt = S.p[i + 1]
        Pb, P1b, _ = pc.P(pc.b)
        assert Pb == nxt.k[0] and P1b == nxt.k[1], 'Hermite C^1 identity at node %d' % (i + 1)
    nsub = 0

    def neg_f2(pc, lo, hi, depth):
        nonlocal nsub
        if lo == 0:
            S_ = rng(Fr(0), hi)
            P, P1, P2 = pc.P_iv(Fr(0), hi)
            j2 = ivA.exp(-S_) * ((S_ - Iv.q(2)) * P + (Iv.q(2) - Iv.q(2) * S_) * P1 + S_ * P2)
            ok = j2.hi < Iv.q(Fr(1) / (hi * (1 + hi))).lo
        else:
            f1, f2 = S.f12_iv(pc, lo, hi)
            ok = f2.hi < 0
        if ok:
            nsub += 1
            return True
        assert depth < 30, "f'' < 0 not certified on [%s, %s]" % (lo, hi)
        mid = (lo + hi) / 2
        return neg_f2(pc, lo, mid, depth + 1) and neg_f2(pc, mid, hi, depth + 1)
    for pc in S.p:
        neg_f2(pc, pc.a, pc.b, 0)
    return nsub


def certify_cell(S, C, pc, s1, s2, r, w, depth, st):
    st['evals'] += 1
    m = (s1 + s2) / 2
    mu_m = r * m
    assert 0 < r * s2 < 1, 'mu in (0, 1)'
    f, f1 = S.ff1(m)
    p0 = Iv.q(1) - ivA.exp(-f1)
    assert p0.lo > 0 and p0.hi < ONE, 'p0 in (0, 1)'
    lX = Iv.q(w) * ivA.log(Iv.q(1 - mu_m)) + ivA.log(p0) / Iv.q(1 - mu_m)
    A_m = -lX
    bl, bu, _ = C.b_bounds(lof(A_m))                    # b decreasing: b(A) <= b(lower end of A)
    assert bl > 0, 'b > 0'
    Dm = Iv.q(w + 1) * f + lX - Iv.q(m * bu) + Iv.q(w * m) * ivA.log(Iv.q(mu_m)) - Iv.q(TAU * m)
    # derivative enclosure over the cell
    f1S, f2S = S.f12_iv(pc, s1, s2)
    Sv = rng(s1, s2); Mu = Iv.q(r) * Sv
    E = ivA.exp(-f1S); P0 = Iv.q(1) - E
    assert P0.lo > 0, 'p0 > 0 on the cell'
    one_mu = Iv.q(1) - Mu
    LX = Iv.q(w) * ivA.log(one_mu) + ivA.log(P0) / one_mu
    AS = -LX
    A_lo, A_hi = lof(AS), hif(AS)
    assert A_lo > 0, 'A > 0'
    bl_hi, _, (Lh, Uh) = C.b_bounds(A_hi)                # b(A_hi) lower bound -> lower end of b on the cell
    _, bu_lo, (Ll, Ul) = C.b_bounds(A_lo)                # b(A_lo) upper bound -> upper end
    Lam = Iv(Iv.q(Lh).lo, Iv.q(Ul).hi)                   # lambda* decreasing in A
    Bc = Iv(Iv.q(bl_hi).lo, Iv.q(bu_lo).hi)
    lp = (-Iv.q(w * r)) / one_mu + (E * f2S / P0) / one_mu + Iv.q(r) * ivA.log(P0) / (one_mu * one_mu)
    dD = Iv.q(w + 1) * f1S + lp * (Iv.q(1) - Sv * Lam) - Bc + Iv.q(w) * ivA.log(Mu) + Iv.q(w) - Iv.q(TAU)
    lb = Dm.lo - (Iv(up(dD)) * Iv.q((s2 - s1) / 2)).hi
    if lb > 0:
        q = Fr(Dm.lo, ONE) / m
        if st['min'] is None or q < st['min'][0]:
            st['min'] = (q, m)
        return True
    if depth >= 60:
        st['fail'] = (str(s1), str(s2))
        return False
    return (certify_cell(S, C, pc, s1, m, r, w, depth + 1, st) and certify_cell(S, C, pc, m, s2, r, w, depth + 1, st))


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
    alpha = Fr(opts.get('--alpha', '1/10000000000000000'))
    global TAU
    TAU = Fr(opts.get('--require', '0'))
    t0 = time.time()
    S = Src(src)
    nconc = certify_f_concave_C1(S)
    print("f is C^1 on (0, 1]; f'' < 0 certified on every piece (%d sub-intervals)" % nconc, flush=True)
    C = Conj(S)
    assert sha(cellsp) == CELLS_SHA, 'source_cells.json is not the pinned Lu-Wang file'
    lw = json.load(open(cellsp))
    lw_left = [Fr(c['left']) for c in lw]
    ctl = [(Fr(c['r']), Fr(c['w'])) for c in lw]
    assert all(r > 0 and w > 0 for r, w in ctl)

    def controls(x):
        return ctl[min(max(bisect.bisect_right(lw_left, x) - 1, 0), len(ctl) - 1)]
    # cells: every Hermite piece meeting [alpha, 1]; below 1/8 also split geometrically (ratio 1 + 2^-11), so that
    # the cell's relative width is small enough for the mean-value bound near 0 (cells end at Hermite nodes)
    work = []
    ratio = 1 + Fr(1, 2048)
    for pc in S.p:
        a, b = max(pc.a, alpha), pc.b
        if b <= alpha:
            continue
        x = a
        while x < b:
            y = min(b, x * ratio) if x < Fr(1, 8) else b
            if y < b:
                y = Fr(y).limit_denominator(10 ** 40)
                if not (x < y < b):
                    y = b
            work.append((pc, x, y)); x = y
    N = len(work)
    i0 = int(opts.get('--from', 0)); i1 = int(opts.get('--to', N))
    if not (0 <= i0 < i1 <= N):
        raise SystemExit('refusing the empty or out-of-range cell range %d..%d of %d' % (i0, i1, N))
    full = (i0 == 0 and i1 == N)
    if not full and opts.get('--partial') != 'yes':
        raise SystemExit('cells %d..%d is only part of the %d cells; pass --partial=yes to run a partial range' % (i0, i1, N))
    st = {'evals': 0, 'min': None}
    ok = True; done = 0
    for pc, x, y in work[i0:i1]:
        r, w = controls((x + y) / 2)
        if not certify_cell(S, C, pc, x, y, r, w, 0, st):
            ok = False; break
        done += 1
        if done % 500 == 0:
            print('%d/%d cells, %d evaluations, %.0f s' % (done, i1 - i0, st['evals'], time.time() - t0), flush=True)
    res = {'program': 'source_A', 'concavity_subintervals': nconc, 'alpha': str(alpha), 'require_tau': str(TAU), 'cells_total': N, 'cells': [i0, i1], 'full_range': full, 'ok': ok, 'evals': st['evals'],
           'min_Delta_over_s': str(st['min'][0]) if st['min'] else None, 'argmin': str(st['min'][1]) if st['min'] else None,
           'fail': st.get('fail'), 'seconds': round(time.time() - t0, 1)}
    json.dump(res, open(outp, 'w'))
    print('SOURCE A: %s; cells %d..%d of %d; %d evaluations; min Delta/s %s' % (
        ('ALL CELLS CERTIFIED' if full else 'ALL CELLS OF THE PARTIAL RANGE CERTIFIED (not a full certificate)') if ok
        else 'NOT CERTIFIED at %s' % (st.get('fail'),), i0, i1, N, st['evals'],
        '%.4e' % float(st['min'][0]) if st['min'] else '-'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
