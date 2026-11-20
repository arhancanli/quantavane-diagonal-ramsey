"""Gaussian-latent cap construction (GC) in the limit R -> infinity, r -> infinity (FLOAT, exploration only).
Rows: latent f_v uniform on a sphere of radius s in R^R; columns: u_y uniform on the sphere of radius sqrt(R);
red iff <f_v,u_y> + sqrt(1-s^2) eta > tau_p (p = Phibar(tau_p)); blue graph on X: j ~ v iff the normalised alignment
c = <f_j,f_v> sqrt(R)/s^2 exceeds theta_q (q0 = Phibar(theta_q)).  Scale eps = H/r with lambda = (phi(tau_p) s/eps)^2/R.
Limit facts (derivation in PROOF_GC.md): maximality of every sub-pair <=> lambda <= w (caps of vanishing measure bind);
gain of row v on column y: psi = kappa_B G', G' = <f_v,u_y>/s ~ N(0,1), kappa_B = sqrt(lambda) phi(theta_q)/q0;
blue retention q0^w E e^{psi} = q0^w e^{kappa_B^2/2}; red retention (1-q0)^w E[e^{-q0 psi/(1-q0)} ; red]
= (1-q0)^w e^{kR^2/2} Phibar(tau_p + s kR), kR = q0 kappa_B/(1-q0) (s = 1 is best).
For a control (p, mu, w): x_GC = min over q0 < mu, lambda <= w with q0 e^{kappa_B^2/(2w)} < mu of the red retention."""
import sys, numpy as np
from math import erf, sqrt, exp, log, pi
sys.path.insert(0, __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', '..', '..', 'tier2', 'ramsey-zbs', 'search'))
from ctlvec import xcert

def Phibar(x): return 0.5 * (1 - erf(x / sqrt(2)))
def phi(x): return exp(-x * x / 2) / sqrt(2 * pi)
def Phibar_inv(q):
    lo, hi = -10.0, 10.0
    for _ in range(200):
        m = 0.5 * (lo + hi)
        if Phibar(m) > q: lo = m
        else: hi = m
    return 0.5 * (lo + hi)

def x_gc(p, mu, w, nq=800, nl=200):
    tp = Phibar_inv(p); best = (np.inf, None, None)
    for q0 in np.linspace(1e-3, mu * (1 - 1e-9), nq):
        th = Phibar_inv(q0)
        for lam in np.linspace(0, w, nl):
            kB = sqrt(lam) * phi(th) / q0
            if q0 * exp(kB * kB / (2 * w)) >= mu: break
            kR = q0 * kB / (1 - q0)
            x = (1 - q0) ** w * exp(kR * kR / 2) * Phibar(tp + kR)
            if x < best[0]: best = (x, q0, lam)
    return best

def xsym(p, mu, w, n=3000):
    best = np.inf
    for q0 in np.linspace(1e-4, mu * (1 - 1e-9), n):
        lo, hi = 0.0, 50.0; rhs = (mu / q0) ** w
        for _ in range(100):
            m = 0.5 * (lo + hi)
            if p * exp(m) + (1 - p) * exp(-p * m / (1 - p)) <= rhs: lo = m
            else: hi = m
        best = min(best, p * (1 - q0) ** w * exp(-q0 * lo / (1 - q0)))
    return best

if __name__ == '__main__':
    for (p, mu, w) in [(0.5, 0.4005, 0.4629), (0.5, 0.4036, 0.4812), (0.55, 0.38, 0.5), (0.6, 0.35, 0.6), (0.7, 0.3, 0.8),
                       (0.4, 0.45, 0.4), (0.5, 0.3, 0.3), (0.5, 0.5, 0.8)]:
        xg, q0, lam = x_gc(p, mu, w)
        xr = p * (1 - mu) ** w; xs = xsym(p, mu, w)
        xc = float(xcert(np.array([p - 1e-6]), np.array([mu]), np.array([w]))[0])
        ar, ag, as_, ac = -log(xr), -log(xg), -log(xs), -log(xc)
        print('p %.2f mu %.4f w %.4f | a_rand %.4f a_GC %.4f (q0 %.3f lam/w %.2f) a_sym %.4f a_cert %.4f | GC share %.2f'
              % (p, mu, w, ar, ag, q0, lam / w, as_, ac, (ag - ar) / (ac - ar)))
