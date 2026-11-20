"""Referee check (19 Nov 2026): EXACT continuum cap functional of the GC construction at finite dimension R (no Gaussian
approximation, no linearisation).  Rows f uniform on S^{R-1}; columns u = sqrt(R) e_hat, e_hat uniform on S^{R-1};
red iff <f,u> > tau_p.  Cap S_theta = {sqrt(R) <f,e> > theta}.  With s = <f,e>, rho = <e_hat,e>,
<f,e_hat> = rho s + sqrt(1-rho^2) sqrt(1-s^2) x, x = one coordinate of a uniform point of S^{R-2}.
Scaled variables a = sqrt(R) s, Z = sqrt(R) rho, b = sqrt(R) x; densities (1-a^2/R)^{(R-3)/2}, same for Z,
(1-b^2/R)^{(R-4)/2} for b.  D(Z) = Pr(red | f in S, rho) - p_R.  Ratio (beta -> 1, Y' = Y; by Hoelder this bounds every
Y' and every beta <= 1, and (1 + D/H)^r <= e^{D/eps} bounds finite r):  ratio(theta) = tau^w E_Z exp(D(Z)/eps),
eps = phi(tau_p)/sqrt(lambda R).  All in logs.
usage: python3 ramsey_ref_capexact.py R p w lambda_over_w [theta_min theta_max ntheta [H]]  (H given: exact (1+D/H)^r form)"""
import sys, numpy as np
from math import erfc, sqrt, exp, log, pi, lgamma
import warnings; warnings.filterwarnings("ignore", message=".*encountered in matmul")

def Phibar(x): return 0.5 * erfc(x / sqrt(2))
def Pinv(q):
    lo, hi = -40.0, 40.0
    for _ in range(200):
        m = 0.5 * (lo + hi)
        lo, hi = (m, hi) if Phibar(m) > q else (lo, m)
    return 0.5 * (lo + hi)

def lse(x):
    m = np.max(x); return m + np.log(np.sum(np.exp(x - m)))

class Cap:
    def __init__(self, R, p, w, lw, nz=4001, zmax=None):
        self.R, self.p, self.w = R, p, w
        self.tp = Pinv(p); phip = exp(-self.tp ** 2 / 2) / sqrt(2 * pi)
        self.eps = phip / sqrt(lw * w * R)
        sq = sqrt(R); self.sq = sq
        # b table: Pr(b > beta), b = sqrt(R) x, x a coordinate of S^{R-2}
        bmax = min(sq * (1 - 1e-12), 60.0)
        bg = np.linspace(-bmax, bmax, 240001)
        lb = 0.5 * (R - 4) * np.log1p(-(bg / sq) ** 2)
        db = np.exp(lb - lb.max())
        cdf = np.concatenate([[0], np.cumsum(0.5 * (db[1:] + db[:-1]) * np.diff(bg))])
        self.bg, self.sf = bg, 1 - cdf / cdf[-1]
        # exact log normaliser of the a-density (1 - a^2/R)^{(R-3)/2} on [-sqrt R, sqrt R]
        self.lnorm = log(sq) + lgamma(0.5) + lgamma((R - 1) / 2) - lgamma(R / 2)
        zmax = min(sq * (1 - 1e-12), zmax if zmax else 200.0)
        self.zg = np.linspace(-zmax, zmax, nz)
        lz = 0.5 * (R - 3) * np.log1p(-(self.zg / sq) ** 2) + np.log(np.gradient(self.zg))
        self.lz = lz - lse(lz)
        a, la = self.agrid(self.tp)
        self.pR = exp(lse(la) - self.lnorm)          # p_R = Pr(<f,e_hat> > tau_p/sqrt R) exactly (same law as s)
        self.pR_num = self.P(-np.inf).mean()        # discretisation check: should equal p_R

    def agrid(self, theta, n=20001):
        """quadrature nodes and log weights (density x spacing) for a = sqrt(R) s on (theta, sqrt R)."""
        sq = self.sq; top = sq * (1 - 1e-12)
        if theta > 3:
            hi = min(theta + 60.0 / theta, top)
        else:
            hi = min(top, 45.0)
        lo = max(theta, -top, -45.0)
        a = np.linspace(lo, hi, n)
        wt = np.full(n, a[1] - a[0]); wt[0] *= 0.5; wt[-1] *= 0.5
        la = 0.5 * (self.R - 3) * np.log1p(-(a / sq) ** 2) + np.log(wt)
        return a, la

    def P(self, theta):
        """Pr(red | f in S_theta, Z) for every Z on the grid (vector)."""
        sq = self.sq
        a, la = self.agrid(theta)
        keep = la > la.max() - 60; a, la = a[keep], la[keep]
        wa = np.exp(la - la.max()); wa /= wa.sum()
        out = np.empty(len(self.zg))
        ca = np.sqrt(1 - (a / sq) ** 2)
        for i0 in range(0, len(self.zg), 256):
            Z = self.zg[i0:i0 + 256, None]
            beta = (self.tp - Z * a[None, :] / sq) / (np.sqrt(1 - (Z / sq) ** 2) * ca[None, :])
            out[i0:i0 + 256] = np.interp(beta, self.bg, self.sf) @ wa
        return out

    def logtau(self, theta):
        a, la = self.agrid(theta)
        return lse(la) - self.lnorm

    def ratio(self, theta, Hs=None):
        D = self.P(theta) - self.pR
        lt = self.logtau(theta)
        if Hs is None:                                # exp form (r -> infinity at fixed D/eps)
            ex = D / self.eps
        else:                                         # exact finite-r beta = 1 form: (1 + D/H)_+^r, r = H/eps
            z = 1 + D / Hs
            ex = np.where(z > 0, (Hs / self.eps) * np.log(np.where(z > 0, z, 1.0)), -np.inf)
        lE = lse(self.lz + ex)
        return self.w * lt + lE, lt, D

if __name__ == '__main__':
    R, p, w, lw = int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
    t0, t1, nt = (float(sys.argv[5]), float(sys.argv[6]), int(sys.argv[7])) if len(sys.argv) > 7 else (-3.0, 6.0, 19)
    Hs = float(sys.argv[8]) if len(sys.argv) > 8 else None
    C = Cap(R, p, w, lw)
    if Hs is not None: print('EXACT finite-r potential: c = p - H, H = %.4f, r = H/eps = %.2f' % (Hs, Hs / C.eps))
    phi = lambda t: exp(-t * t / 2) / sqrt(2 * pi)
    print('R %d p %.3f w %.4f lambda/w %.3f eps %.5f p_R %.7f (numerical full-sphere check %.7f)' % (R, p, w, lw, C.eps, C.pR, C.pR_num))
    best = (-np.inf, None)
    for th in np.linspace(t0, t1, nt):
        if th >= 0.98 * sqrt(R): continue
        lr, lt, D = C.ratio(th, Hs)
        # Gaussian-limit formula (valid for theta = O(1)): tau^w exp(lambda m^2 / 2), m = phi(theta)/Phibar(theta)
        tg = Phibar(th); lim = w * log(tg) + lw * w * (phi(th) / tg) ** 2 / 2 if tg > 0 else float('nan')
        print('theta %8.3f  log tau %10.3f  log ratio %10.4f  ratio %.4g   (Gaussian-limit log ratio %.4f)'
              % (th, lt, lr, exp(min(lr, 700)), lim))
        if lr > best[0]: best = (lr, th)
    print('max log ratio %.4f at theta %.3f' % best)
