"""Checker A (exact; Python Fractions only) for an off-diagonal certificate over a validated bank.

Statement checked, for every cell i = [lo, hi] with affine Phi_i(g) = v_lo + (v_hi - v_lo)(g - lo)/(hi - lo):
  'src'  h, 'AB': A_h + g B_h <= Phi_i(g) on [lo, hi]        (checked at lo and hi: both sides affine)
  'src'  h, 'BA': B_h + g A_h <= Phi_i(g) on [lo, hi]
  'pair' R, S   : p_R + p_S <= 1, [lo, hi] in I_R, [1/hi, 1/lo] in I_S, and on [lo, hi]
                  L_R(g) <= Phi_i(g) and g L_S(1/g) <= Phi_i(g), checked at T = {lo, hi} u {knots of R in (lo, hi)}
                  u {1/y : y knot of S in (1/hi, 1/lo)}; between consecutive points of T every side is affine
                  (on a piece of S, L_S(t) = c + d t gives g L_S(1/g) = c g + d).
Cells must tile [g_lo, 1] in order. Bank: certCD3-full.json or certK3-full.json, pinned by SHA-256.
usage: python3 -I ramsey_offdiag_checkA.py bank_full.json offdiag_cert.json [out.json]
"""
import sys, json, hashlib, time
from fractions import Fraction as Fr

assert __debug__, 'refusing to run under python -O'
PINNED = {
    '32bcafd3fccbf094c83cc942669b3b843f09a3b10f87a6bd6a465d112bb07af8': 'certCD3-full (Theorem 2U bank)',
    '38091eed691b3ffa954d81e9658885cb68fb30e4e46ae76ddc376444f69ee468': 'certK3-full (Theorem 1U bank)',
}
REPORT_G = ['1/5', '21/100', '1/4', '3/10', '1/3', '2/5', '1/2', '3/5', '2/3', '7/10', '3/4', '4/5', '17/20', '9/10',
            '19/20', '99/100', '1']


class Refused(Exception):
    pass


def need(cond, msg):
    if not cond:
        raise Refused(msg)


def q(s):
    need(isinstance(s, str), 'non-string rational %r' % (s,))
    v = Fr(s)
    return v


def file_sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''):
            h.update(b)
    return h.hexdigest()


class Claim:
    def __init__(self, r):
        self.p = q(r['p'])
        self.xs = [q(x) for x in r['xs']]
        self.ys = [q(y) for y in r['ys']]
        need(0 < self.p < 1, 'density outside (0, 1)')
        need(len(self.xs) == len(self.ys) >= 2, 'knot list length')
        need(all(a < b for a, b in zip(self.xs, self.xs[1:])), 'knots not increasing')
        need(self.xs[0] > 0, 'interval not in (0, inf)')

    def L(self, t):
        xs, ys = self.xs, self.ys
        need(xs[0] <= t <= xs[-1], 'evaluation outside the interval')
        for j in range(len(xs) - 1):
            if xs[j] <= t <= xs[j + 1]:
                return ys[j] + (ys[j + 1] - ys[j]) * (t - xs[j]) / (xs[j + 1] - xs[j])
        raise Refused('unreachable')


def dec_up(v, places):
    # exact ceiling of v at the given number of decimals (referee 19 Nov, finding 7)
    m = 10 ** places
    n = -((-v.numerator * m) // v.denominator)
    return '%d.%0*d' % (n // m, places, n % m)


def exp_upper(x):
    # e^x for 0 <= x <= 3: Taylor sum to N plus the tail bound x^(N+1)/(N+1)! * e^3 (e^3 < 21)
    need(0 <= x <= 3, 'exp range')
    s, term, n = Fr(0), Fr(1), 0
    while n <= 40:
        s += term; n += 1; term = term * x / n
    return s + term * 21


def main():
    t0 = time.time()
    bank_path, cert_path = sys.argv[1], sys.argv[2]
    out_path = sys.argv[3] if len(sys.argv) > 3 else None
    sha = file_sha(bank_path)
    need(sha in PINNED, 'bank SHA-256 %s not pinned' % sha)
    cert = json.load(open(cert_path))
    need(cert.get('bank_sha256') == sha, 'certificate names another bank')
    bank = json.load(open(bank_path))
    lists = {'raw': bank['raw'], 'closed': bank['closed']}
    sources = bank['sources']
    cache = {}

    def claim(ref):
        need(isinstance(ref, list) and len(ref) == 2 and ref[0] in lists, 'bad claim reference')
        lst, i = ref
        need(isinstance(i, int) and not isinstance(i, bool) and 0 <= i < len(lists[lst]), 'claim index out of range')
        key = (lst, i)
        if key not in cache:
            cache[key] = Claim(lists[lst][i])
        return cache[key]

    g_lo = q(cert['g_lo'])
    need(g_lo == Fr(1, 5), 'g_lo must be 1/5')  # referee 19 Nov, finding 8
    cells = cert['cells']
    need(len(cells) >= 1, 'no cells')
    prev = g_lo
    margins = {'src': None, 'pair': None}
    table = []
    for n, c in enumerate(cells):
        lo, hi, vlo, vhi = q(c['lo']), q(c['hi']), q(c['v_lo']), q(c['v_hi'])
        need(lo == prev, 'cells do not tile at cell %d' % n)
        need(lo < hi <= 1, 'cell %d bounds' % n)
        need(vlo > 0 and vhi > 0, 'cell %d values' % n)
        prev = hi

        def phi(t):
            return vlo + (vhi - vlo) * (t - lo) / (hi - lo)

        kind = c['kind']
        if kind == 'src':
            h = c['h']
            need(isinstance(h, int) and not isinstance(h, bool) and 0 <= h < len(sources), 'source index')
            A, B = q(sources[h]['A']), q(sources[h]['B'])
            need(A > 0 and B > 0, 'source coefficients')
            need(c['orient'] in ('AB', 'BA'), 'orientation')
            pts = [lo, hi]
            if c['orient'] == 'AB':
                gaps = [phi(t) - (A + t * B) for t in pts]
            else:
                gaps = [phi(t) - (B + t * A) for t in pts]
        elif kind == 'pair':
            R, S = claim(c['R']), claim(c['S'])
            need(R.p + S.p <= 1, 'cell %d: densities sum above 1' % n)
            need(R.xs[0] <= lo and hi <= R.xs[-1], 'cell %d: [lo, hi] not in I_R' % n)
            need(S.xs[0] <= 1 / hi and 1 / lo <= S.xs[-1], 'cell %d: [1/hi, 1/lo] not in I_S' % n)
            pts = {lo, hi}
            pts.update(x for x in R.xs if lo < x < hi)
            pts.update(1 / y for y in S.xs if 1 / hi < y < 1 / lo)
            gaps = []
            for t in sorted(pts):
                gaps.append(phi(t) - R.L(t))
                gaps.append(phi(t) - t * S.L(1 / t))
        else:
            raise Refused('unknown kind %r' % kind)
        m = min(gaps)
        need(m >= 0, 'cell %d (%s): bound exceeds Phi by %s' % (n, kind, float(-m)))
        margins[kind] = m if margins[kind] is None else min(margins[kind], m)
        for gs in REPORT_G:
            g = Fr(gs)
            if lo <= g < hi or (g == hi == 1):
                table.append((gs, phi(g)))
    need(prev == 1, 'cells do not reach 1')
    res = {'checker': 'A', 'ok': True, 'bank': PINNED[sha], 'bank_sha256': sha, 'cert_sha256': file_sha(cert_path),
           'cells': len(cells), 'g_lo': str(g_lo),
           'min_margin': {k: (str(v) if v is not None else None) for k, v in margins.items()},
           'phi': [{'g': gs, 'phi': str(v), 'phi_dec_up': dec_up(v, 9),
                    'exp_phi_upper': dec_up(exp_upper(v), 7)} for gs, v in table],
           'seconds': round(time.time() - t0, 1)}
    print(json.dumps(res, indent=1))
    if out_path:
        json.dump(res, open(out_path, 'w'), indent=1)


if __name__ == '__main__':
    try:
        main()
    except Refused as e:
        print('REFUSED:', e)
        sys.exit(2)
