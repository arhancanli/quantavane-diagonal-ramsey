"""Checker A for Lemma D (CERT_DESIGN.md): robust two-region level (i) certificate for one ZBS control.

Exact rationals (fractions.Fraction) and outward-rounded dyadic intervals (ivA.py, copied unchanged from
../../ramsey-zbs/code/checkA/ivA.py, SHA-256 f6fe4408...579ee8).  No floating point is used for any decision.

Statement checked (CERT_DESIGN.md, Lemma D): for every admissible (phi, eta) of Theorem A (PROOF.md) with the scale
grid {u_b + k D, k = 0..(1-u_b)/D} (plus any scales below u_b), V_A(phi, eta) <= max over the certificate's boxes
of U(box) < 0.  The checker recomputes every U(box) from the certificate's rational data and verifies that the box
tree covers the rectangle [0, G_up] x [-w, P_up], which contains every feasible (Phi_b, p_b).
"""
if not __debug__:
    raise SystemExit('checker A uses assert statements; refusing to run under python -O')
import json
import os
import sys
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ivA                      # noqa: E402
from ivA import Iv              # noqa: E402

ONE = ivA.ONE


def lo(v): return Fr(v.lo, ONE)
def hi(v): return Fr(v.hi, ONE)
def I(x): return Iv.q(x)


def logI(v):
    v = v if isinstance(v, Iv) else I(v)
    return ivA.log(v)


def expI(v):
    v = v if isinstance(v, Iv) else I(v)
    a = ivA._exp_rat(lo(v))
    b = a if v.hi == v.lo else ivA._exp_rat(hi(v))
    return Iv(a.lo, b.hi)


def hull(*vs):
    return Iv(min(v.lo for v in vs), max(v.hi for v in vs))


def cup(x, den=1 << 90):
    """a rational >= x (x a Fraction), with denominator den."""
    return Fr(-((-x.numerator * den) // x.denominator), den)


def cdown(x, den=1 << 90):
    return Fr((x.numerator * den) // x.denominator, den)


class Ctl:
    """H(q) = q M(q) + w q and its derivatives for the ZBS control (p, mu, w, beta, x), on rational points or on
    intervals of q.  Binding branch (A > B): Ht = p (1-q) l + ((1-p)/beta) q log Z, Z = (U - p e^{beta A})/(1-p);
    non-binding (A <= B): Ht = q B.  Ht = q M.  Both branches agree to first order at A = B (CERT_DESIGN.md D0)."""

    def __init__(self, p, mu, w, beta, x):
        self.p, self.mu, self.w, self.beta, self.x = p, mu, w, beta, x
        self.lp, self.lmu, self.lx = logI(p), logI(mu), logI(x)

    def G0(self, q):
        p, mu, w, beta = self.p, self.mu, self.w, self.beta
        qv = q if isinstance(q, Iv) else I(q)
        l = self.lp + I(w) * logI(1 - qv) - self.lx
        return qv * self.lp + I(beta) * (1 - qv) * l - I(beta * w) * qv * (self.lmu - logI(qv))

    def dG0(self, q):
        """G0'(q) = log p - beta l(q) - beta w (log mu - log q)."""
        w, beta = self.w, self.beta
        qv = q if isinstance(q, Iv) else I(q)
        l = self.lp + I(w) * logI(1 - qv) - self.lx
        return self.lp - I(beta) * l - I(beta * w) * (self.lmu - logI(qv))

    def jet(self, q, order=2):
        """returns (Ht, Ht', Ht'') enclosures over q (point or interval); raises if q not certified in D."""
        p, mu, w, beta = self.p, self.mu, self.w, self.beta
        qv = q if isinstance(q, Iv) else I(q)
        lq = logI(qv)
        l = self.lp + I(w) * logI(1 - qv) - self.lx
        A = (1 - qv) / qv * l
        B = I(w) * (self.lmu - lq)
        outs = []
        if A.lo <= B.hi:                         # non-binding branch possible
            outs.append((qv * B, B - I(w), I(-w) / qv))
        if A.hi > B.lo:                          # binding branch possible
            bA, bB = I(beta) * A, I(beta) * B
            E, U = expI(bA), expI(bB)
            Z = (U - I(p) * E) / I(1 - p)
            if Z.lo <= 0:
                raise ArithmeticError('q not certified in D')
            Ap = (-l - I(w) * qv) / (qv * qv)
            App = (I(w) * qv * qv / (1 - qv) + 2 * l + I(2 * w) * qv) / (qv * qv * qv)
            Bp = I(-w) / qv
            Up = I(beta) * Bp * U
            Upp = I(beta * w * (1 + beta * w)) * U / (qv * qv)
            Ep = I(beta) * Ap * E
            Epp = I(beta) * (App + I(beta) * Ap * Ap) * E
            Zp = (Up - I(p) * Ep) / I(1 - p)
            Zpp = (Upp - I(p) * Epp) / I(1 - p)
            r1 = Zp / Z
            Ht = I(p) * (1 - qv) * l + I((1 - p) / beta) * qv * logI(Z)
            Ht1 = I(p) * (-l - I(w)) + I((1 - p) / beta) * (logI(Z) + qv * r1)
            Ht2 = I(p * w) / (1 - qv) + I((1 - p) / beta) * (2 * r1 + qv * (Zpp / Z - r1 * r1))
            outs.append((Ht, Ht1, Ht2))
        return tuple(hull(*[o[k] for o in outs]) for k in range(3))


def build_lines(C, qs):
    """node heights h_j (rational, rounded up) with H(q) - q(w+y) <= max_j (h_j - q_j (w+y)) for q in Q, all y;
    cells use the tangent at their right end.  Also returns per-node enclosures of H, Ht'."""
    w = C.w
    N = len(qs) - 1
    Hn, D1 = [None] * (N + 1), [None] * (N + 1)
    for j in range(1, N + 1):
        Ht, Ht1, _ = C.jet(qs[j], order=1)
        Hn[j] = Ht + I(w * qs[j]); D1[j] = Ht1
    h = [None] * (N + 1)
    for j in range(N + 1):
        cands = []
        if j >= 1: cands.append(hi(Hn[j]))
        if j <= N - 1:
            Hp1 = Hn[j + 1]; slo = lo(D1[j + 1]) + w            # lower bound of H'(q_{j+1})
            cands.append(hi(Hp1 - I(slo) * I(qs[j + 1] - qs[j])))
        h[j] = cup(max(cands))
    return h, Hn, D1


class Env:
    """upper hull of lines c_k + d_k s (d increasing) for s <= 0; exact rational breakpoints."""

    def __init__(self, c, d):
        st = []                                   # indices on hull, breakpoints between consecutive
        for k in range(len(c)):
            while st:
                if len(st) >= 2:
                    i, j = st[-2], st[-1]
                    # j redundant if intersection(i,k) <= intersection(i,j)
                    if (c[i] - c[k]) * (d[j] - d[i]) <= (c[i] - c[j]) * (d[k] - d[i]):
                        st.pop(); continue
                break
            st.append(k)
        self.c = [c[k] for k in st]; self.d = [d[k] for k in st]
        self.bp = [(self.c[i] - self.c[i + 1]) / (self.d[i + 1] - self.d[i]) for i in range(len(st) - 1)]

    def at(self, s):
        """max over lines at rational s (exact)."""
        return max(ci + di * s for ci, di in zip(self.c, self.d))

    def piece(self, sI):
        """index of the hull piece containing every s in the interval sI; raises if ambiguous."""
        k = 0
        while k < len(self.bp) and self.bp[k] < lo(sI):
            k += 1
        if k < len(self.bp) and self.bp[k] <= hi(sI):
            raise ArithmeticError('envelope breakpoint inside log-enclosure')
        return k

    def integral(self, ta, tb):
        """enclosure of int_{ta}^{tb} max_k (c_k + d_k log t) dt, 0 <= ta < tb <= 1 rational."""
        assert 0 <= ta < tb <= 1
        def F(k, t_iv, logt_iv):
            return t_iv * (I(self.c[k]) + I(self.d[k]) * (logt_iv - 1))
        sb = logI(tb); kb = self.piece(sb)
        if ta == 0:
            ka = 0; left = None
        else:
            sa = logI(ta); ka = self.piece(sa); left = (I(ta), sa)
        tot = I(0)
        for k in range(ka, kb + 1):
            if k == ka and left is not None: a = F(k, left[0], left[1])
            elif k == ka: a = I(0)
            else:
                sg = self.bp[k - 1]; a = F(k, expI(I(sg)), I(sg))
            if k == kb: b = F(k, I(tb), sb)
            else:
                sg = self.bp[k]; b = F(k, expI(I(sg)), I(sg))
            tot = tot + (b - a)
        return tot


def gsat(w, u): return I(-w) * I(u) * logI(u)
def phis(w, u): return I(-w) * (1 + logI(u))


def switch_left(w, ub, Phib, pb, iters=70):
    """enclosure [a, b] of u1 for Phi* = min(g, Phib - pb (ub - .)) on [0, ub], requiring pb*ub <= Phib < g(ub):
    f = g - line is concave, f(0+) <= 0 < f(ub), so f <= 0 on (0, u1] and f > 0 on (u1, ub]."""
    f = lambda u: gsat(w, u) - I(Phib - pb * (ub - u))
    a, b = Fr(0), Fr(ub)
    for _ in range(iters):
        m = (a + b) / 2
        v = f(m)
        if v.hi <= 0: a = m
        elif v.lo > 0: b = m
        else: break
    return a, b


def switch_right(w, ub, Phib, pb, iters=70):
    """enclosure [a, b] of u2 for Phi** = min(g, Phib + pb (. - ub)) on [ub, 1], requiring Phib < g(ub) and
    Phib + pb (1 - ub) >= 0: f = line - g is convex, f(ub) < 0 <= f(1), so f <= 0 on [ub, u2], > 0 after."""
    f = lambda u: I(Phib + pb * (u - ub)) - gsat(w, u)
    a, b = Fr(ub), Fr(1)
    for _ in range(iters):
        m = (a + b) / 2
        v = f(m)
        if v.hi <= 0: a = m
        elif v.lo > 0: b = m
        else: break
    return a, b


class LemmaD:
    def __init__(self, cert):
        g = lambda k: Fr(cert[k])
        self.cert = cert
        p, mu, w, beta, x = (Fr(cert['control'][k]) for k in ('p', 'mu', 'w', 'beta', 'x'))
        assert 0 < p < 1 and 0 < mu < 1 and w > 0 and 0 < beta < 1 and 0 < x < p, 'control ranges'
        assert x < lo(expI(I(w) * logI(1 - mu))), 'x < (1 - mu)^w'      # Theorem A / ZBS Step 6 (d* < 1)
        self.p, self.mu, self.w, self.beta, self.x = p, mu, w, beta, x
        C = self.C = Ctl(p, mu, w, beta, x)
        a_cut, a_hi, alpha = g('a_cut'), g('a_hi'), g('alpha')
        assert 0 < a_cut < a_hi < mu, 'a_cut < a_hi < mu'
        assert C.G0(a_cut).lo >= 0, 'G0(a_cut) >= 0'
        assert C.G0(a_hi).hi < 0, 'G0(a_hi) < 0'
        assert C.G0(mu).hi < 0, 'G0(mu) < 0 (mu in Q: Q nonempty, Lemma C (ii))'
        d = C.dG0(a_hi)
        assert d.hi < 0, "G0'(a_hi) < 0"
        assert hi(I(beta) / (-d)) <= alpha, "alpha >= beta / |G0'(a_hi)|"
        self.a0, self.alpha = a_cut, alpha
        ub, Dp = g('u_b'), g('Dplus')
        assert 0 < ub < 1 and Dp > 0, 'u_b, D'
        n = (1 - ub) / Dp
        assert n.denominator == 1 and n >= 1, '(1 - u_b)/D must be a positive integer'
        self.ub, self.Dp = ub, Dp
        qs = [Fr(t) for t in cert['qgrid']]
        assert qs[0] == a_cut and qs[-1] == mu and all(qs[i] < qs[i + 1] for i in range(len(qs) - 1)), 'q grid'
        assert qs[1] >= a_hi, 'first interior node inside D'
        self.qs = qs
        self.h, self.Hn, self.D1 = build_lines(C, qs)
        # second-derivative bounds per cell, for cells from index jA0 on
        self.jA0 = int(cert['jA0'])
        self.d2 = {}
        for i in range(self.jA0, len(qs) - 1):
            _, _, h2 = C.jet(Iv(I(qs[i]).lo, I(qs[i + 1]).hi))
            self.d2[i] = max(abs(lo(h2)), abs(hi(h2)))
        # cap level: y_c >= Ht'(mu)
        yc = g('y_c')
        assert hi(self.D1[-1]) <= yc and yc > -w, "y_c >= Ht'(mu)"
        self.yc = yc
        ycI = I(yc)
        self.Ecap0 = hi((ycI * ycI - I(w * w)) / 2 + I(w * w) * (1 - expI(I(-1) - ycI / I(w))))
        # envelopes
        self.cw = [self.h[j] for j in range(len(qs))]
        self.dw = [w * qs[j] for j in range(len(qs))]
        self.envall = Env(self.cw, self.dw)
        self.gub = gsat(w, ub)
        self.phis_ub = phis(w, ub)
        assert lo(self.phis_ub) >= self.yc, 'y_sp = phi_s(u_b) >= y_c (cap and high bands disjoint)'
        self.IRs = hi(self.envall.integral(ub, Fr(1)))
        self._suffix = {}

    def env_from(self, j0):
        if j0 not in self._suffix:
            self._suffix[j0] = Env(self.cw[j0:], self.dw[j0:])
        return self._suffix[j0]

    def Hplus(self, env, y):
        """max_j (h_j - q_j (w + y)) for rational y, lines of env (s = -(w+y)/w)."""
        return env.at(-(self.w + y) / self.w)

    def qA_of(self, y):
        """largest node j with Ht'(q_j) >= y certified (then qhat(y) >= q_j); None if none."""
        best = None
        for j in range(1, len(self.qs)):
            if lo(self.D1[j]) >= y: best = j
            else: break
        return best

    def box(self, Pl, Ph, pl, ph):
        """upper bound U for every feasible (Phi_b, p_b) in [Pl,Ph] x [pl,ph] (CERT_DESIGN.md, Lemma D, D1-D8);
        returns (U, info), or (None, reason) if this box cannot be bounded."""
        w, ub, Dp, a0, alpha = self.w, self.ub, self.Dp, self.a0, self.alpha
        gl, gh = lo(self.gub), hi(self.gub)
        if Pl > gh: return Fr(-1), 'infeasible: Phi_b > g(u_b)'
        if pl * ub > Ph or pl * ub > gh: return Fr(-1), 'infeasible: p_b > Phi_b/u_b'
        if ph * (1 - ub) < -Ph: return Fr(-1), 'infeasible: p_b < -Phi_b/(1-u_b)'
        if ph < -w: return Fr(-1), 'infeasible: p_b < -w'
        # D3: C >= C0 - G for every configuration in the box
        C0 = a0 * (w + ub * pl - Ph - Dp * (ph + w))
        j0 = next((j for j in range(1, len(self.qs)) if lo(self.Hn[j]) >= C0), None)
        if j0 is None: return None, 'no node with H >= C0'
        h1 = lo(self.D1[j0]) + w
        if h1 <= 0: return None, 'H not increasing at q0'
        s0 = lo(self.D1[j0])
        Dl0 = (hi(self.Hn[j0]) - C0) / h1
        env0 = self.env_from(j0)
        # D7: all Phi-dependent terms at P1, the smallest feasible Phi_b of the box (clipped below g(u_b))
        P1 = min(max(Pl, pl * ub), gl)
        if P1 < pl * ub: return None, 'P1 < pl u_b (box straddles g(u_b) too widely)'
        # D4/D5 left: int_0^{u_b} Psi0+(phi*) at (P1, pl); u1 in [a1, b1]
        a1, b1 = switch_left(w, ub, P1, pl)
        F0p = self.Hplus(env0, pl)
        lb1 = logI(b1)
        v_b1 = max(hi(I(ck) + I(dk) * lb1) for ck, dk in zip(env0.c, env0.d))
        IL = (hi(env0.integral(Fr(0), a1)) if a1 > 0 else Fr(0)) + (b1 - a1) * max(F0p, v_b1) + (ub - b1) * F0p
        # K = int_0^{u_b} (phi* - s0)_+ at (min(Ph, gl), pl) (nondecreasing in Phi_b) + (gh - gl)
        PK = min(Ph, gl)
        if PK < pl * ub: PK = pl * ub
        ak, bk = switch_left(w, ub, PK, pl) if PK < gl else (Fr(ub), Fr(ub))
        t0 = expI(I(-1) - I(s0) / I(w))                 # (phi_s - s0)_+ > 0 iff u < t0
        if bk > 0 and lo(t0) >= bk:
            Kint = hi(I(-bk * s0) - I(w) * I(bk) * logI(bk))
        else:
            Kint = hi(I(w) * t0)
        Kv = Kint + (ub - ak) * max(pl - s0, Fr(0)) + (gh - gl)
        # D5 right, majorised: int_{u_b}^1 Hhat+(phi**) at (P1, ph); u2 in [a2, b2]
        a2, b2 = switch_right(w, ub, P1, ph)
        Fph = self.Hplus(self.envall, ph)
        lb2 = logI(b2)
        v_b2 = max(hi(I(ck) + I(dk) * lb2) for ck, dk in zip(self.envall.c, self.envall.d))
        IR2 = (a2 - ub) * Fph + (b2 - a2) * max(Fph, v_b2) + (hi(self.envall.integral(b2, Fr(1))) if b2 < 1 else 0)
        # D6: drop levels split at y_c (cap) and y_sp = phi_s(u_b)+ (high band, where m <= m_b);
        # slope condition on [y_c, y_top], y_top = min(ph, y_sp): qhat(y_top) >= q_A, |Ht''| <= 1/kappa2 on cells >= jA
        ysp = hi(self.phis_ub)
        ytop = min(ph, ysp)
        jA = self.qA_of(ytop)
        if jA is None or jA < self.jA0: return None, 'q_A below jA0'
        kap2 = 1 / max(self.d2[i] for i in range(jA, len(self.qs) - 1))
        jB = self.qA_of(ph)
        qB = self.qs[jB] if jB is not None else self.a0           # qhat(p_b) >= qhat(ph) >= qB
        kap = alpha * Kv / h1
        th = kap / kap2
        if th > 1: return None, 'theta > 1'
        mb = max(gl - P1, Fr(0))
        # D7: Phi-variation of T: dT/dPhi <= -q_min(env0) + (1-th) qR + th qB; qR = largest active slope of Hhat+ at
        # drift phi_s(b2) (the hull piece at s = hi(log b2))
        k = 0
        while k < len(self.envall.bp) and self.envall.bp[k] < hi(lb2): k += 1
        qR = self.envall.d[k] / w
        slope = -env0.d[0] / w + (1 - th) * qR + th * qB
        dvar = max(slope, Fr(0)) * (Ph - P1)
        # D6/D8 errors: grid (middle band), cap band, high band (m <= m_b there)
        Lip = max(hi(self.phis_ub), ph) + w
        Egrid = Lip * Dp * max(ph - self.yc, Fr(0))
        Ecap = self.Ecap0 + Dp * (ph + w) * (self.yc + w)
        # high band: the Q-increment there is >= kappa2h * drop (slope bound on [q_jB, mu]), so only the fraction
        # (1 - kappa2h/kappa2) of kappa * m_b * (ph - y_sp)_+ is left over (CERT_DESIGN.md D6)
        kap2h = 1 / max(self.d2[i] for i in range(jB, len(self.qs) - 1)) if (jB is not None and jB >= self.jA0) else Fr(0)
        if kap2h > kap2: kap2h = kap2
        Ehigh = (1 - kap2h / kap2) * (gh - P1) * max(ph - ysp, Fr(0))
        U = IL + Dl0 * Kv + (1 - th) * IR2 + th * (self.IRs - qB * mb) + dvar + kap * (Egrid + Ecap + Ehigh)
        return U, dict(j0=j0, jA=jA, kEhigh=float(kap * Ehigh), th=round(float(th), 4), K=float(Kv), IL=float(IL), IR2=float(IR2),
                       dvar=float(dvar), kEcap=float(kap * Ecap), slope=round(float(slope), 5))


def walk(tree, rect):
    """yield leaf rectangles of a bisection tree: tree = 'L' or ['P'|'p', left, right] (split Phi or p at midpoint)."""
    stack = [(tree, rect)]
    while stack:
        t, (Pl, Ph, pl, ph) = stack.pop()
        if t == 'L':
            yield (Pl, Ph, pl, ph)
        else:
            ax, a, b = t
            if ax == 'P':
                m = (Pl + Ph) / 2
                stack.append((a, (Pl, m, pl, ph))); stack.append((b, (m, Ph, pl, ph)))
            else:
                m = (pl + ph) / 2
                stack.append((a, (Pl, Ph, pl, m))); stack.append((b, (Pl, Ph, m, ph)))


def check(cert, verbose=True):
    L = LemmaD(cert)
    w, ub = L.w, L.ub
    Gup, Pup = Fr(cert['G_up']), Fr(cert['P_up'])
    assert Gup >= hi(L.gub), 'G_up >= g(u_b)'
    assert Pup >= hi(I(-w) * logI(ub)), 'P_up >= -w log u_b'
    rect = (Fr(0), Gup, -w, Pup)
    worst = None; n = 0
    for bx in walk(cert['tree'], rect):
        U, info = L.box(*bx)
        n += 1
        assert U is not None, 'box %s failed: %s' % ([float(t) for t in bx], info)
        assert U < 0, 'box %s: U = %s >= 0 (%s)' % ([float(t) for t in bx], float(U), info)
        if worst is None or U > worst[0]: worst = (U, bx, info)
    if verbose:
        print('checker A: %d boxes, all U < 0; worst U = %.6e at Phi in [%.6g, %.6g], p in [%.6g, %.6g]  %s' % (
            n, float(worst[0]), *[float(t) for t in worst[1]], worst[2]))
    return worst


if __name__ == '__main__':
    cert = json.load(open(sys.argv[1]))
    check(cert)
    print('checker A ok')
