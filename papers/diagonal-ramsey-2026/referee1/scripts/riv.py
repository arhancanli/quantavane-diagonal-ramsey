# Referee's own rigorous enclosures via decimal (exp/ln correctly rounded half-even; widen by 4 ulp).
from decimal import Decimal, getcontext, localcontext
from fractions import Fraction as F
PREC = 60
def _dec(fr, ctx):
    return ctx.divide(Decimal(fr.numerator), Decimal(fr.denominator))
def _to_frac(d):
    return F(d)
def _ulp(d, prec):
    if d == 0: return Decimal(10) ** (-(prec+50))
    return Decimal(10) ** (d.adjusted() - prec + 1)
def exp_iv(x):
    """x: Fraction -> (lo, hi) Fractions with lo <= e^x <= hi"""
    with localcontext() as ctx:
        ctx.prec = PREC
        d = _dec(F(x), ctx)
        # d itself is rounded; widen input by its ulp
        u = _ulp(d, PREC)
        lo_in, hi_in = d - 2*u, d + 2*u
        assert F(lo_in) <= F(x) <= F(hi_in)
        elo = lo_in.exp(); ehi = hi_in.exp()
        return F(elo - 4*_ulp(elo, PREC)), F(ehi + 4*_ulp(ehi, PREC))
def ln_iv(x):
    x = F(x); assert x > 0
    with localcontext() as ctx:
        ctx.prec = PREC
        d = _dec(x, ctx); u = _ulp(d, PREC)
        lo_in, hi_in = d - 2*u, d + 2*u
        assert lo_in > 0 and F(lo_in) <= x <= F(hi_in)
        llo = lo_in.ln(); lhi = hi_in.ln()
        return F(llo - 4*_ulp(llo, PREC)), F(lhi + 4*_ulp(lhi, PREC))
