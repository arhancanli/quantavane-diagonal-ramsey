"""Exploration (float, proves nothing): the robust two-region level (i) bound of CERT_DESIGN.md (Lemma D),
evaluated on boxes of (Phi_b, p_b) with the corner rules of the design.  Fast: concave hull of (q, Ht(q))."""
import sys
import numpy as np
from explore1 import P, a_of, parts

class Fn:
    def __init__(self, c, nq=400001):
        p, mu, w, beta, x = c['p'], c['mu'], c['w'], c['beta'], c['x']
        self.c = c; self.w = w; self.mu = mu
        self.a0 = a_of(0, c); self.alpha = (a_of(0, c) - a_of(1e-7, c)) / 1e-7
        q = self.a0 + (mu - self.a0) * np.linspace(0, 1, nq)[1:]
        M = parts(q, p, mu, w, beta, x); ok = np.isfinite(M)
        self.q = q[ok]; self.Ht = self.q * M[ok]; self.H = self.Ht + w * self.q
        self.dHt = np.gradient(self.Ht, self.q); self.d2Ht = np.gradient(self.dHt, self.q)
        self.ipk = int(np.argmax(self.H))
        # slopes between consecutive points (concave => decreasing)
        self.sl = np.diff(self.Ht) / np.diff(self.q)
    def qhat(self, y):
        # argmax_q Ht(q) - q y : first index where slope to next < y
        y = np.atleast_1d(y)
        j = np.searchsorted(-self.sl, -y)          # sl decreasing: count of sl >= y
        return np.minimum(j, len(self.q) - 1)
    def Hhat(self, y, j0=0):
        y = np.atleast_1d(y); j = np.maximum(self.qhat(y), j0)
        return self.Ht[j] - self.q[j] * y
    def j_of_C(self, C):
        return min(int(np.searchsorted(self.H[:self.ipk + 1], C)), self.ipk)

def quad_log(f, lo, hi, n=4000):
    if hi <= lo: return 0.0
    lo = max(lo, 1e-80)
    e = np.linspace(np.log(lo), np.log(hi), n + 1); um = np.exp(0.5 * (e[1:] + e[:-1])); du = np.diff(np.exp(e))
    return float(np.sum(f(um) * du))

def switch_left(w, ub, Phib, pb):
    gs = lambda u: -w * u * np.log(u)
    f = lambda u: gs(u) - (Phib - pb * (ub - u))
    if f(ub * (1 - 1e-13)) <= 0: return ub
    lo, hi = 1e-300, ub
    for _ in range(300):
        m = np.sqrt(lo * hi) if hi / lo > 4 else 0.5 * (lo + hi)
        if f(m) <= 0: lo = m
        else: hi = m
    return lo

def switch_right(w, ub, Phib, pb):
    gs = lambda u: -w * u * np.log(u)
    g = lambda u: Phib + pb * (u - ub) - gs(u)
    if g(ub + 1e-13) >= 0 and gs(ub) - Phib <= 1e-15: return ub
    lo, hi = ub, 1.0
    if g(hi - 1e-15) < 0: return 1.0
    for _ in range(300):
        m = 0.5 * (lo + hi)
        if g(m) >= 0: hi = m
        else: lo = m
    return hi

class Bound:
    def __init__(self, F, ub, Dplus=1e-6):
        self.F = F; self.ub = ub; self.Dp = Dplus; w = F.w
        self.fs = lambda u: -w * (1 + np.log(u)); self.gs = lambda u: -w * u * np.log(u)
        self.IRs = quad_log(lambda u: F.Hhat(self.fs(u)), ub, 1)
        # cap level y_mu = left slope at mu
        self.ymu = F.sl[-1]
        yc = self.ymu
        self.Ecap0 = (yc**2 - w**2) / 2 + w**2 * (1 - np.exp(-1 - yc / w))
    def U(self, Phl, Phh, pl, ph, detail=False):
        F = self.F; w = F.w; ub = self.ub; Dp = self.Dp; gs, fs = self.gs, self.fs
        gb = gs(ub)
        # C0_lo over box: a0 (w + ub p - Phi - Dp (p + w)) minimal at pl, Phh
        C0 = F.a0 * (w + ub * pl - Phh - Dp * (ph + w))
        j0 = F.j_of_C(C0)
        q0 = F.q[j0]; h1 = F.dHt[j0] + w; s0 = F.dHt[j0]
        Dl0 = max(F.H[j0] - C0, 0) / h1
        # left integral at (max(Phl, pl ub), pl)
        P1 = max(Phl, pl * ub)
        u1 = switch_left(w, ub, P1, pl)
        IL = quad_log(lambda u: F.Hhat(fs(u), j0), 0, u1) + (ub - u1) * F.Hhat(pl, j0)[0]
        # K at (Phh, pl)
        u1k = switch_left(w, ub, Phh, pl)
        K = quad_log(lambda u: np.maximum(fs(u) - s0, 0), 0, u1k) + (ub - u1k) * max(pl - s0, 0)
        # right majorised at (Phh, ph)
        u2 = switch_right(w, ub, Phh, ph)
        IR2 = (u2 - ub) * F.Hhat(ph)[0] + quad_log(lambda u: F.Hhat(fs(u)), u2, 1)
        # theta-part
        mb_lo = max(gb - Phh, 0)
        jq = F.qhat(ph)[0]; qh = F.q[jq]
        i0 = jq; kap2 = 1.0 / np.max(np.abs(F.d2Ht[i0:-2]))
        kap = F.alpha * K / h1
        th = kap / kap2
        Lip = max(fs(ub), ph) + w
        Egrid = Lip * Dp * max(ph - self.ymu, 0)
        Ecap = self.Ecap0 + Dp * (ph + w) * (self.ymu + w)
        val = IL + Dl0 * K + (1 - th) * IR2 + th * (self.IRs - qh * mb_lo) + kap * (Egrid + Ecap)
        if detail:
            return val, dict(IL=IL, K=K, IR2=IR2, th=th, kap=kap, kap2=kap2, C0=C0, q0=q0, Dl0=Dl0, Ecap=kap * Ecap, u1=u1, u2=u2)
        return val

if __name__ == '__main__':
    da = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    ubs = [float(s) for s in (sys.argv[2].split(',') if len(sys.argv) > 2 else ['0.03'])]
    c = dict(P); c['x'] = P['x'] * np.exp(-da)
    F = Fn(c)
    zbs = quad_log(lambda u: F.Hhat(-F.w * (1 + np.log(u))), 0, 1, 20000)
    print('da %+.5f  a0 %.6f alpha %.4f  ZBS(float) %.4e' % (da, F.a0, F.alpha, zbs))
    for ub in ubs:
        B = Bound(F, ub); w = F.w; gb = B.gs(ub); pbs = B.fs(ub)
        v, d = B.U(gb, gb, pbs, pbs, True)
        print('u_b %.3f point-at-saturation U %.4e  %s' % (ub, v, {k: round(float(x), 6) for k, x in d.items()}))
        # scan point boxes over the feasible region
        best = (v, gb, pbs)
        for mbr in np.concatenate([[0], np.geomspace(1e-5, 0.999, 30)]):
            Ph = gb * (1 - mbr)
            lo = max(-w, -Ph / (1 - ub)); hi = Ph / ub
            for pb in np.concatenate([np.linspace(lo, hi, 40), pbs + np.array([-0.3, -0.1, -0.03, -0.01, 0, 0.01, 0.03])]):
                if pb < lo or pb > hi: continue
                vv = B.U(Ph, Ph, pb, pb)
                if vv > best[0]: best = (vv, Ph, pb)
        vv, dd = B.U(best[1], best[1], best[2], best[2], True)
        print('   max over point boxes U %.4e at m_b/g %.3g, p_b - phi_s %+.4f   th %.3f kap*Ecap %.2e' % (
            best[0], 1 - best[1] / gb, best[2] - pbs, dd['th'], dd['Ecap']), flush=True)
