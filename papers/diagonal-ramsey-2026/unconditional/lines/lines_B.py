"""Program B for the 1,128 lines (UNCONDITIONAL_PLAN item Z14), written separately from lines_A.py.
Claim, for every line (c, d) of ZBS's theorem lu_wang_lines_P0r12: f-hat(lambda) <= c + d lambda for all lambda > 0,
equivalently (t = lambda or t = 1/lambda) for all t in (0, 1]:  (O1) f(t) <= c + d t,  (O2) f(t) <= d + c t,
with Lu-Wang's f(t) = (1+t) log(1+t) - t log t + t e^{-t} P(t), P the cubic Hermite interpolant of data/source.json.
Method (different from program A):
  (1) Hermite data: on every piece the cubic built from (P_a, P'_a, P_b, P'_b) reproduces P_b and P'_b exactly
      (checked in exact rationals), so P is C^1 and f is C^1 on (0, 1] and continuous on [0, 1] with f(0) = 0.
  (2) Concavity: f'' = -1/(t(1+t)) + j''(t), j'' = e^{-t}((t-2)P + (2-2t)P' + tP''), is certified < 0 on every piece
      by Arb ball arithmetic with bisection; on the first piece (0, b] it suffices that sup j'' < 1/(b(1+b)).
      Hence f is concave on [0, 1] and, for a line L, g = L - f is convex on [0, 1].
  (3) Per line and orientation (alpha + beta t): a point m is located by bisection of the sign of f'(t) - beta (m = 1
      if f'(1) >= beta), and the convex tangent bound g(t) >= g(m) + g'(m)(t - m) for all t in [0, 1] is certified
      >= 0 at both ends t = 0 and t = 1 of [0, 1] (an affine function is smallest at an end).
The list of lines is read from ZBS's Lean file Bridge/P06LinesP0r12.lean @ c2875f33 (not from our parse), pinned by
SHA-256. Arithmetic: python-flint 0.9.0 (pinned) Arb balls at 400 bits and fmpq rationals; no floating point enters
any decision.
usage: <flint-python> -I lines_B.py <source.json> <P06LinesP0r12.lean> <out.json> [--lines=i,j] [--tamper=i:o:delta,...]"""
import sys, os, re, json, hashlib, time
import flint
from flint import arb, fmpq

if flint.__version__ != '0.9.0':
    raise SystemExit('pinned to python-flint 0.9.0')
flint.ctx.prec = 400
SRC_SHA = 'f3e4a4eaf3f778ae125466eb6d47647a38fd38430fdcdffe8c5f774f9718c08c'
LEAN_SHA = 'aeac27eba632215b908461f7ee42c886ff4d14bd5b5b6ad5cd5b5a0d9d4556ba'


class Refuse(Exception):
    pass


def need(ok, why):
    if not ok:
        raise Refuse(why)


def sha(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def Q(s):
    s = str(s).strip()
    if '/' in s:
        n, d = s.split('/')
        return fmpq(int(n), int(d))
    return fmpq(int(s))


def read_lines(path):
    need(sha(path) == LEAN_SHA, 'P06LinesP0r12.lean is not the pinned ZBS file')
    s = open(path, encoding='utf-8').read()
    i = s.index('theorem lu_wang_lines_P0r12')
    body = s[i:s.index('] : List', i)]
    pairs = re.findall(r'\(\((-?\d+)/(\d+) : ℚ\), \((-?\d+)/(\d+) : ℚ\)\)', body)
    need(len(pairs) == 1128, 'expected 1,128 lines, found %d' % len(pairs))
    # the statement proved for each p in the list:
    stmt = s[i:s.index(':=', i)]                     # the statement of lu_wang_lines_P0r12 itself (audit L-3)
    need('∀ s : ℝ, 0 < s → symmetricProfile luWangSource 1 s ≤ (p.1 : ℝ) + (p.2 : ℝ) * s' in stmt, 'statement form')
    return [(fmpq(int(a), int(b)), fmpq(int(c), int(d))) for a, b, c, d in pairs]


class Piece:
    def __init__(self, a, b, Pa, Pb, Da, Db):
        d = b - a; D = (Pb - Pa) / d
        self.a, self.b = a, b
        self.k = [Pa, Da, (3 * D - 2 * Da - Db) / d, (Da + Db - 2 * D) / (d * d)]
        k = self.k
        need(k[0] + d * (k[1] + d * (k[2] + d * k[3])) == Pb, 'Hermite value at the right end')
        need(k[1] + d * (2 * k[2] + 3 * k[3] * d) == Db, 'Hermite derivative at the right end')

    def P(self, x):
        """P, P', P'' at x (fmpq or arb)."""
        k = self.k; u = x - self.a
        return (k[0] + u * (k[1] + u * (k[2] + u * k[3])), k[1] + u * (2 * k[2] + 3 * k[3] * u), 2 * k[2] + 6 * k[3] * u)


def load(path):
    need(sha(path) == SRC_SHA, 'source.json is not the pinned Lu-Wang file')
    d = json.load(open(path))
    t = [Q(x) for x in d['nodes']]; v = [Q(x) for x in d['values']]; dv = [Q(x) for x in d['derivatives']]
    need(len(t) == 2280 and t[0] == 0 and t[-1] == 1, 'nodes 0 .. 1')
    need(all(t[i] < t[i + 1] for i in range(len(t) - 1)), 'nodes increase')
    return t, [Piece(t[i], t[i + 1], v[i], v[i + 1], dv[i], dv[i + 1]) for i in range(len(t) - 1)]


def ball(lo, hi):
    """an arb ball containing [lo, hi] (fmpq)."""
    return arb(lo).union(arb(hi))


def j2(pc, T):
    P, P1, P2 = pc.P(T)
    return (-T).exp() * ((T - 2) * P + (2 - 2 * T) * P1 + T * P2)


def concave_piece(pc, lo, hi, depth=0):
    """certify f'' < 0 on [lo, hi] (0 < lo) or on (0, hi] if lo == 0."""
    T = ball(lo, hi)
    if lo == 0:
        ok = j2(pc, T) < arb(1) / (arb(hi) * (1 + arb(hi)))
    else:
        ok = (-1 / (T * (1 + T)) + j2(pc, T)) < 0
    if ok:
        return 1
    need(depth < 30, 'concavity not certified on [%s, %s]' % (lo, hi))
    m = (lo + hi) / 2
    return concave_piece(pc, lo, m, depth + 1) + concave_piece(pc, m, hi, depth + 1)


class Fn:
    def __init__(self, nodes, pieces):
        self.t, self.p = nodes, pieces

    def piece(self, x):
        lo, hi = 0, len(self.p) - 1                     # piece i with t[i] <= x <= t[i+1]
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if self.t[mid] <= x: lo = mid
            else: hi = mid - 1
        return self.p[lo]

    def f_f1(self, x):
        """arb enclosures of f(x), f'(x) at a rational x > 0."""
        pc = self.piece(x); P, P1, _ = pc.P(x)
        X = arb(x); L1 = (1 + X).log(); Lx = X.log(); E = (-X).exp()
        f = (1 + X) * L1 - X * Lx + X * E * arb(P)
        f1 = L1 - Lx + E * arb((1 - x) * P + x * P1)
        return f, f1


def check_line(Fn_, alpha, beta, t_lo):
    """certify alpha + beta t >= f(t) on [0, 1] (f concave there); returns (ok, m, lower bound of the gap)."""
    f1_one = Fn_.f_f1(fmpq(1))[1]
    if f1_one >= arb(beta):
        m = fmpq(1)
    else:
        need(Fn_.f_f1(t_lo)[1] > arb(beta), 'start of bisection')
        lo, hi = t_lo, fmpq(1)
        for _ in range(240):
            mid = (lo + hi) / 2
            s = Fn_.f_f1(mid)[1]
            if s > arb(beta): lo = mid
            elif s < arb(beta): hi = mid
            else:
                lo = hi = mid; break
        m = (lo + hi) / 2
    f, f1 = Fn_.f_f1(m)
    g = arb(alpha + beta * m) - f
    g1 = arb(beta) - f1
    # convexity: g(t) >= g(m) + g'(m)(t - m) on [0, 1]; the affine minorant is smallest at t = 0 or t = 1
    at0 = g - g1 * arb(m)
    at1 = g + g1 * arb(1 - m)
    ok = bool(at0 >= 0) and bool(at1 >= 0)
    bound = at0 if at0.lower() < at1.lower() else at1
    return ok, m, bound


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
    src, lean, outp = argv[:3]
    opts = parse_opts(argv[3:], {'--lines', '--tamper'})
    t0 = time.time()
    nodes, pieces = load(src)
    lines = read_lines(lean)
    nleaf = sum(concave_piece(pc, pc.a, pc.b) for pc in pieces)
    print('Hermite data C^1 on %d pieces; f\'\' < 0 certified on every piece (%d sub-intervals), %.0f s'
          % (len(pieces), nleaf, time.time() - t0), flush=True)
    Fn_ = Fn(nodes, pieces)
    t_lo = nodes[1]
    tamper = {}
    for item in filter(None, opts.get('--tamper', '').split(',')):
        i, o, dl = item.split(':'); tamper[(int(i), int(o))] = Q(dl)
    sel = range(len(lines)) if '--lines' not in opts else [int(x) for x in opts['--lines'].split(',')]
    res = {'program': 'B', 'concavity_subintervals': nleaf, 'lines': {}, 'ok': True}
    worst = None
    for i in sel:
        c, d = lines[i]
        for o, (alpha, beta) in ((1, (c, d)), (2, (d, c))):
            alpha = alpha - tamper.get((i, o), fmpq(0))
            need(alpha > 0 and beta > 0, 'line %d: positive intercept and slope' % i)
            ok, m, bound = check_line(Fn_, alpha, beta, t_lo)
            low = bound.lower()
            res['lines']['%d/%d' % (i, o)] = {'ok': ok, 'm': str(m), 'gap_lower': str(low)}
            if not ok:
                res['ok'] = False
            elif worst is None or low < worst[0]:
                worst = (low, i, o)
        if (i + 1) % 100 == 0:
            print('line %d done, %.0f s' % (i, time.time() - t0), flush=True)
    res['worst'] = None if worst is None else {'gap_lower': str(worst[0]), 'line': worst[1], 'orientation': worst[2]}
    res['seconds'] = round(time.time() - t0, 1)
    json.dump(res, open(outp, 'w'), indent=0)
    nfail = sum(1 for r in res['lines'].values() if not r['ok'])
    print('PROGRAM B: %d line-orientations checked, %d failed; %s' % (len(res['lines']), nfail,
          'ALL LINES CERTIFIED' if res['ok'] else 'SOME LINE NOT CERTIFIED'))
    if worst is not None:
        print('smallest certified gap lower bound %s (line %d, orientation %d)' % (worst[0].str(5, radius=False), worst[1], worst[2]))
    return 0 if res['ok'] else 1


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except Refuse as e:
        print('PROGRAM B REFUSED: %s' % e)
        sys.exit(1)
