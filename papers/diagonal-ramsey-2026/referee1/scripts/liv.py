# Referee's interval class: Fraction endpoints rounded outward to grid 2^-SH; exp/ln from riv (decimal, widened).
from fractions import Fraction as F
from math import floor, ceil
from riv import exp_iv, ln_iv
SH = 200
SC = 1 << SH
def rd(x): return F(floor(x * SC), SC)
def ru(x): return F(ceil(x * SC), SC)
class I:
    __slots__ = ("lo", "hi")
    def __init__(s, lo, hi=None):
        if hi is None: hi = lo
        lo, hi = F(lo), F(hi)
        assert lo <= hi, (lo, hi)
        s.lo, s.hi = rd(lo), ru(hi)
    @staticmethod
    def c(x):
        if isinstance(x, I): return x
        return I(x, x)
    def __add__(s, o): o = I.c(o); return I(s.lo + o.lo, s.hi + o.hi)
    __radd__ = __add__
    def __neg__(s): return I(-s.hi, -s.lo)
    def __sub__(s, o): o = I.c(o); return I(s.lo - o.hi, s.hi - o.lo)
    def __rsub__(s, o): return I.c(o) - s
    def __mul__(s, o):
        o = I.c(o); ps = [s.lo*o.lo, s.lo*o.hi, s.hi*o.lo, s.hi*o.hi]; return I(min(ps), max(ps))
    __rmul__ = __mul__
    def __truediv__(s, o):
        o = I.c(o); assert o.lo > 0 or o.hi < 0, "div by interval containing 0"
        return s * I(1 / o.hi, 1 / o.lo) if o.lo > 0 else s * I(1 / o.hi, 1 / o.lo)
    def __rtruediv__(s, o): return I.c(o) / s
    def exp(s):
        a, _ = exp_iv(s.lo); _, b = exp_iv(s.hi); return I(a, b)
    def ln(s):
        assert s.lo > 0, "ln of nonpositive"
        a, _ = ln_iv(s.lo); _, b = ln_iv(s.hi); return I(a, b)
    def hull(s, o): return I(min(s.lo, o.lo), max(s.hi, o.hi))
    def __repr__(s): return "[%.17g, %.17g]" % (float(s.lo), float(s.hi))
    def lt(s, o): o = I.c(o); return s.hi < o.lo     # certainly <
    def le(s, o): o = I.c(o); return s.hi <= o.lo
    def ge(s, o): o = I.c(o); return s.lo >= o.hi
    def gt(s, o): o = I.c(o); return s.lo > o.hi

class Ctl:
    """Functions of ZBS Section 3.2 for a control (p, mu, w, beta, x), exact rationals."""
    def __init__(s, p, mu, w, beta, x):
        s.p, s.mu, s.w, s.beta, s.x = map(F, (p, mu, w, beta, x))
        s.lp = I(s.p).ln(); s.lmu = I(s.mu).ln(); s.lx = I(s.x).ln(); s.l1p = I(1 - s.p).ln()
    def G0(s, q):
        q = F(q); lq = I(q).ln(); l1q = I(1 - q).ln()
        return q * s.lp + s.beta * (1 - q) * (s.lp + s.w * l1q - s.lx) - s.beta * s.w * q * (s.lmu - lq)
    def AB(s, q):
        q = F(q); lq = I(q).ln(); l1q = I(1 - q).ln()
        A = F(1 - q, 1) / q * (s.lp + s.w * l1q - s.lx)
        B = s.w * (s.lmu - lq)
        return A, B
    def M(s, q):
        """ZBS two-branch formula; requires q certified feasible (G0<0)."""
        A, B = s.AB(q)
        def bind():
            U = (s.beta * B).exp(); E = (s.beta * A).exp()
            Z = (U - s.p * E) / (1 - s.p)
            return s.p * A + ((1 - s.p) / s.beta) * Z.ln()
        if A.le(B): return B
        if A.gt(B): return bind()
        return B.hull(bind())
    def H(s, q):
        assert s.G0(q).lt(0), "grid point not certified in D"
        return F(q) * s.M(q) + s.w * F(q)
