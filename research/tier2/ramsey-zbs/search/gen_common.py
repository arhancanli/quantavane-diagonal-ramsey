"""Exact helpers for the certificate generator (proposes data; the checkers decide)."""
import math, sys, os
from fractions import Fraction as Fr
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code', 'checkA'))
import ivA

GRID = 10 ** 13


def up(v, den=GRID):    # rational >= v (v float or Fraction), on grid 1/den
    v = Fr(v); return Fr(-((-v.numerator * den) // v.denominator), den)


def down(v, den=GRID):
    v = Fr(v); return Fr((v.numerator * den) // v.denominator, den)


def neg_log_up(y):
    """rational aU with e^{-aU} <= y (aU >= -log y), tight."""
    y = Fr(y)
    a = up(-ivA.log(y).lof())
    while not ivA.exp(-a).hif() <= y:
        a += Fr(1, GRID)
    return a


def child_slope(pc):
    """for child density pc: z < 1 - pc and d with e^{-d} <= z (so d > -log(1 - pc))."""
    z = Fr(1) - Fr(pc) - Fr(1, 10 ** 12)
    return z, neg_log_up(z)


def terminal(ctl, A_sigma):
    """ctl: dict p, mu, w, x (strings); returns xi, nu, ys, aU, bU (Fractions) for a terminal using source A_sigma."""
    x, mu = Fr(ctl['x']), Fr(ctl['mu'])
    eA = ivA.exp(-Fr(A_sigma)).lof()                 # lower bound of e^{-A_sigma}
    xi = down(min(x, eA) * (1 - Fr(1, 10 ** 11)))
    assert 0 < xi < x and xi < eA
    nu = down(mu * (1 - Fr(1, 10 ** 11)))
    ys = Fr(1, 10 ** 12)
    return xi, nu, ys, neg_log_up(xi), neg_log_up(nu)
