"""GC sub-pair strengthening in the Gaussian limit (FLOAT): at the GC optimum (q0, lambda) for a control, the largest
red sub-pair ratio over T in R_v (bands of alignment just below the cap) with Y'' in Y_v, and the largest blue sub-pair
ratio over T in B_v (higher caps), compared with x_GC and mu^w.  Ratios use the exp form at beta = 1, an upper bound
(Hoelder, PROOF_GC 3(d)(i)).  usage: python3 ramsey_gc_subpairs.py"""
import sys, numpy as np
from math import erf, sqrt, exp, log, pi
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from ramsey_gauss_cap import x_gc, Phibar_inv, phi
from math import erfc
def Phibar(x): return 0.5 * erfc(x / sqrt(2))
for (p, mu, w) in [(0.5, 0.4005, 0.4629), (0.55, 0.38, 0.5), (0.6, 0.35, 0.6), (0.7, 0.3, 0.8)]:
    xg, q0, lam = x_gc(p, mu, w)
    tp, th = Phibar_inv(p), Phibar_inv(q0)
    # blue: T = {c > th2}, th2 >= th
    bb = max((Phibar(t2) ** w * exp(lam * (phi(t2) / Phibar(t2)) ** 2 / 2), t2) for t2 in np.linspace(th, th + 7, 3501))
    # red: T = {a < c <= th}, Y'' = Y_v: ratio tau^w e^{kT^2/2} Phibar(tp - kT), kT = sqrt(lam) E[c z]/tau
    best = (0, None)
    for a in np.linspace(th - 8, th - 1e-4, 8000):
        tau = Phibar(a) - Phibar(th); Ecz = phi(a) - phi(th)
        k = sqrt(lam) * Ecz / tau
        val = tau ** w * exp(k * k / 2) * Phibar(tp - k)
        if val > best[0]: best = (val, a)
    full = (1 - q0) ** w * exp((q0 * sqrt(lam) * phi(th) / (q0 * (1 - q0))) ** 2 / 2) * Phibar(tp + sqrt(lam) * phi(th) / (1 - q0))
    print('p %.2f mu %.4f w %.4f | GC q0 %.3f lam/w %.2f x_GC %.4f mu^w %.4f | blue: R_v-level %.4f, best higher cap %.4f (th2 %.2f) | '
          'red: full R_v %.4f, best band %.4f (lower edge %.2f)' % (p, mu, w, q0, lam / w, xg, mu ** w,
          q0 ** w * exp(lam * (phi(th) / q0) ** 2 / 2), bb[0], bb[1], full, best[0], best[1]), flush=True)
