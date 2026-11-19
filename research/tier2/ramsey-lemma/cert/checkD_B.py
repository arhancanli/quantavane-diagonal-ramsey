"""Checker B for Lemma D (CERT_DESIGN.md): python-flint 0.9.0 Arb balls and fmpq.

INDEPENDENCE: checkers A and B are independent in ARITHMETIC only (own interval libraries, own evaluation of H, Ht',
Ht'', own hull and switch-point code). The assembly of the box bound U(B) (CERT_DESIGN.md D3-D7, spec in Section 4b)
is shared: this file implements the same formula as checkD_A.py, written by the same author; the gate-1 referee
covers that formula. Differences from checker A:
- H is evaluated through the representation of ZBS Lemma C (iii) (EP Sec. 5):
    H(q) = q B(q) + w q + (q/beta) [fbar(G0(q)/q) - f(log p)],  f(z) = p z + (1-p) log(1 - e^z),
  and its first and second derivatives come from Arb power series (arb_series), not from hand-written formulas;
- node heights: for each cell, the end tangent (left, with a right-derivative upper bound; or right, with a
  left-derivative lower bound) whose larger endpoint height is smaller; on the bank controls this is always the right
  tangent, so the heights coincide with A's, computed with different arithmetic; the first cell uses the right tangent;
- the upper envelope of the lines is built by gift-wrapping with a precomputed successor map (A uses a stack);
- switch points u1, u2 are enclosed by certified-sign bisection (linear in u, as in A).
The statement checked and the box tree format are those of checkD_A.py.
"""
import json
import sys

import flint
from flint import arb, arb_series, fmpq

flint.ctx.prec = 300


def Q(s):
    s = str(s)
    if '/' in s:
        n, d = s.split('/'); return fmpq(int(n), int(d))
    return fmpq(int(s))


def ub_q(a, den=2**90):
    """a rational >= every point of the ball a."""
    u = a.upper()
    m, e = u.man_exp()
    v = fmpq(int(m)) * (fmpq(2) ** int(e)) if e >= 0 else fmpq(int(m), 2 ** int(-e))
    return fmpq(-((-v.p * den) // v.q), den)


def lo_q(a, den=2**90):
    l = a.lower()
    m, e = l.man_exp()
    v = fmpq(int(m)) * (fmpq(2) ** int(e)) if e >= 0 else fmpq(int(m), 2 ** int(-e))
    return fmpq((v.p * den) // v.q, den)


def ball(lo, hi):
    """Arb ball containing the rational interval [lo, hi]."""
    a, b = arb(lo), arb(hi)
    return a.union(b)


class Ctl:
    def __init__(self, p, mu, w, beta, x):
        self.p, self.mu, self.w, self.beta, self.x = p, mu, w, beta, x
        self.lp, self.lmu, self.lx = arb(p).log(), arb(mu).log(), arb(x).log()
        self.flp = arb(p) * self.lp + arb(1 - p) * arb(1 - p).log()

    def G0_series(self, qs):
        p, w, beta = self.p, self.w, self.beta
        Aq = (1 - qs) / qs * (self.lp + arb(w) * (1 - qs).log() - self.lx)
        Bq = arb(w) * (self.lmu - qs.log())
        return qs * self.lp + arb(beta) * qs * (Aq - Bq), Bq, Aq

    def jet(self, qball):
        """(H, H', H'') over the ball qball (Arb), H = q M + w q; raises if not certified in D."""
        p, w, beta = self.p, self.w, self.beta
        qs = arb_series([qball, 1], prec=3)
        g0, Bq, Aq = self.G0_series(qs)
        c0 = g0.coeffs()[0]
        if not c0 < 0:
            raise ArithmeticError('q not certified in D')
        dAB = (Aq - Bq).coeffs()[0]
        outs = []
        base = qs * Bq + arb(w) * qs
        if not dAB > 0:                       # non-binding possible (A <= B): fbar = f(log p)
            outs.append(base)
        if not dAB <= 0:                      # binding possible
            z = g0 / qs
            fz = arb(p) * z + arb(1 - p) * (1 - z.exp()).log()
            outs.append(base + qs / arb(beta) * (fz - self.flp))
        res = []
        for k in range(3):
            vals = [o.coeffs()[k] if len(o.coeffs()) > k else arb(0) for o in outs]
            v = vals[0]
            for t in vals[1:]: v = v.union(t)
            res.append(v * (2 if k == 2 else 1))
        return tuple(res)


def successors(c, d):
    """gift-wrapping successor of each line on the upper envelope of lines j, j+1, ...: the line k > j whose
    intersection with line j is leftmost (ties: largest slope).  Depends only on j, so suffix hulls are chains."""
    n = len(c); nxt = [None] * n
    for j in range(n - 1):
        best, bk = None, None
        cj, dj = c[j], d[j]
        for k in range(j + 1, n):
            xs = (cj - c[k]) / (d[k] - dj)
            if best is None or xs <= best:
                best, bk = xs, k
        nxt[j] = (bk, best)
    return nxt


def env_suffix(nxt, j0):
    j = j0; pieces = []
    while nxt[j] is not None:
        k, xs = nxt[j]
        pieces.append((j, xs)); j = k
    pieces.append((j, None))
    return pieces


def env_integral(c, d, pieces, ta, tb):
    """enclosure of int_{ta}^{tb} max(c_k + d_k log t) dt with the hull pieces [(k, right bp)], 0<=ta<tb<=1."""
    def F(k, t, lt): return t * (arb(c[k]) + arb(d[k]) * (lt - 1))
    sb = arb(tb).log()
    sa = arb(ta).log() if ta > 0 else None
    tot = arb(0); left_bp = None
    for (k, bp) in pieces:
        # piece k on (left_bp, bp]
        if sa is not None and bp is not None and arb(bp) < sa:
            left_bp = bp; continue
        if sa is not None and bp is not None and not (arb(bp) > sa):
            raise ArithmeticError('ambiguous left piece')
        if left_bp is None or (sa is not None and arb(left_bp) < sa):
            a = F(k, arb(ta), sa) if sa is not None else arb(0)
        else:
            a = F(k, arb(left_bp).exp(), arb(left_bp))
        if bp is None or arb(bp) > sb:
            if bp is not None and not (arb(bp) > sb): raise ArithmeticError('ambiguous right piece')
            b = F(k, arb(tb), sb); tot += b - a; break
        if not (arb(bp) < sb): raise ArithmeticError('ambiguous right piece')
        b = F(k, arb(bp).exp(), arb(bp)); tot += b - a
        left_bp = bp
    return tot


class LemmaD:
    def __init__(self, cert):
        cc = cert['control']
        p, mu, w, beta, x = (Q(cc[k]) for k in ('p', 'mu', 'w', 'beta', 'x'))
        if not (0 < p < 1 and 0 < mu < 1 and w > 0 and 0 < beta < 1 and 0 < x < p): raise AssertionError('ranges')
        if not arb(x) < (arb(w) * arb(1 - mu).log()).exp(): raise AssertionError('x < (1-mu)^w')
        self.p, self.mu, self.w, self.beta, self.x = p, mu, w, beta, x
        C = self.C = Ctl(p, mu, w, beta, x)
        a_cut, a_hi, alpha = Q(cert['a_cut']), Q(cert['a_hi']), Q(cert['alpha'])
        if not (0 < a_cut < a_hi < mu): raise AssertionError('a_cut < a_hi < mu')
        g_cut = C.G0_series(arb_series([arb(a_cut), 1], prec=1))[0].coeffs()[0]
        g_hi = C.G0_series(arb_series([arb(a_hi), 1], prec=2))[0]
        if not g_cut >= 0: raise AssertionError('G0(a_cut) >= 0')
        if not g_hi.coeffs()[0] < 0: raise AssertionError('G0(a_hi) < 0')
        dg = g_hi.coeffs()[1]
        if not dg < 0: raise AssertionError("G0'(a_hi) < 0")
        if not arb(beta) / (-dg) <= arb(alpha): raise AssertionError("alpha >= beta/|G0'(a_hi)|")
        self.a0, self.alpha = a_cut, alpha
        ub, Dp = Q(cert['u_b']), Q(cert['Dplus'])
        n = (1 - ub) / Dp
        if not (0 < ub < 1 and Dp > 0 and n.q == 1 and n >= 1): raise AssertionError('u_b, D')
        self.ub, self.Dp = ub, Dp
        qs = [Q(t) for t in cert['qgrid']]
        if not (qs[0] == a_cut and qs[-1] == mu and all(qs[i] < qs[i + 1] for i in range(len(qs) - 1))):
            raise AssertionError('q grid')
        if not qs[1] >= a_hi: raise AssertionError('q_1 >= a_hi')
        self.qs = qs; N = len(qs) - 1
        Hn, D1 = [None] * (N + 1), [None] * (N + 1)
        for j in range(1, N + 1):
            H0, H1, _ = C.jet(arb(qs[j]))
            Hn[j], D1[j] = H0, H1                    # H and H' (H' = Ht' + w)
        self.Hn, self.D1 = Hn, D1
        # node heights: cell i in [q_i, q_{i+1}]: the end tangent with the smaller larger-endpoint height (left end
        # for i >= 1 with a right-derivative upper bound, or right end with a left-derivative lower bound),
        # tangent at right end for i = 0.
        h = [None] * (N + 1)
        def bump(j, v):
            h[j] = v if h[j] is None or v > h[j] else h[j]
        for i in range(N):
            Dq = arb(qs[i + 1] - qs[i])
            right = (ub_q(Hn[i + 1] - arb(lo_q(D1[i + 1])) * Dq), ub_q(Hn[i + 1]))     # tangent at q_{i+1}
            pair = right
            if i >= 1:
                left = (ub_q(Hn[i]), ub_q(Hn[i] + arb(ub_q(D1[i])) * Dq))            # tangent at q_i
                if max(left) < max(right): pair = left
            bump(i, pair[0]); bump(i + 1, pair[1])
        self.h = h
        self.c = [h[j] for j in range(N + 1)]
        self.d = [w * qs[j] for j in range(N + 1)]
        self.jA0 = int(cert['jA0'])
        self.d2 = {}
        for i in range(self.jA0, N):
            _, _, h2 = C.jet(ball(qs[i], qs[i + 1]))
            self.d2[i] = max(ub_q(h2), ub_q(-h2))
        yc = Q(cert['y_c'])
        Ht1mu = D1[N] - arb(w)
        if not (Ht1mu <= arb(yc) and yc > -w): raise AssertionError("y_c >= Ht'(mu)")
        self.yc = yc
        ycb = arb(yc)
        self.Ecap0 = ub_q((ycb * ycb - arb(w * w)) / 2 + arb(w * w) * (1 - (-1 - ycb / arb(w)).exp()))
        self.gub = -arb(w) * arb(ub) * arb(ub).log()
        self.phis_ub = -arb(w) * (1 + arb(ub).log())
        if not self.phis_ub >= arb(self.yc): raise AssertionError('y_sp >= y_c')
        self.nxt = successors(self.c, self.d)
        self.pieces_all = env_suffix(self.nxt, 0)
        self.IRs = ub_q(env_integral(self.c, self.d, self.pieces_all, ub, fmpq(1)))
        self._suf = {}

    def pieces_from(self, j0):
        if j0 not in self._suf:
            self._suf[j0] = env_suffix(self.nxt, j0)
        return self._suf[j0]

    def Fplus(self, j0, y):
        """max_{j >= j0} (h_j - q_j (w + y)), exact."""
        return max(self.h[j] - self.qs[j] * (self.w + y) for j in range(j0, len(self.qs)))

    def g(self, u): return -arb(self.w) * arb(u) * arb(u).log()

    def switch(self, f, a, b, it=70):
        """certified-sign bisection, linear in u: f <= 0 on [a, s], > 0 on (s, b]."""
        for _ in range(it):
            m = (a + b) / 2
            v = f(m)
            if v <= 0: a = m
            elif v > 0: b = m
            else: break
        return a, b

    def box(self, Pl, Ph, pl, ph):
        w, ub, Dp, a0, alpha = self.w, self.ub, self.Dp, self.a0, self.alpha
        gl, gh = lo_q(self.gub), ub_q(self.gub)
        if Pl > gh: return fmpq(-1), 'infeasible'
        if pl * ub > Ph or pl * ub > gh: return fmpq(-1), 'infeasible'
        if ph * (1 - ub) < -Ph: return fmpq(-1), 'infeasible'
        if ph < -w: return fmpq(-1), 'infeasible'
        C0 = a0 * (w + ub * pl - Ph - Dp * (ph + w))
        j0 = None
        for j in range(1, len(self.qs)):
            if self.Hn[j] >= arb(C0): j0 = j; break
        if j0 is None: return None, 'no q0'
        h1 = lo_q(self.D1[j0])
        if not h1 > 0: return None, 'H not increasing'
        s0 = lo_q(self.D1[j0] - arb(w))
        Dl0 = (ub_q(self.Hn[j0]) - C0) / h1
        P1 = min(max(Pl, pl * ub), gl)
        if P1 < pl * ub: return None, 'P1'
        pcs0 = self.pieces_from(j0)
        # left
        fL = lambda u: self.g(u) - arb(P1 - pl * (ub - u))
        a1, b1 = self.switch(fL, fmpq(0), ub)
        F0p = self.Fplus(j0, pl)
        lb1 = arb(b1).log()
        vb1 = max(ub_q(arb(self.h[j]) + arb(self.d[j]) * lb1) for j, _ in pcs0)
        IL = (ub_q(env_integral(self.c, self.d, pcs0, fmpq(0), a1)) if a1 > 0 else fmpq(0)) \
            + (b1 - a1) * max(F0p, vb1) + (ub - b1) * F0p
        # K
        PK = min(Ph, gl)
        if PK < pl * ub: PK = pl * ub
        if PK < gl:
            fK = lambda u: self.g(u) - arb(PK - pl * (ub - u))
            ak, bk = self.switch(fK, fmpq(0), ub)
        else:
            ak, bk = ub, ub
        t0 = (-1 - arb(s0) / arb(w)).exp()
        if bk > 0 and arb(bk) <= t0:
            Kint = ub_q(-arb(bk) * arb(s0) - arb(w) * arb(bk) * arb(bk).log())
        else:
            Kint = ub_q(arb(w) * t0)
        Kv = Kint + (ub - ak) * max(pl - s0, fmpq(0)) + (gh - gl)
        # right
        fR = lambda u: arb(P1 + ph * (u - ub)) - self.g(u)
        a2, b2 = self.switch(fR, ub, fmpq(1))
        Fph = self.Fplus(0, ph)
        lb2 = arb(b2).log()
        vb2 = max(ub_q(arb(self.h[j]) + arb(self.d[j]) * lb2) for j, _ in self.pieces_all)
        IR2 = (a2 - ub) * Fph + (b2 - a2) * max(Fph, vb2) + \
            (ub_q(env_integral(self.c, self.d, self.pieces_all, b2, fmpq(1))) if b2 < 1 else fmpq(0))
        # slope condition on [y_c, y_top], y_top = min(ph, y_sp), y_sp >= phi_s(u_b); high band uses m <= m_b
        ysp = ub_q(self.phis_ub)
        ytop = min(ph, ysp)
        def qa(y):
            jj = None
            for j in range(1, len(self.qs)):
                if self.D1[j] - arb(w) >= arb(y): jj = j
                else: break
            return jj
        jA = qa(ytop)
        if jA is None or jA < self.jA0: return None, 'jA'
        kap2 = 1 / max(self.d2[i] for i in range(jA, len(self.qs) - 1))
        jB = qa(ph)
        qB = self.qs[jB] if jB is not None else self.a0
        kap = alpha * Kv / h1
        th = kap / kap2
        if th > 1: return None, 'theta > 1'
        mb = max(gl - P1, fmpq(0))
        sh = ub_q(lb2)
        qR = None
        for (j, bp) in self.pieces_all:
            if bp is None or bp >= sh:
                qR = self.qs[j]; break
        slope = -self.qs[pcs0[0][0]] + (1 - th) * qR + th * qB
        dvar = max(slope, fmpq(0)) * (Ph - P1)
        Lip = max(ub_q(self.phis_ub), ph) + w
        Egrid = Lip * Dp * max(ph - self.yc, fmpq(0))
        Ecap = self.Ecap0 + Dp * (ph + w) * (self.yc + w)
        kap2h = fmpq(0)
        if jB is not None and jB >= self.jA0:
            kap2h = 1 / max(self.d2[i] for i in range(jB, len(self.qs) - 1))
        if kap2h > kap2: kap2h = kap2
        Ehigh = (1 - kap2h / kap2) * (gh - P1) * max(ph - ysp, fmpq(0))
        U = IL + Dl0 * Kv + (1 - th) * IR2 + th * (self.IRs - qB * mb) + dvar + kap * (Egrid + Ecap + Ehigh)
        return U, dict(j0=j0, jA=jA)


def walk(tree, rect):
    out = []
    def rec(t, r):
        Pl, Ph, pl, ph = r
        if t == 'L': out.append(r); return
        ax, a, b = t
        if ax == 'P':
            m = (Pl + Ph) / 2; rec(a, (Pl, m, pl, ph)); rec(b, (m, Ph, pl, ph))
        elif ax == 'p':
            m = (pl + ph) / 2; rec(a, (Pl, Ph, pl, m)); rec(b, (Pl, Ph, m, ph))
        else:
            raise AssertionError('bad tree node')
    rec(tree, rect)
    return out


def check(cert, verbose=True):
    L = LemmaD(cert)
    w, ub = L.w, L.ub
    Gup, Pup = Q(cert['G_up']), Q(cert['P_up'])
    if not arb(Gup) >= L.gub: raise AssertionError('G_up >= g(u_b)')
    if not arb(Pup) >= -arb(w) * arb(ub).log(): raise AssertionError('P_up >= -w log u_b')
    worst = None; n = 0
    for bx in walk(cert['tree'], (fmpq(0), Gup, -w, Pup)):
        U, info = L.box(*bx)
        n += 1
        if U is None: raise AssertionError('box %s failed: %s' % (bx, info))
        if not U < 0: raise AssertionError('box %s: U >= 0' % (bx,))
        if worst is None or U > worst[0]: worst = (U, bx)
    if verbose:
        print('checker B: %d boxes, all U < 0; worst U = %s' % (n, arb(worst[0]).str(8)))
    return worst


if __name__ == '__main__':
    check(json.load(open(sys.argv[1])))
    print('checker B ok')
