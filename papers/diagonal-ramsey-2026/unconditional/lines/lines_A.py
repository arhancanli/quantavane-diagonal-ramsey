"""Program A for the 1,128 lines (UNCONDITIONAL_PLAN item Z14): for every line (c, d) of ZBS's list,
    f-hat(lambda) <= c + d lambda   for ALL lambda > 0,
where f is Lu-Wang's source f(t) = (1+t) log(1+t) - t log t + t e^{-t} P(t) on [0, 1] (P the piecewise cubic Hermite
interpolant of data/source.json) and f-hat(lambda) = f(lambda) on (0, 1], lambda f(1/lambda) on [1, infinity).
Substituting t = 1/lambda on lambda >= 1, the claim is equivalent to the two statements on (0, 1]
    (O1) f(t) <= c + d t,        (O2) f(t) <= d + c t.
Method (no concavity of f is used anywhere in this program):
  * small t: for t in (0, t0] with t0 <= 1/e a node, f(t) <= t0 (1 + t0) + t0 log(1/t0) + t0 max(0, sup P on [0, t0])
    (because (1+t) log(1+t) <= (1+t) t, t log(1/t) is increasing on (0, 1/e], and t e^{-t} P <= t max(P, 0)); this is
    < alpha <= alpha + beta t (alpha, beta > 0 the line's intercept and slope in the orientation);
  * every Hermite piece [a, b] with a >= t0: second-order Taylor form at the midpoint m of [t1, t2] in the piece,
        min_{[t1,t2]} (L - f) >= (L - f)(m) - |L' - f'(m)| w/2 - sup_{[t1,t2]} |f''| w^2/8,   w = t2 - t1,
    with bisection (depth <= 90) until the bound is >= 0.
Arithmetic: exact Fractions and the lab's own outward-rounded dyadic intervals (ivA.py, 256 bits; pinned by SHA-256).
No floating point enters any decision. Inputs are pinned by SHA-256.
usage: python3 -I lines_A.py <source.json> <zbs_bank.json> <out.json> [--lines=i,j,...] [--tamper=i:o:delta,...]
  --tamper i:o:delta lowers the intercept of line i in orientation o (1 or 2) by the rational delta (red control)."""
if not __debug__:
    raise SystemExit('refusing to run under python -O')
import sys, os, json, hashlib, time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
IVA_DIR = os.path.join(REPO, 'research', 'tier2', 'ramsey-zbs', 'code', 'checkA')
IVA_SHA = 'f6fe4408e2899fcfb39eab8ec2a4cba6f05ef6c2ba6855b97644a252b4579ee8'
SRC_SHA = 'f3e4a4eaf3f778ae125466eb6d47647a38fd38430fdcdffe8c5f774f9718c08c'
ZBS_SHA = '2946c6561f562ea01a5f9b60ac0812c689af71985c60378e11c89e8cdc003bf0'


def sha(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


assert sha(os.path.join(IVA_DIR, 'ivA.py')) == IVA_SHA, 'ivA.py is not the pinned file'
sys.path.insert(0, IVA_DIR)
import ivA
from ivA import Iv

ONE = ivA.ONE
INV_E = Fr(367879441171442321, 10 ** 18)        # < 1/e (e < 2.7182818284590452...)


def rng(x1, x2):
    """enclosure of the real interval [x1, x2] (Fractions)."""
    return Iv(Iv.q(x1).lo, Iv.q(x2).hi)


def up(iv):          # an upper bound of |iv| as a nonnegative scaled int
    return max(-iv.lo, iv.hi)


class Cell:
    __slots__ = ('a', 'b', 'c0', 'c1', 'c2', 'c3')

    def __init__(self, a, b, Pa, Pb, Da, Db):
        d = b - a; D = (Pb - Pa) / d
        self.a, self.b = a, b
        self.c0, self.c1 = Pa, Da
        self.c2 = (3 * D - 2 * Da - Db) / d
        self.c3 = (Da + Db - 2 * D) / (d * d)

    def P3(self, t):
        """exact P, P', P'' at a rational t of the cell."""
        u = t - self.a
        c0, c1, c2, c3 = self.c0, self.c1, self.c2, self.c3
        return (c0 + u * (c1 + u * (c2 + u * c3)), c1 + u * (2 * c2 + 3 * c3 * u), 2 * c2 + 6 * c3 * u)

    def P3_iv(self, t1, t2):
        """interval enclosures of P, P', P'' over [t1, t2] (Horner in interval arithmetic)."""
        U = rng(t1 - self.a, t2 - self.a)
        c0, c1, c2, c3 = (Iv.q(x) for x in (self.c0, self.c1, self.c2, self.c3))
        P = c0 + U * (c1 + U * (c2 + U * c3))
        P1 = c1 + U * (Iv.q(2) * c2 + Iv.q(3) * c3 * U)
        P2 = Iv.q(2) * c2 + Iv.q(6) * c3 * U
        return P, P1, P2


def load_source(path):
    assert sha(path) == SRC_SHA, 'source.json is not the pinned Lu-Wang file'
    d = json.load(open(path))
    t = [Fr(x) for x in d['nodes']]; v = [Fr(x) for x in d['values']]; dv = [Fr(x) for x in d['derivatives']]
    assert len(t) == len(v) == len(dv) == 2280 and t[0] == 0 and t[-1] == 1
    assert all(t[i] < t[i + 1] for i in range(len(t) - 1)), 'nodes increase'
    return [Cell(t[i], t[i + 1], v[i], v[i + 1], dv[i], dv[i + 1]) for i in range(len(t) - 1)], t


class F:
    """f and its derivatives with caches."""
    def __init__(self, cells):
        self.cells = cells
        self.pt = {}; self.m2 = {}

    def at(self, cell, t):
        """(f(t), f'(t)) enclosures at a rational t > 0 of the cell."""
        key = t
        if key not in self.pt:
            P, P1, _ = cell.P3(t)
            L1 = ivA.log(1 + t); Lt = ivA.log(t); E = ivA.exp(-t)
            f = Iv.q(1 + t) * L1 - Iv.q(t) * Lt + Iv.q(t) * E * Iv.q(P)
            f1 = L1 - Lt + E * Iv.q((1 - t) * P + t * P1)
            self.pt[key] = (f, f1)
        return self.pt[key]

    def sup_f2(self, cell, t1, t2):
        """upper bound (Fraction) of |f''| on [t1, t2], 0 < t1 < t2 inside the cell."""
        key = (t1, t2)
        if key not in self.m2:
            T = rng(t1, t2)
            P, P1, P2 = cell.P3_iv(t1, t2)
            f2 = Iv.q(1) / (Iv.q(1) + T) - Iv.q(1) / T + ivA.exp(-T) * ((T - Iv.q(2)) * P + (Iv.q(2) - Iv.q(2) * T) * P1 + T * P2)
            self.m2[key] = Fr(up(f2), ONE)
        return self.m2[key]


def check_piece(Fo, cell, t1, t2, alpha, beta, depth, stats):
    """True iff alpha + beta t >= f(t) on [t1, t2] is certified (bisection)."""
    stats['evals'] += 1
    m = (t1 + t2) / 2; w = t2 - t1
    f, f1 = Fo.at(cell, m)
    g = Iv.q(alpha + beta * m) - f
    g1 = Iv.q(beta) - f1
    lb = g.lo - (Iv(up(g1)) * Iv.q(w / 2)).hi - Iv.q(Fo.sup_f2(cell, t1, t2) * w * w / 8).hi
    if lb >= 0:
        gm = Fr(g.lo, ONE)
        if stats['min_gm'] is None or gm < stats['min_gm']:
            stats['min_gm'] = gm; stats['argmin'] = m
        return True
    if depth >= 90:
        stats['fail_at'] = (str(t1), str(t2))
        return False
    return check_piece(Fo, cell, t1, m, alpha, beta, depth + 1, stats) and check_piece(Fo, cell, m, t2, alpha, beta, depth + 1, stats)


def small_t_index(nodes, pplus, alpha):
    """largest k with nodes[k] <= 1/e and the small-t bound at nodes[k] < alpha (0 if none works)."""
    def ok(k):
        t = nodes[k]
        if t == 0:
            return True
        b = Iv.q(t * (1 + t)) + Iv.q(t) * (-ivA.log(t)) + Iv.q(t * pplus[k])
        return b.hi < Iv.q(alpha).lo
    lo, hi = 0, max(k for k in range(len(nodes)) if nodes[k] <= INV_E)
    if ok(hi):
        return hi
    while hi - lo > 1:                     # ok(lo) true, ok(hi) false; the bound increases with k
        mid = (lo + hi) // 2
        if ok(mid): lo = mid
        else: hi = mid
    return lo


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
    src, zbs, outp = argv[:3]
    opts = parse_opts(argv[3:], {'--lines', '--tamper'})
    t0 = time.time()
    cells, nodes = load_source(src)
    assert sha(zbs) == ZBS_SHA, 'zbs_bank.json is not the pinned parse'
    lines = [(Fr(c), Fr(d)) for c, d in json.load(open(zbs))['lines']]
    assert len(lines) == 1128
    sel = range(len(lines)) if '--lines' not in opts else [int(x) for x in opts['--lines'].split(',')]
    tamper = {}
    for item in filter(None, opts.get('--tamper', '').split(',')):
        i, o, dl = item.split(':'); tamper[(int(i), int(o))] = Fr(dl)
    # sup of P on each cell, prefix maxima of max(P, 0) up to node k
    psup = [Fr(c.P3_iv(c.a, c.b)[0].hi, ONE) for c in cells]
    pplus = [Fr(0)]
    for s in psup:
        pplus.append(max(pplus[-1], s, Fr(0)))
    Fo = F(cells)
    res = {'program': 'A', 'lines': {}, 'ok': True}
    worst = None
    for i in sel:
        c, d = lines[i]
        for o, (alpha, beta) in ((1, (c, d)), (2, (d, c))):
            alpha = alpha - tamper.get((i, o), 0)
            assert alpha > 0 and beta > 0, 'line %d: positive intercept and slope' % i
            k = small_t_index(nodes, pplus, alpha)
            assert k >= 1, "small-t region must contain the first piece"
            stats = {'evals': 0, 'min_gm': None, 'argmin': None}
            ok = True
            for cell in cells[k:]:
                if not check_piece(Fo, cell, cell.a, cell.b, alpha, beta, 0, stats):
                    ok = False; break
            rec = {'ok': ok, 't0': str(nodes[k]), 'evals': stats['evals'],
                   'min_gap_at_midpoints': str(stats['min_gm']) if ok else None,
                   'argmin': str(stats['argmin']) if ok else None}
            if not ok:
                rec['fail_at'] = stats.get('fail_at')
                res['ok'] = False
            res['lines']['%d/%d' % (i, o)] = rec
            if ok and (worst is None or stats['min_gm'] < worst[0]):
                worst = (stats['min_gm'], i, o)
        if (i + 1) % 50 == 0:
            print('line %d done, %.0f s' % (i, time.time() - t0), flush=True)
    res['worst'] = None if worst is None else {'gap': str(worst[0]), 'gap_float_display': float(worst[0]), 'line': worst[1], 'orientation': worst[2]}
    res['seconds'] = round(time.time() - t0, 1)
    json.dump(res, open(outp, 'w'), indent=0)
    nfail = sum(1 for r in res['lines'].values() if not r['ok'])
    print('PROGRAM A: %d line-orientations checked, %d failed; %s' % (len(res['lines']), nfail,
          'ALL LINES CERTIFIED' if res['ok'] else 'SOME LINE NOT CERTIFIED'))
    if worst is not None:
        print('smallest midpoint gap %.3e (line %d, orientation %d)' % (float(worst[0]), worst[1], worst[2]))
    return 0 if res['ok'] else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
