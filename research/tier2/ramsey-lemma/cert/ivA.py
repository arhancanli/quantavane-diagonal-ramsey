"""Checker A, part 1: outward-rounded interval arithmetic on dyadic integers (own implementation).

An interval [lo, hi] is stored as two Python ints scaled by 2^B (value = int / 2^B).  Every operation rounds lo
down and hi up, so the true real value always lies in the interval.  Transcendental functions use fixed-point
series with directed rounding (all terms nonnegative, so floors give lower and ceilings give upper sums):
  log y, y in [1,2):  2 * sum_{j<m} u^{2j+1}/(2j+1),  u = (y-1)/(y+1) in [0,1/3],
                      remainder in [0, 2 u^{2m+1} / ((2m+1)(1-u^2))]   (u^2 <= 1/9, so <= 2.25 * 2 u^{2m+1}/(2m+1))
  exp y, 0 <= y <= 1/16: sum_{j<=m} y^j/j!, remainder in [0, 2 y^{m+1}/(m+1)!], then r squarings.
No floating point is used anywhere in this module.
"""
if not __debug__:
    raise SystemExit('checker A is written with assert statements; refusing to run under python -O')
from fractions import Fraction

B = 256               # output precision (bits after the binary point)
G = 40                # guard bits for series
W = B + G
ONE = 1 << B
ONEW = 1 << W


def _cdiv(a, b):      # ceil(a/b) for b > 0
    return -((-a) // b)


class Iv:
    __slots__ = ('lo', 'hi')

    def __init__(self, lo, hi=None):
        self.lo = lo
        self.hi = lo if hi is None else hi
        if self.lo > self.hi:
            raise ArithmeticError('empty interval')

    @staticmethod
    def q(x):
        """enclosure of a rational (Fraction, int or str)."""
        x = Fraction(x)
        n, d = x.numerator << B, x.denominator
        return Iv(n // d, _cdiv(n, d))

    def lof(self):
        return Fraction(self.lo, ONE)

    def hif(self):
        return Fraction(self.hi, ONE)

    def width(self):
        return Fraction(self.hi - self.lo, ONE)

    def __add__(self, o):
        o = _iv(o)
        return Iv(self.lo + o.lo, self.hi + o.hi)

    __radd__ = __add__

    def __neg__(self):
        return Iv(-self.hi, -self.lo)

    def __sub__(self, o):
        o = _iv(o)
        return Iv(self.lo - o.hi, self.hi - o.lo)

    def __rsub__(self, o):
        return _iv(o) - self

    def __mul__(self, o):
        o = _iv(o)
        ps = (self.lo * o.lo, self.lo * o.hi, self.hi * o.lo, self.hi * o.hi)
        return Iv(min(ps) >> B, -((-max(ps)) >> B))

    __rmul__ = __mul__

    def __truediv__(self, o):
        o = _iv(o)
        if o.lo <= 0:
            if o.hi < 0:
                return -(self / (-o))
            raise ArithmeticError('division by an interval containing 0')
        a, b = self.lo << B, self.hi << B
        return Iv(min(a // o.lo, a // o.hi), max(_cdiv(b, o.lo), _cdiv(b, o.hi)))

    def __rtruediv__(self, o):
        return _iv(o) / self

    def gt(self, o):
        return self.lo > _iv(o).hi

    def ge(self, o):
        return self.lo >= _iv(o).hi

    def __repr__(self):
        return 'Iv[%.17g, %.17g]' % (self.lo / ONE, self.hi / ONE)


def _iv(x):
    return x if isinstance(x, Iv) else Iv.q(x)


# ---------------- logarithm ----------------
def _atanh2_bounds(u_lo, u_hi):
    """u_lo <= u <= u_hi given as W-scaled ints with 0 <= u <= 1/3; returns W-scaled ints (L, U) with
    L <= 2 atanh(u) <= U."""
    m = W // 3 + 4                      # u^{2m} <= 9^{-m} < 2^{-W-4}
    def lower(u):
        u2 = (u * u) >> W
        p = u; s = 0
        for j in range(m):
            s += p // (2 * j + 1)
            p = (p * u2) >> W
        return 2 * s
    def upper(u):
        u2 = -((-(u * u)) >> W)
        p = u; s = 0
        for j in range(m):
            s += _cdiv(p, 2 * j + 1)
            p = -((-(p * u2)) >> W)
        # p >= u^{2m+1}; remainder <= 2 p /((2m+1)(1-u^2)) <= 2 p * 9/(8(2m+1))
        return 2 * s + _cdiv(2 * 9 * p, 8 * (2 * m + 1)) + 1
    return lower(u_lo), upper(u_hi)


_LOG2 = None


def log2_iv():
    global _LOG2
    if _LOG2 is None:
        third_lo, third_hi = ONEW // 3, _cdiv(ONEW, 3)
        L, U = _atanh2_bounds(third_lo, third_hi)
        _LOG2 = Iv(L >> G, -((-U) >> G))
    return _LOG2


def _log_rat(x):
    """enclosure of log x for a positive rational x."""
    x = Fraction(x)
    if x <= 0:
        raise ArithmeticError('log of nonpositive')
    k = x.numerator.bit_length() - x.denominator.bit_length()
    y = x / Fraction(2) ** k
    while y >= 2:
        y /= 2; k += 1
    while y < 1:
        y *= 2; k -= 1
    u = (y - 1) / (y + 1)
    un, ud = u.numerator << W, u.denominator
    L, U = _atanh2_bounds(un // ud, _cdiv(un, ud))
    base = Iv(L >> G, -((-U) >> G))
    if k:
        base = base + log2_iv() * Iv(k << B, k << B)
    return base


def log(x):
    x = _iv(x)
    if x.lo <= 0:
        raise ArithmeticError('log of interval not strictly positive')
    a = _log_rat(Fraction(x.lo, ONE))
    b = a if x.hi == x.lo else _log_rat(Fraction(x.hi, ONE))
    return Iv(a.lo, b.hi)


# ---------------- exponential ----------------
def _exp_nonneg_bounds(y_lo, y_hi):
    """0 <= y_lo <= y <= y_hi <= 1/16 (W-scaled); returns W-scaled (L, U) with L <= e^y <= U."""
    def lower(y):
        s = ONEW; t = ONEW; j = 0
        while t:
            j += 1
            t = (t * y >> W) // j
            s += t
        return s
    def upper(y):
        s = ONEW; t = ONEW; j = 0
        while True:
            j += 1
            t = _cdiv(-((-(t * y)) >> W), j)
            s += t
            if t * 16 < (1 << 8) or j > 400:   # t tiny: remainder bound below
                break
        # remainder after degree j: <= 2 * t * y/(j+1) <= t (y <= 1/16)
        return s + t + 1
    return lower(y_lo), upper(y_hi)


def _exp_rat(z):
    z = Fraction(z)
    if z < 0:
        return Iv.q(1) / _exp_rat(-z)
    r = 0
    while z > Fraction(1, 16) * (1 << r):
        r += 1
    y = z / (1 << r)
    yn, yd = y.numerator << W, y.denominator
    L, U = _exp_nonneg_bounds(yn // yd, _cdiv(yn, yd))
    e = Iv(L >> G, -((-U) >> G))
    for _ in range(r):
        e = e * e
    return e


def exp(x):
    x = _iv(x)
    a = _exp_rat(Fraction(x.lo, ONE))
    b = a if x.hi == x.lo else _exp_rat(Fraction(x.hi, ONE))
    return Iv(a.lo, b.hi)


def ceil_grid(x, den):
    """smallest multiple of 1/den that is >= the rational x (exact)."""
    x = Fraction(x)
    return Fraction(-((-x.numerator * den) // x.denominator), den)


def self_test():
    l2 = log2_iv()
    assert l2.lof() < Fraction('0.6931471805599453094172321214581765680755001343602552541206800094933936219696947156058633269964186875') < l2.hif()
    assert l2.width() < Fraction(1, 1 << (B - 4))
    e1 = exp(1)
    assert e1.lof() < Fraction('2.7182818284590452353602874713526624977572470936999595749669676277240766303535475945713821785251664274') < e1.hif()
    l10 = log(10)
    assert l10.lof() < Fraction('2.3025850929940456840179914546843642076011014886287729760333279009675726096773524802359972050895982983') < l10.hif()
    em = exp(Fraction(-7, 3))   # e^{-7/3} = 0.0969719678644050628099066592983707314807208589248043936530474...
    assert em.lof() < Fraction('0.096971967864405062809906659298370731480720858924804393653048')
    assert em.hif() > Fraction('0.096971967864405062809906659298370731480720858924804393653047')
    assert em.width() < Fraction(1, 1 << (B - 8))
    x = log(exp(Fraction(3, 7)))
    assert x.lof() <= Fraction(3, 7) <= x.hif() and x.width() < Fraction(1, 1 << (B - 20))
    y = exp(log(Fraction(5, 11)))
    assert y.lof() <= Fraction(5, 11) <= y.hif() and y.width() < Fraction(1, 1 << (B - 20))
    return True


if __name__ == '__main__':
    print('ivA self test', self_test())
