"""Independent Monte Carlo check of the Gaussian-cap (GC) limit formulas on an explicit finite host (FLOAT; second
program for ramsey_gauss_cap.py).  Rows f_v ~ uniform on S^{R-1}; columns u_y ~ uniform on the sphere of radius sqrt(R);
red iff <f_v,u_y> > tau_p; blue iff <f_j,f_v> sqrt(R) > theta_q.  eps = phi(tau_p)/sqrt(lambda R).
Checks: (1) gain field psi_v(y) = (b_v(y) - g_y)/eps against kappa_B * <f_v,u_y> (slope, residual sd);
(2) blue and red retentions (limit forms) against the formulas; (3) cap sub-pairs: max over caps of
tau^w E_y exp((g^S_y - g_y)/eps) for lambda below and above w (maximality iff lambda <= w in the limit).
usage: python3 ramsey_gc_montecarlo.py R N M lambda_over_w seed"""
import sys, numpy as np
from math import erf, sqrt, exp, log, pi
R, N, M = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]); lw = float(sys.argv[4]); seed = int(sys.argv[5])
p, w, q0 = 0.5, 0.4629, 0.342
rng = np.random.default_rng(seed)
def Phibar(x): return 0.5 * (1 - erf(x / sqrt(2)))
def Pinv(q):
    lo, hi = -12, 12
    for _ in range(200):
        m = 0.5 * (lo + hi)
        lo, hi = (m, hi) if Phibar(m) > q else (lo, m)
    return 0.5 * (lo + hi)
tp, th = Pinv(p), Pinv(q0); phip = exp(-tp * tp / 2) / sqrt(2 * pi); phith = exp(-th * th / 2) / sqrt(2 * pi)
lam = lw * w; eps = phip / sqrt(lam * R)
F = rng.standard_normal((N, R)); F /= np.linalg.norm(F, axis=1, keepdims=True)
U = rng.standard_normal((M, R)); U *= sqrt(R) / np.linalg.norm(U, axis=1, keepdims=True)
G = F @ U.T                                              # <f_v, u_y>, ~ N(0,1)
Hred = (G > tp).astype(np.float32)
g = Hred.mean(axis=0)                                    # column densities
print('R %d N %d M %d lambda/w %.2f eps %.4f | column density mean %.4f sd %.5f (sd/eps %.3f)' % (R, N, M, lw, eps, g.mean(), g.std(), g.std() / eps))
kB = sqrt(lam) * phith / q0
rows = rng.choice(N, 40, replace=False)
slopes, resid, blue_ret, red_ret = [], [], [], []
for v in rows:
    c = (F @ F[v]) * sqrt(R); c[v] = -np.inf
    B = c > th
    psi = (Hred[B].mean(axis=0) - g) / eps
    Gv = G[v]
    b = np.polyfit(Gv, psi, 1); slopes.append(b[0]); resid.append(np.std(psi - np.polyval(b, Gv)))
    blue_ret.append(np.mean(np.exp(psi)))
    kR = B.mean() / (1 - B.mean())
    red_ret.append(np.mean(Hred[v] * np.exp(-kR * psi)))
qv = q0
print('gain slope on <f_v,u>: mean %.4f (formula kappa_B %.4f); residual sd %.4f (sampling noise expected ~%.3f)'
      % (np.mean(slopes), kB, np.mean(resid), sqrt(p * (1 - p) / (q0 * N)) / eps))
print('E e^psi: MC %.4f formula e^{kB^2/2} %.4f | E[1_red e^{-k psi}]: MC %.4f formula %.4f'
      % (np.mean(blue_ret), exp(kB * kB / 2), np.mean(red_ret), exp((q0 * kB / (1 - q0)) ** 2 / 2) * Phibar(tp + q0 * kB / (1 - q0))))
# cap sub-pairs: S = {<f, e> sqrt(R) > t}, e random unit; ratio = tau^w E_y exp(D_y/eps)  (beta -> 1 limit form)
worst = []
for t in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
    vals = []
    for _ in range(6):
        e = rng.standard_normal(R); e /= np.linalg.norm(e)
        S = (F @ e) * sqrt(R) > t
        if S.sum() < 20: continue
        D = Hred[S].mean(axis=0) - g
        vals.append((S.mean()) ** w * np.mean(np.exp(D / eps)))
    if vals: worst.append((t, max(vals), np.mean(S)))
print('cap sub-pairs (t, max ratio over 6 directions, measure): ' + '; '.join('%.1f %.3f %.4f' % x for x in worst))
