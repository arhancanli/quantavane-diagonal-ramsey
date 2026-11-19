#!/usr/bin/env python3
"""checkD_C: a third, independently written checker for Lemma D certificates.

Written from CERT_DESIGN.md Sections 1-3, 4b and 4c only (spec commit ddb8c7a8e).  No code, formula
derivation or library is shared with cert/checkD_A.py, cert/checkD_B.py or cert/genD.py (none of them
was opened while writing this file).

ARITHMETIC (different from A's dyadic intervals and B's Arb):
  * every rational datum and every rational intermediate (C0, P1, heights, hull breakpoints, theta,
    kappa, the final U(B)) is an exact fractions.Fraction;
  * irrational quantities are enclosed in class IV: closed intervals with fixed-point endpoints
    lo/2^256, hi/2^256 (Python ints), every operation rounded outward (floor for lo, ceil for hi);
  * exp and log are written here from scratch (Taylor series with halving/squaring for exp,
    atanh series with power-of-two reduction for log, ln 2 by the atanh(1/3) series), each with a
    proven truncation bound that is added to the enclosure (see _exp_bounds and _log_bounds);
  * H, Ht', Ht'', Ht''' come from interval Taylor jets (automatic differentiation in interval
    arithmetic) applied to the 4c formula for M(q); nothing is hand-differentiated.
No float is created anywhere in this file except in decimal display strings; no decision uses one.

Every accept/reject decision is a comparison of exact Fractions or of interval endpoints.

CHOICES the specification leaves open (documented; see also SPEC_ISSUES.md):
  * node heights (K5): tangent at the right end of each cell by default (--heights right, the 4c
    example); --heights mid uses the midpoint tangent (also valid, tighter) for comparison only;
  * |Ht''| bound on a cell (K6): min of (a) the direct interval enclosure of Ht'' over the cell and
    (b) |Ht''(midpoint)| + (h/2) sup|Ht'''| over the cell, for each branch formula that may be active;
    a cell whose sign of A - B is not certified uses the max over both branch formulas;
  * "certified in Q": G0(q)+ < 0 at both ends of the cell (G0 is convex); every node q_1..q_N is
    checked individually as well;
  * nodes j >= 1 only are used for j0, jA, jB (q_0 = a_cut need not lie in Q);
  * switch points: bisection to width 2^-120 of the interval (or until the sign is uncertain);
  * jA = N (no cell >= jA) and "no node with H(q_j)- >= C0" are treated as failures;
  * jB = N or jB < jA0 or jB undefined -> kappa2h = 0 (E_high at its largest);
  * q_min(Psi+) = q_j0 (the 4c example); q_R = q of the hull line active at s = (log b2)+, right
    piece at a breakpoint;
  * theta = kappa / kappa2 computed EXACTLY as a Fraction (kappa = alpha K+ / h1 exactly), so the
    same theta is used in every place it appears;
  * step 3 uses [u_b, u_b] when PK = g- exactly as 4b says (sound; see SPEC_ISSUES.md item 2).
"""
import sys
import json
import argparse
import random
from bisect import bisect_right
from fractions import Fraction as Fr

# ----------------------------------------------------------------------------------------------
# Outward-rounded fixed-point interval arithmetic
# ----------------------------------------------------------------------------------------------
P = 256                 # fractional bits of every IV endpoint
ONE = 1 << P


def _cdiv(a, b):
    """ceil(a / b) for ints, b != 0."""
    return -((-a) // b)


class IV(object):
    """Closed interval [lo/2^P, hi/2^P], lo <= hi ints; all operations outward rounded."""
    __slots__ = ('lo', 'hi')

    def __init__(self, lo, hi):
        if lo > hi:
            raise ArithmeticError('inverted interval')
        self.lo = lo
        self.hi = hi

    @staticmethod
    def of(v):
        if isinstance(v, IV):
            return v
        if isinstance(v, bool):
            raise TypeError('bool')
        if isinstance(v, int):
            n = v << P
            return IV(n, n)
        if isinstance(v, Fr):
            num = v.numerator << P
            d = v.denominator
            return IV(num // d, _cdiv(num, d))
        raise TypeError('IV.of(%r)' % type(v))

    @staticmethod
    def _ok(o):
        return isinstance(o, (IV, int, Fr)) and not isinstance(o, bool)

    def __add__(s, o):
        if not IV._ok(o):
            return NotImplemented
        o = IV.of(o)
        return IV(s.lo + o.lo, s.hi + o.hi)

    __radd__ = __add__

    def __neg__(s):
        return IV(-s.hi, -s.lo)

    def __sub__(s, o):
        if not IV._ok(o):
            return NotImplemented
        o = IV.of(o)
        return IV(s.lo - o.hi, s.hi - o.lo)

    def __rsub__(s, o):
        if not IV._ok(o):
            return NotImplemented
        return IV.of(o) - s

    def __mul__(s, o):
        if not IV._ok(o):
            return NotImplemented
        o = IV.of(o)
        a = s.lo * o.lo
        b = s.lo * o.hi
        c = s.hi * o.lo
        d = s.hi * o.hi
        return IV(min(a, b, c, d) >> P, -((-max(a, b, c, d)) >> P))

    __rmul__ = __mul__

    def __truediv__(s, o):
        if not IV._ok(o):
            return NotImplemented
        o = IV.of(o)
        if not (o.lo > 0 or o.hi < 0):
            raise ZeroDivisionError('IV division by an interval containing 0')
        nl = s.lo << P
        nh = s.hi << P
        lo = min(nl // o.lo, nl // o.hi, nh // o.lo, nh // o.hi)
        hi = max(_cdiv(nl, o.lo), _cdiv(nl, o.hi), _cdiv(nh, o.lo), _cdiv(nh, o.hi))
        return IV(lo, hi)

    def __rtruediv__(s, o):
        if not IV._ok(o):
            return NotImplemented
        return IV.of(o) / s

    def absmax(s):
        """Upper bound of |x| on the interval, as a Fraction."""
        return Fr(max(abs(s.lo), abs(s.hi)), ONE)

    def lof(s):
        return Fr(s.lo, ONE)

    def hif(s):
        return Fr(s.hi, ONE)

    def hull(s, o):
        return IV(min(s.lo, o.lo), max(s.hi, o.hi))

    def __repr__(s):
        return 'IV[%s, %s]' % (dec(s.lof()), dec(s.hif()))


ZERO = IV(0, 0)


# ---- ln 2 by 2 atanh(1/3) = 2 sum_{i>=0} 1 / ((2i+1) 3^(2i+1)) ---------------------------------
_LN2 = {}


def _ln2(Q):
    """Integers (lo, hi) with lo <= ln2 * 2^Q <= hi.

    Each term floor(2^Q / ((2i+1) 3^(2i+1))) is low by < 1; the tail after K terms is at most
    3^-(2K+1) * (9/8) / (2K+1) < 2^-Q for K = (Q+1)//3 + 1 (since 3^2 > 2^3).  So with S the sum of
    the K floored terms, S <= atanh(1/3) 2^Q <= S + K + 1, and ln 2 = 2 atanh(1/3).
    """
    if Q not in _LN2:
        K = (Q + 1) // 3 + 1
        S = 0
        for i in range(K):
            S += (1 << Q) // ((2 * i + 1) * 3 ** (2 * i + 1))
        _LN2[Q] = (2 * S, 2 * (S + K + 1))
    return _LN2[Q]


def _log_bounds(n):
    """For an int n > 0 return ints (lo, hi) with lo <= log(n / 2^P) * 2^P <= hi.

    Reduction: n / 2^P = 2^k y with y in [2^-1/2, 2^1/2] exactly (y = num/den, ints), so
    z = (y - 1)/(y + 1) has |z| <= (sqrt2 - 1)/(sqrt2 + 1) < 0.1716 and log = k ln2 + 2 atanh(z).
    Fixed point at Q = P + 64 bits:  Z = floor(z 2^Q) (error < 1 ulp, which moves atanh by
    < 1.03 ulp), Z2 = floor(Z^2 / 2^Q), T_0 = Z, T_i = floor(T_{i-1} Z2 / 2^Q).  With e_i the error of
    T_i against 2^Q z~^(2i+1):  |e_i| <= |e_{i-1}| (z^2 + 2^-Q) + |z|^(2i-1) + 1 <= 1.25 for all i, so
    each floor(T_i / (2i+1)) is within 2.25 ulp of its term.  The tail after K terms is at most
    |z|^(2K+3)/(1 - z^2) < 2^-(Q+1) when (2K+3) * 2.54 >= Q + 1, true for K = (Q+1)//5 + 2.
    Total atanh error < 2.25 (K+1) + 1 + 1.03 <= pad = 3 (K+1) + 4 ulps.
    """
    if n <= 0:
        raise ArithmeticError('log of a nonpositive number')
    if n == ONE:
        return 0, 0
    Q = P + 64
    b = n.bit_length()                # 2^(b-1) <= n < 2^b
    num = n
    den = 1 << (b - 1)                # y = num/den in [1, 2)
    k = b - 1 - P
    if num * num > 2 * den * den:     # y > sqrt 2: use y/2 in (2^-1/2, 1)
        den <<= 1
        k += 1
    Z = ((num - den) << Q) // (num + den)
    Z2 = (Z * Z) >> Q
    K = (Q + 1) // 5 + 2
    T = Z
    A = Z
    for i in range(1, K + 1):
        T = (T * Z2) >> Q
        A += T // (2 * i + 1)
    pad = 3 * (K + 1) + 4
    l2lo, l2hi = _ln2(Q)
    if k >= 0:
        lo = k * l2lo + 2 * (A - pad)
        hi = k * l2hi + 2 * (A + pad)
    else:
        lo = k * l2hi + 2 * (A - pad)
        hi = k * l2lo + 2 * (A + pad)
    sh = Q - P
    return lo >> sh, -((-hi) >> sh)


def _exp_bounds(n):
    """For an int n return ints (lo, hi) with lo <= exp(n / 2^P) * 2^P <= hi.

    exp(x) = (exp(r))^(2^m), r = x / 2^m, m chosen with |r| < 2^-8.  Taylor at Q = P + m + 64 bits:
    R = r 2^Q is exact; t_0 = 2^Q, t_i = floor(t_{i-1} R / (i 2^Q)).  The error e_i of t_i satisfies
    |e_i| <= |e_{i-1}| |r| / i + 1 <= 1/(1 - 2^-8), and the tail after K terms is at most
    2 |r|^(K+1) / (K+1)! < 2^-Q for 8 (K+1) >= Q + 1 (K = (Q+1)//8 + 1).  So the Taylor enclosure has
    pad = 2K + 4 ulps.  Then m outward-rounded squarings of the positive interval.
    Arguments below -200 give [0, 2^-P] (exp(-200) < 2^-288); above +200 are refused.
    """
    if n == 0:
        return ONE, ONE
    if n < -(200 << P):
        return 0, 1
    if n > (200 << P):
        raise ArithmeticError('exp argument too large')
    bl = abs(n).bit_length()
    m = max(0, bl - P + 8)            # |n| < 2^bl <= 2^(P + m - 8)
    Q = P + m + 64
    R = n << (Q - P - m)              # exactly r * 2^Q
    K = (Q + 1) // 8 + 1
    t = 1 << Q
    S = t
    for i in range(1, K + 1):
        t = (t * R) // (i << Q)
        S += t
    pad = 2 * K + 4
    lo = S - pad
    hi = S + pad
    if lo < 0:
        lo = 0
    for _ in range(m):
        lo = (lo * lo) >> Q
        hi = -((-(hi * hi)) >> Q)
    sh = Q - P
    return lo >> sh, -((-hi) >> sh)


def ilog(a):
    a = IV.of(a)
    if a.lo <= 0:
        raise ArithmeticError('log of an interval not certified positive')
    if a.lo == a.hi:
        lo, hi = _log_bounds(a.lo)
        return IV(lo, hi)
    return IV(_log_bounds(a.lo)[0], _log_bounds(a.hi)[1])


def iexp(a):
    a = IV.of(a)
    if a.lo == a.hi:
        lo, hi = _exp_bounds(a.lo)
        return IV(lo, hi)
    return IV(_exp_bounds(a.lo)[0], _exp_bounds(a.hi)[1])


# ----------------------------------------------------------------------------------------------
# Interval Taylor jets (coefficients c_k = f^(k)/k!), for derivatives of the 4c formulas
# ----------------------------------------------------------------------------------------------
class Jet(object):
    __slots__ = ('c',)

    def __init__(self, c):
        self.c = c

    @staticmethod
    def var(x, order):
        return Jet([IV.of(x), IV.of(1)] + [ZERO] * (order - 1))

    @staticmethod
    def const(v, order):
        return Jet([IV.of(v)] + [ZERO] * order)

    def __add__(s, o):
        if isinstance(o, Jet):
            return Jet([a + b for a, b in zip(s.c, o.c)])
        c = list(s.c)
        c[0] = c[0] + o
        return Jet(c)

    __radd__ = __add__

    def __neg__(s):
        return Jet([-a for a in s.c])

    def __sub__(s, o):
        return s + (-o)

    def __rsub__(s, o):
        return (-s) + o

    def __mul__(s, o):
        if isinstance(o, Jet):
            n = len(s.c)
            out = []
            for k in range(n):
                acc = s.c[0] * o.c[k]
                for i in range(1, k + 1):
                    acc = acc + s.c[i] * o.c[k - i]
                out.append(acc)
            return Jet(out)
        o = IV.of(o)
        return Jet([a * o for a in s.c])

    __rmul__ = __mul__

    def __truediv__(s, o):
        if isinstance(o, Jet):
            n = len(s.c)
            out = []
            for k in range(n):
                acc = s.c[k]
                for j in range(1, k + 1):
                    acc = acc - o.c[j] * out[k - j]
                out.append(acc / o.c[0])
            return Jet(out)
        o = IV.of(o)
        return Jet([a / o for a in s.c])

    def __rtruediv__(s, o):
        return Jet.const(o, len(s.c) - 1) / s

    def deriv(s, k):
        """Enclosure of the k-th derivative."""
        f = 1
        for i in range(2, k + 1):
            f *= i
        return s.c[k] * f


def jexp(a):
    n = len(a.c)
    e = [iexp(a.c[0])]
    for k in range(1, n):
        acc = ZERO
        for m in range(1, k + 1):
            acc = acc + IV.of(Fr(m, k)) * a.c[m] * e[k - m]
        e.append(acc)
    return Jet(e)


def jlog(a):
    n = len(a.c)
    out = [ilog(a.c[0])]
    for k in range(1, n):
        acc = a.c[k]
        for m in range(1, k):
            acc = acc - IV.of(Fr(m, k)) * out[m] * a.c[k - m]
        out.append(acc / a.c[0])
    return Jet(out)


# ----------------------------------------------------------------------------------------------
# Display helper (exact; no floats)
# ----------------------------------------------------------------------------------------------
def dec(x, digits=6):
    """Exact Fraction -> scientific string with `digits` significant digits (truncated)."""
    x = Fr(x)
    if x == 0:
        return '0'
    sgn = '-' if x < 0 else ''
    x = abs(x)
    e = 0
    while x >= 10:
        x /= 10
        e += 1
    while x < 1:
        x *= 10
        e -= 1
    m = int(x * 10 ** (digits - 1))
    s = str(m)
    return '%s%s.%se%+d' % (sgn, s[0], s[1:], e)


# ----------------------------------------------------------------------------------------------
# The model of 4c (base control only)
# ----------------------------------------------------------------------------------------------
class Model(object):
    def __init__(self, p, mu, w, beta, x):
        self.p, self.mu, self.w, self.beta, self.x = p, mu, w, beta, x
        self.lp = ilog(p)
        self.lx = ilog(x)
        self.lmu = ilog(mu)

    def G0(self, q):
        """G0(q) = q log p + beta (1-q)(log p + w log(1-q) - log x) - beta w q (log mu - log q)."""
        Q = IV.of(q)
        L = self.lp + self.w * ilog(1 - Q) - self.lx
        return Q * self.lp + self.beta * (1 - Q) * L - self.beta * self.w * Q * (self.lmu - ilog(Q))

    def G0p(self, q):
        """G0'(q) = log p - beta (log p + w log(1-q) - log x) - beta w (log mu - log q)."""
        Q = IV.of(q)
        return (self.lp - self.beta * (self.lp + self.w * ilog(1 - Q) - self.lx)
                - self.beta * self.w * (self.lmu - ilog(Q)))

    def branches(self, qiv, order):
        """Jets of Ht on the two branch formulas at q in qiv.

        Returns (AmB, free, bind): AmB encloses A - B; free = jet of q B; bind = jet of q M_bind or
        None when (U - p e^{beta A}) is not certified positive on qiv.
        """
        p, w, beta = self.p, self.w, self.beta
        q = Jet.var(qiv, order)
        omq = 1 - q
        Lt = jlog(omq) * w + (self.lp - self.lx)          # log p + w log(1-q) - log x
        A = (omq / q) * Lt
        B = (-jlog(q) + self.lmu) * w
        free = q * B
        bind = None
        U = jexp(B * beta)
        E = jexp(A * beta)
        Zn = U - E * p                                     # (1-p) Z
        if Zn.c[0].lo > 0:
            Z = Zn * (1 / (1 - p))
            Mb = A * p + jlog(Z) * ((1 - p) / beta)
            bind = q * Mb
        AmB = (A - B).c[0]
        return AmB, free, bind

    def active(self, qiv, order):
        """List of Ht jets that may be the active branch on qiv (raises if a needed one fails)."""
        AmB, free, bind = self.branches(qiv, order)
        if AmB.lo > 0:
            if bind is None:
                raise ArithmeticError('binding branch needed but Z not certified positive')
            return [bind]
        if AmB.hi <= 0:
            return [free]
        if bind is None:
            raise ArithmeticError('sign of A-B uncertain and Z not certified positive')
        return [free, bind]

    def node(self, q):
        """(H enclosure, Ht' enclosure) at a point q (union over possibly active branches)."""
        js = self.active(IV.of(q), 1)
        Ht = None
        Htp = None
        for J in js:
            v = J.c[0]
            d = J.deriv(1)
            Ht = v if Ht is None else Ht.hull(v)
            Htp = d if Htp is None else Htp.hull(d)
        H = Ht + self.w * IV.of(q)
        return H, Htp

    def d2_cell(self, qa, qb):
        """Upper bound (Fraction) of |Ht''| on [qa, qb] over every branch formula possibly active."""
        cell = IV(IV.of(qa).lo, IV.of(qb).hi)
        mid = (qa + qb) / 2
        half = (qb - qa) / 2
        AmB, free_c, bind_c = self.branches(cell, 3)
        _, free_m, bind_m = self.branches(IV.of(mid), 2)
        if AmB.lo > 0:
            kinds = ('bind',)
        elif AmB.hi <= 0:
            kinds = ('free',)
        else:
            kinds = ('free', 'bind')
        best = Fr(0)
        for kd in kinds:
            Jc, Jm = (free_c, free_m) if kd == 'free' else (bind_c, bind_m)
            if Jc is None or Jm is None:
                raise ArithmeticError('branch formula not evaluable on cell')
            direct = Jc.deriv(2).absmax()                                   # sup |f''| by enclosure
            mv = Jm.deriv(2).absmax() + half * Jc.deriv(3).absmax()         # mean value form
            b = min(direct, mv)
            if b > best:
                best = b
        return best


# ----------------------------------------------------------------------------------------------
# Upper envelope of lines c_j + d_j s (d strictly increasing) and integrals along phi_s
# ----------------------------------------------------------------------------------------------
class Hull(object):
    def __init__(self, lines):
        st = []
        for (c, d, j) in lines:
            if st and not d > st[-1][1]:
                raise ValueError('slopes must increase strictly')
            while len(st) >= 2:
                c1, d1, _ = st[-2]
                c2, d2, _ = st[-1]
                # st[-1] is useless iff x(st[-2], new) <= x(st[-2], st[-1]),  x(a, b) = (c_a - c_b)/(d_b - d_a)
                if (c1 - c) * (d2 - d1) <= (c1 - c2) * (d - d1):
                    st.pop()
                else:
                    break
            st.append((c, d, j))
        self.c = [t[0] for t in st]
        self.d = [t[1] for t in st]
        self.j = [t[2] for t in st]
        self.bps = [(self.c[k - 1] - self.c[k]) / (self.d[k] - self.d[k - 1]) for k in range(1, len(st))]
        self._pre = [ZERO]

    def piece(self, s):
        """Index of the hull line active at s (the right one at a breakpoint)."""
        return bisect_right(self.bps, s)

    def value(self, s):
        r = self.piece(s)
        return self.c[r] + self.d[r] * s

    def pre(self, r):
        """Enclosure of sum_{k=1}^{r} e^{s_k} (d_k - d_{k-1})  (s_k = bps[k-1])."""
        while len(self._pre) <= r:
            k = len(self._pre)
            self._pre.append(self._pre[-1] + iexp(IV.of(self.bps[k - 1])) * (self.d[k] - self.d[k - 1]))
        return self._pre[r]

    def I(self, t, upper):
        """Bound of int_0^t E(log tau) dtau, E the envelope.

        With r the piece used: I_r(t) = t (c_r + d_r (log t - 1)) + pre(r) equals
        int_0^{e^{s_r}} E + int_{e^{s_r}}^t line_r; it is >= I(t) when r is at or right of the true
        piece and <= I(t) when at or left of it.  So the piece at (log t)+ gives an upper bound and the
        piece at (log t)- a lower bound.
        """
        if t == 0:
            return Fr(0)
        if t < 0:
            raise ValueError('negative t')
        S = ilog(IV.of(t))
        sv = S.hif() if upper else S.lof()
        r = self.piece(sv)
        F = IV.of(t) * (IV.of(self.c[r]) + IV.of(self.d[r]) * (S - 1)) + self.pre(r)
        return F.hif() if upper else F.lof()

    def integral_up(self, ta, tb):
        """Upper bound of int_{ta}^{tb} E(log t) dt."""
        return self.I(tb, True) - self.I(ta, False)


# ----------------------------------------------------------------------------------------------
# Certificate parsing
# ----------------------------------------------------------------------------------------------
class CertError(Exception):
    pass


def _no_float(s):
    raise CertError('JSON number %r: rationals must be strings' % s)


def parse_rat(v, name):
    if not isinstance(v, str):
        raise CertError('%s: rational must be a string, got %r' % (name, type(v).__name__))
    s = v.strip()
    if s != v or not s:
        raise CertError('%s: malformed rational %r' % (name, v))
    parts = s.split('/')
    if len(parts) > 2:
        raise CertError('%s: malformed rational %r' % (name, v))

    def isint(t, allow_sign):
        if allow_sign and t.startswith('-'):
            t = t[1:]
        return t.isdigit() and t.isascii()
    if not isint(parts[0], True):
        raise CertError('%s: malformed rational %r' % (name, v))
    if len(parts) == 2:
        if not isint(parts[1], False) or int(parts[1]) == 0:
            raise CertError('%s: malformed denominator %r' % (name, v))
        return Fr(int(parts[0]), int(parts[1]))
    return Fr(int(parts[0]))


def parse_tree(t):
    """Validate the box tree iteratively; return it unchanged."""
    stack = [t]
    n = 0
    while stack:
        x = stack.pop()
        n += 1
        if n > 10 ** 7:
            raise CertError('tree too large')
        if isinstance(x, str):
            if x != 'L':
                raise CertError('tree: leaf must be "L", got %r' % x)
            continue
        if not isinstance(x, list) or len(x) != 3 or x[0] not in ('P', 'p'):
            raise CertError('tree: bad node %r' % (x if not isinstance(x, list) else x[:1]))
        stack.append(x[1])
        stack.append(x[2])
    return t


def load_cert(path):
    with open(path) as f:
        d = json.load(f, parse_float=_no_float, parse_constant=_no_float)
    if not isinstance(d, dict):
        raise CertError('certificate must be a JSON object')
    need = ['control', 'a_cut', 'a_hi', 'alpha', 'u_b', 'Dplus', 'y_c', 'G_up', 'P_up', 'qgrid', 'jA0', 'tree']
    for k in need:
        if k not in d:
            raise CertError('missing field %s' % k)
    c = d['control']
    if not isinstance(c, dict):
        raise CertError('control must be an object')
    cert = {}
    for k in ('p', 'mu', 'w', 'beta', 'x'):
        if k not in c:
            raise CertError('control missing %s' % k)
        cert[k] = parse_rat(c[k], 'control.' + k)
    for k in ('a_cut', 'a_hi', 'alpha', 'u_b', 'Dplus', 'y_c', 'G_up', 'P_up'):
        cert[k] = parse_rat(d[k], k)
    if not isinstance(d['qgrid'], list):
        raise CertError('qgrid must be a list')
    cert['qgrid'] = [parse_rat(v, 'qgrid[%d]' % i) for i, v in enumerate(d['qgrid'])]
    if not isinstance(d['jA0'], int) or isinstance(d['jA0'], bool):
        raise CertError('jA0 must be an integer')
    cert['jA0'] = d['jA0']
    cert['tree'] = parse_tree(d['tree'])
    return cert


# ----------------------------------------------------------------------------------------------
# The checker
# ----------------------------------------------------------------------------------------------
BISECT_STEPS = 120
HGRID = 160             # node heights are rounded UP to multiples of 2^-HGRID


class Reject(Exception):
    pass


class Checker(object):
    def __init__(self, cert, heights='right', log=print, verbose=False, stop_on_data_fail=False):
        self.cert = cert
        self.stop_on_data_fail = stop_on_data_fail
        self.heights_rule = heights
        self.log = log
        self.verbose = verbose
        self.fails = []

    def fail(self, msg):
        self.fails.append(msg)
        self.log('  FAIL: ' + msg)

    # ---- K1 - K9 --------------------------------------------------------------------------------
    def data_checks(self):
        c = self.cert
        p, mu, w, beta, x = c['p'], c['mu'], c['w'], c['beta'], c['x']
        ok = True

        def req(cond, msg):
            if not cond:
                self.fail(msg)
            return cond
        # K1
        k1 = (req(0 < p < 1, 'K1: 0 < p < 1') & req(0 < mu < 1, 'K1: 0 < mu < 1') & req(w > 0, 'K1: w > 0')
              & req(0 < beta < 1, 'K1: 0 < beta < 1') & req(0 < x < p, 'K1: 0 < x < p'))
        if not k1:
            raise Reject('K1')
        self.M = Model(p, mu, w, beta, x)
        one_mu_w = iexp(w * ilog(1 - IV.of(mu)))
        ok &= req(x < one_mu_w.lof(), 'K1: x < (1 - mu)^w  (x = %s, (1-mu)^w >= %s)' % (dec(x), dec(one_mu_w.lof())))
        self.log('  K1 %s' % ('ok' if ok else 'FAILED'))
        # K2
        a_cut, a_hi, alpha = c['a_cut'], c['a_hi'], c['alpha']
        k2 = req(0 < a_cut < a_hi < mu, 'K2: 0 < a_cut < a_hi < mu')
        if k2:
            g_cut = self.M.G0(a_cut)
            g_hi = self.M.G0(a_hi)
            g_mu = self.M.G0(mu)
            gp_hi = self.M.G0p(a_hi)
            k2 &= req(g_cut.lo >= 0, 'K2: G0(a_cut) >= 0 (enclosure %r)' % g_cut)
            k2 &= req(g_hi.hi < 0, 'K2: G0(a_hi) < 0 (enclosure %r)' % g_hi)
            k2 &= req(g_mu.hi < 0, 'K2: G0(mu) < 0 (enclosure %r)' % g_mu)
            k2 &= req(gp_hi.hi < 0, "K2: G0'(a_hi) < 0 (enclosure %r)" % gp_hi)
            if gp_hi.hi < 0:
                need = beta / (-gp_hi.hif())        # >= beta / |G0'(a_hi)|
                k2 &= req(alpha >= need, "K2: alpha >= beta/|G0'(a_hi)| (alpha = %s, bound %s)" % (dec(alpha, 12), dec(need, 12)))
            self.log("  K2 %s  G0(a_cut) in %r, G0(a_hi) in %r, G0'(a_hi) in %r" % ('ok' if k2 else 'FAILED', g_cut, g_hi, gp_hi))
        ok &= k2
        # K3
        u_b, D = c['u_b'], c['Dplus']
        k3 = req(0 < u_b < 1, 'K3: 0 < u_b < 1') & req(D > 0, 'K3: Dplus > 0')
        if k3:
            r = (1 - u_b) / D
            k3 &= req(r.denominator == 1 and r > 0, 'K3: (1 - u_b)/Dplus a positive integer (got %s)' % r)
        self.log('  K3 %s' % ('ok' if k3 else 'FAILED'))
        ok &= k3
        # K4
        q = c['qgrid']
        N = len(q) - 1
        k4 = req(N >= 2, 'K4: N >= 2')
        if k4:
            k4 &= req(q[0] == a_cut, 'K4: q_0 = a_cut')
            k4 &= req(q[N] == mu, 'K4: q_N = mu')
            k4 &= req(all(q[i] < q[i + 1] for i in range(N)), 'K4: q strictly increasing')
            k4 &= req(q[1] >= a_hi, 'K4: q_1 >= a_hi')
        self.log('  K4 %s  (N = %d)' % ('ok' if k4 else 'FAILED', N))
        ok &= k4
        if not (k2 and k4):
            raise Reject('K2/K4')
        self.N = N
        self.q = q
        # every node q_1..q_N in Q, checked directly (implied by K2 + K4 + convexity of G0)
        self.G0n = [None] + [self.M.G0(q[j]) for j in range(1, N + 1)]
        inQ = all(self.G0n[j].hi < 0 for j in range(1, N + 1))
        ok &= req(inQ, 'nodes q_1..q_N certified in Q (G0 < 0)')
        if not inQ:
            raise Reject('nodes not in Q')
        # node values H, Ht' (nodes j >= 1)
        self.Hn = [None] * (N + 1)
        self.Htpn = [None] * (N + 1)
        for j in range(1, N + 1):
            self.Hn[j], self.Htpn[j] = self.M.node(q[j])
        # K5 heights
        self.compute_heights()
        self.log('  K5 heights computed (%s tangents)' % self.heights_rule)
        # K6
        jA0 = c['jA0']
        k6 = req(1 <= jA0 <= N - 1, 'K6: 1 <= jA0 <= N - 1')
        if k6:
            self.d2 = [None] * N
            for i in range(jA0, N):
                if not (self.G0n[i].hi < 0 and self.G0n[i + 1].hi < 0):
                    k6 = req(False, 'K6: cell %d not certified in Q' % i)
                    break
                self.d2[i] = self.M.d2_cell(q[i], q[i + 1])
            if k6:
                # suffix maxima: d2suf[i] = max_{i' >= i} d2[i']
                self.d2suf = [None] * (N + 1)
                cur = None
                for i in range(N - 1, jA0 - 1, -1):
                    cur = self.d2[i] if cur is None else max(cur, self.d2[i])
                    self.d2suf[i] = cur
                self.log('  K6 ok  max |Ht\'\'| over cells >= jA0 <= %s' % dec(self.d2suf[jA0]))
        ok &= k6
        self.jA0 = jA0
        # K7
        Htp_mu = self.Htpn[N]
        k7 = req(c['y_c'] > -w, 'K7: y_c > -w') & req(c['y_c'] >= Htp_mu.hif(),
                                                      "K7: y_c >= Ht'(mu) (y_c = %s, Ht'(mu) <= %s)" % (dec(c['y_c'], 12), dec(Htp_mu.hif(), 12)))
        self.log("  K7 %s  Ht'(mu) in %r" % ('ok' if k7 else 'FAILED', Htp_mu))
        ok &= k7
        # K8
        self.phis_ub = -w * (1 + ilog(u_b))
        k8 = req(self.phis_ub.lof() >= c['y_c'], 'K8: phi_s(u_b) >= y_c')
        self.log('  K8 %s  phi_s(u_b) in %r' % ('ok' if k8 else 'FAILED', self.phis_ub))
        ok &= k8
        # K9
        self.g_ub = -w * u_b * ilog(u_b)
        mwlog = -w * ilog(u_b)
        k9 = req(c['G_up'] >= self.g_ub.hif(), 'K9: G_up >= g(u_b) (g(u_b) in %r)' % self.g_ub)
        k9 &= req(c['P_up'] >= mwlog.hif(), 'K9: P_up >= -w log u_b (in %r)' % mwlog)
        self.log('  K9 %s' % ('ok' if k9 else 'FAILED'))
        ok &= k9
        return ok

    def compute_heights(self):
        q, N, M = self.q, self.N, self.M
        w = self.cert['w']
        h = [None] * (N + 1)

        def up(j, v):
            if h[j] is None or v > h[j]:
                h[j] = v
        for i in range(N):
            # cell 0 always uses the right-end tangent: its midpoint can lie within ~1e-15 of a(0),
            # where H' is unbounded, and the midpoint tangent is then valid but useless
            use_mid = self.heights_rule == 'mid' and i >= 1
            if use_mid:
                m = (q[i] + q[i + 1]) / 2
            if use_mid:
                Hm, Htpm = M.node(m)
                Hp = Htpm + w
                up(i, Hm.hif() - Hp.lof() * (m - q[i]))
                up(i + 1, Hm.hif() + Hp.hif() * (q[i + 1] - m))
            else:
                j = i + 1
                Hp_lo = self.Htpn[j].lof() + w
                up(j, self.Hn[j].hif())
                up(i, self.Hn[j].hif() - Hp_lo * (q[j] - q[i]))
        G = 1 << HGRID
        self.h = [Fr(_cdiv((v.numerator * G), v.denominator), G) for v in h]
        self.Htp_lo = [None] + [self.Htpn[j].lof() for j in range(1, N + 1)]
        self.H_lo = [None] + [self.Hn[j].lof() for j in range(1, N + 1)]
        self.H_hi = [None] + [self.Hn[j].hif() for j in range(1, N + 1)]
        self.full = Hull([(self.h[j], w * q[j], j) for j in range(N + 1)])
        self._psi = {}

    def psi_hull(self, j0):
        if j0 not in self._psi:
            w = self.cert['w']
            self._psi[j0] = Hull([(self.h[j], w * self.q[j], j) for j in range(j0, self.N + 1)])
        return self._psi[j0]

    # ---- helpers ------------------------------------------------------------------------------
    def env_at_y(self, hull, y):
        """max_j (h_j - q_j (w + y)) over the hull's lines, exact for rational y."""
        w = self.cert['w']
        return hull.value(-1 - y / w)

    def phis_lo(self, u):
        return (-self.cert['w'] * (1 + ilog(u))).lof()

    def g_iv(self, u):
        if u == 0:
            return ZERO
        return -self.cert['w'] * u * ilog(u)

    def enclose_u1(self, Phi, p):
        """[a, b] around u1 on [0, u_b]: f(u) = g(u) - (Phi - p (u_b - u)), concave, f(0+) <= 0 < f(u_b)."""
        ub = self.cert['u_b']
        a, b = Fr(0), ub
        for _ in range(BISECT_STEPS):
            m = (a + b) / 2
            f = self.g_iv(m) - (Phi - p * (ub - m))
            if f.hi <= 0:
                a = m
            elif f.lo > 0:
                b = m
            else:
                break
        return a, b

    def enclose_u2(self, Phi, p):
        """[a, b] around u2 on [u_b, 1]: f(u) = Phi + p (u - u_b) - g(u), convex, f(u_b) < 0."""
        ub = self.cert['u_b']
        a, b = ub, Fr(1)
        for _ in range(BISECT_STEPS):
            m = (a + b) / 2
            f = (Phi + p * (m - ub)) - self.g_iv(m)
            if f.hi <= 0:
                a = m
            elif f.lo > 0:
                b = m
            else:
                break
        return a, b

    # ---- U(B), CERT_DESIGN 4b steps 0-8 ------------------------------------------------------
    def box_U(self, Pl, Ph, pl, ph):
        c = self.cert
        w, ub, D, a0, alpha, y_c = c['w'], c['u_b'], c['Dplus'], c['a_cut'], c['alpha'], c['y_c']
        q, N = self.q, self.N
        gm, gp = self.g_ub.lof(), self.g_ub.hif()
        info = {}
        # step 0
        if Pl > gp or pl * ub > Ph or pl * ub > gp or ph * (1 - ub) < -Ph or ph < -w:
            return 'infeasible', Fr(-1), info
        # step 1
        C0 = a0 * (w + ub * pl - Ph - D * (ph + w))
        j0 = None
        for j in range(1, N + 1):
            if self.H_lo[j] >= C0:
                j0 = j
                break
        if j0 is None:
            return 'fail: no node with H(q_j)- >= C0', None, info
        s0 = self.Htp_lo[j0]
        h1 = s0 + w
        if not h1 > 0:
            return 'fail: h1 <= 0', None, info
        Delta0 = (self.H_hi[j0] - C0) / h1
        psi = self.psi_hull(j0)
        # step 2
        P1 = min(max(Pl, pl * ub), gm)
        if P1 < pl * ub:
            return 'fail: P1 < pl u_b', None, info
        a1, b1 = self.enclose_u1(P1, pl)
        Psi_pl = self.env_at_y(psi, pl)
        IL = (psi.integral_up(Fr(0), a1) if a1 > 0 else Fr(0)) + (ub - b1) * Psi_pl
        if b1 > a1:
            IL += (b1 - a1) * max(Psi_pl, self.env_at_y(psi, self.phis_lo(b1)))
        # step 3
        PK = max(min(Ph, gm), pl * ub)
        if PK == gm:
            ak, bk = ub, ub
        else:
            ak, bk = self.enclose_u1(PK, pl)
        t0 = iexp(-1 - s0 / w)
        if bk == 0:
            Kint = Fr(0)
        elif bk <= t0.lof():
            Kint = (-bk * s0 - w * bk * ilog(bk)).hif()
        else:
            Kint = (w * t0).hif()
        K = Kint + (ub - ak) * max(pl - s0, Fr(0)) + (gp - gm)
        # step 4
        a2, b2 = self.enclose_u2(P1, ph)
        Hh_ph = self.env_at_y(self.full, ph)
        IR2 = (a2 - ub) * Hh_ph + self.full.integral_up(b2, Fr(1))
        if b2 > a2:
            IR2 += (b2 - a2) * max(Hh_ph, self.env_at_y(self.full, self.phis_lo(b2)))
        IRs = self.IRs
        # step 5
        y_sp = self.phis_ub.hif()
        y_top = min(ph, y_sp)
        jA = None
        for j in range(N, 0, -1):
            if self.Htp_lo[j] >= y_top:
                jA = j
                break
        if jA is None or jA < self.jA0:
            return 'fail: jA undefined or < jA0', None, info
        if jA >= N:
            return 'fail: jA = N (no cell >= jA)', None, info
        d2A = self.d2suf[jA]
        jB = None
        for j in range(N, 0, -1):
            if self.Htp_lo[j] >= ph:
                jB = j
                break
        qB = q[jB] if jB is not None else a0
        kappa = alpha * K / h1                       # exact
        theta = kappa * d2A                          # = kappa / kappa2, kappa2 = 1/d2A, exact
        if theta > 1:
            return 'fail: theta > 1', None, info
        m_b = max(gm - P1, Fr(0))
        # step 6
        sb2 = ilog(b2).hif() if b2 != 1 else Fr(0)
        qR = q[self.full.j[self.full.piece(sb2)]]
        qmin = q[j0]
        slope = -qmin + (1 - theta) * qR + theta * qB
        dvar = max(slope, Fr(0)) * (Ph - P1)
        # step 7
        Lip = max(y_sp, ph) + w
        E_grid = Lip * D * max(ph - y_c, Fr(0))
        E_cap = self.Ecap_const + D * (ph + w) * (y_c + w)
        if jB is not None and jB >= self.jA0 and jB < N:
            ratio = min(d2A / self.d2suf[jB], Fr(1))  # kappa2h / kappa2
        else:
            ratio = Fr(0)
        E_high = (1 - ratio) * (gp - P1) * max(ph - y_sp, Fr(0))
        # step 8
        U = (IL + Delta0 * K + (1 - theta) * IR2 + theta * (IRs - qB * m_b) + dvar
             + kappa * (E_grid + E_cap + E_high))
        info = dict(j0=j0, C0=C0, P1=P1, IL=IL, K=K, Delta0=Delta0, IR2=IR2, IRs=IRs, jA=jA, jB=jB, theta=theta,
                    kappa=kappa, dvar=dvar, slope=slope, qR=qR, E_grid=E_grid, E_cap=E_cap, E_high=E_high,
                    u1=(a1, b1), u2=(a2, b2))
        return 'ok', U, info

    def run(self):
        c = self.cert
        try:
            ok = self.data_checks()
        except Reject as e:
            self.log('  data checks aborted at %s' % e)
            return False, None, 0
        except ArithmeticError as e:
            self.fail('arithmetic failure in data checks: %s' % e)
            return False, None, 0
        if not ok:
            self.log('  data checks failed; boxes are still evaluated where possible')
            if self.stop_on_data_fail or not hasattr(self, 'd2suf'):
                return False, None, 0
        w = c['w']
        y_c = c['y_c']
        self.IRs = self.full.integral_up(c['u_b'], Fr(1))
        ecap = ((IV.of(y_c * y_c - w * w) / 2) + w * w * (1 - iexp(-1 - y_c / w)))
        self.Ecap_const = ecap.hif()
        # traverse the tree
        root = (Fr(0), c['G_up'], -w, c['P_up'])
        stack = [(c['tree'], root, '')]
        nleaf = 0
        ninf = 0
        worst = None
        worst_leaf = None
        nfail = 0
        rows = []
        while stack:
            node, (Pl, Ph, pl, ph), path = stack.pop()
            if node == 'L':
                nleaf += 1
                try:
                    st, U, info = self.box_U(Pl, Ph, pl, ph)
                except ArithmeticError as e:
                    st, U, info = 'fail: arithmetic %s' % e, None, {}
                if st == 'infeasible':
                    ninf += 1
                if U is None or U >= 0:
                    nfail += 1
                    if nfail <= 20:
                        self.fail('K10: leaf %s box P[%s, %s] p[%s, %s]: %s%s' % (
                            path or 'root', dec(Pl), dec(Ph), dec(pl), dec(ph), st,
                            '' if U is None else ', U(B) <= %s' % dec(U)))
                if U is not None and (worst is None or U > worst):
                    worst = U
                    worst_leaf = (path, Pl, Ph, pl, ph, info)
                rows.append((path, Pl, Ph, pl, ph, st, U, info))
                continue
            ax, c1, c2 = node
            if ax == 'P':
                m = (Pl + Ph) / 2
                stack.append((c2, (m, Ph, pl, ph), path + 'P2'))
                stack.append((c1, (Pl, m, pl, ph), path + 'P1'))
            else:
                m = (pl + ph) / 2
                stack.append((c2, (Pl, Ph, m, ph), path + 'p2'))
                stack.append((c1, (Pl, Ph, pl, m), path + 'p1'))
        self.rows = rows
        self.log('  K10: %d leaves (%d infeasible by step 0), %d failing' % (nleaf, ninf, nfail))
        if worst_leaf is not None:
            path, Pl, Ph, pl, ph, info = worst_leaf
            self.log('  worst leaf %s: P[%s, %s] p[%s, %s], U(B) <= %s' % (
                path or 'root', dec(Pl, 10), dec(Ph, 10), dec(pl, 10), dec(ph, 10), dec(worst, 8)))
            if info and self.verbose:
                for k in sorted(info):
                    v = info[k]
                    if isinstance(v, Fr):
                        v = dec(v, 10)
                    elif isinstance(v, tuple):
                        v = '(%s)' % ', '.join(dec(t, 12) for t in v)
                    self.log('      %s = %s' % (k, v))
        accept = (not self.fails) and nfail == 0
        return accept, worst, nleaf


# ----------------------------------------------------------------------------------------------
# Self tests of the arithmetic, jets and hull (no certificate needed)
# ----------------------------------------------------------------------------------------------
def selftest():
    rng = random.Random(20261118)
    bad = 0

    def contains(iv, x):
        return iv.lof() <= x <= iv.hif()

    def chk(cond, msg):
        nonlocal bad
        if not cond:
            bad += 1
            print('SELFTEST FAIL:', msg)
    # exp/log basic identities
    chk(contains(ilog(Fr(1)), Fr(0)), 'log 1')
    l2 = ilog(Fr(2))
    lo, hi = _ln2(P + 64)
    chk(l2.lo <= (hi >> 64) + 1 and l2.hi >= (lo >> 64) - 1, 'log 2 vs ln2 series')
    # ln 2 decimal digits (exact value 0.693147180559945309417232121458176568...)
    ref = Fr(693147180559945309417232121458176568, 10 ** 36)
    chk(abs(l2.lof() - ref) < Fr(1, 10 ** 35), 'ln2 digits')
    e1 = iexp(Fr(1))
    refe = Fr(2718281828459045235360287471352662497757, 10 ** 39)
    chk(abs(e1.lof() - refe) < Fr(1, 10 ** 38), 'e digits')
    for _ in range(300):
        x = Fr(rng.randint(1, 10 ** 12), rng.randint(1, 10 ** 12))
        y = Fr(rng.randint(1, 10 ** 12), rng.randint(1, 10 ** 12))
        lx, ly, lxy = ilog(x), ilog(y), ilog(x * y)
        s = lx + ly
        chk(not (s.hi < lxy.lo or lxy.hi < s.lo), 'log x + log y = log xy')
        chk(lxy.hi - lxy.lo < (1 << 20), 'log width')
        t = Fr(rng.randint(-40 * 10 ** 9, 40 * 10 ** 9), 10 ** 9)
        et = iexp(t)
        back = ilog(et)
        chk(contains(back, t), 'log(exp(t)) contains t (t=%s)' % dec(t))
        e2 = iexp(t / 2)
        sq = e2 * e2
        chk(not (sq.hi < et.lo or et.hi < sq.lo), 'exp(t/2)^2 = exp(t)')
    # an independent check of log by its own series around 1: log(1+h) for tiny h
    h = Fr(1, 10 ** 30)
    v = ilog(1 + h)
    approx = h - h * h / 2 + h ** 3 / 3
    chk(abs(v.lof() - approx) < Fr(1, 10 ** 70), 'log(1+h)')
    # jets: derivative of log(1+q)/q * exp(q) vs exact rational difference quotient
    for _ in range(20):
        q0 = Fr(rng.randint(1, 10 ** 6), 10 ** 6 + 1)
        J = Jet.var(IV.of(q0), 3)
        f = jexp(J) * jlog(J + 1) / J
        hh = Fr(1, 10 ** 20)

        def fv(qq):
            Q = IV.of(qq)
            return iexp(Q) * ilog(Q + 1) / Q
        fd = (fv(q0 + hh) - fv(q0 - hh)) / (2 * hh)
        d1 = f.deriv(1)
        chk(abs(fd.lof() - d1.lof()) < Fr(1, 10 ** 30), 'jet first derivative')
        fd2 = (fv(q0 + hh) - 2 * fv(q0) + fv(q0 - hh)) / (hh * hh)
        chk(abs(fd2.lof() - f.deriv(2).lof()) < Fr(1, 10 ** 10), 'jet second derivative')
    # hull vs brute force
    for _ in range(20):
        n = rng.randint(2, 60)
        ds = sorted(set(Fr(rng.randint(1, 10 ** 6), 10 ** 6) for _ in range(n)))
        lines = [(Fr(rng.randint(-10 ** 6, 10 ** 6), 10 ** 6), d, i) for i, d in enumerate(ds)]
        H = Hull(lines)
        for _ in range(50):
            s = Fr(rng.randint(-10 ** 8, 10 ** 8), 10 ** 6)
            bf = max(cc + dd * s for cc, dd, _ in lines)
            chk(H.value(s) == bf, 'hull value')
        # integral against a fine Riemann-type bracket (monotone pieces): crude sanity only
        ta, tb = Fr(1, 100), Fr(1, 2)
        up = H.integral_up(ta, tb)
        lo_b = H.I(tb, False) - H.I(ta, True)
        chk(lo_b <= up and up - lo_b < Fr(1, 10 ** 60), 'hull integral bracket')
    print('selftest: %s' % ('PASS' if bad == 0 else '%d FAILURES' % bad))
    return bad == 0


def main(argv=None):
    ap = argparse.ArgumentParser(description='checkD_C: independent Lemma D certificate checker')
    ap.add_argument('certs', nargs='*')
    ap.add_argument('--heights', choices=('right', 'mid'), default='right')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('-v', '--verbose', action='store_true')
    ap.add_argument('--leaves', help='write per-leaf U(B) upper bounds to this file')
    a = ap.parse_args(argv)
    if a.selftest:
        if not selftest():
            return 3
        if not a.certs:
            return 0
    allok = True
    out = []
    for path in a.certs:
        print('== %s  (heights: %s)' % (path, a.heights))
        try:
            cert = load_cert(path)
        except (CertError, ValueError, OSError) as e:
            print('  REJECT (format): %s' % e)
            allok = False
            continue
        ch = Checker(cert, heights=a.heights, verbose=a.verbose)
        acc, worst, nleaf = ch.run()
        print('  RESULT %s  leaves=%d  worst U(B) <= %s' % ('ACCEPT' if acc else 'REJECT', nleaf,
                                                           dec(worst, 8) if worst is not None else 'n/a'))
        if worst is not None:
            print('  worst U(B) exact upper bound = %s' % worst)
        allok &= acc
        if a.leaves and hasattr(ch, 'rows'):
            for (pth, Pl, Ph, pl, ph, st, U, _info) in ch.rows:
                out.append('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (path, pth or 'root', Pl, Ph, pl, ph, st,
                                                               'None' if U is None else dec(U, 10)))
    if a.leaves:
        with open(a.leaves, 'w') as f:
            f.write('\n'.join(out) + '\n')
    return 0 if allok else 1


if __name__ == '__main__':
    sys.exit(main())
