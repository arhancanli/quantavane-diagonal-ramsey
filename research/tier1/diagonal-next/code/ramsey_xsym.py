"""Symmetric-split adversary (all rows alike: q constant, drift 0, two-cell gain split) in the r -> infinity limit.
x_sym(p, mu, w) = min over q0 < mu of p (1-q0)^w exp(-q0 Z/(1-q0)), Z = largest red-cell gain with
p e^Z + (1-p) e^{-p Z/(1-p)} <= (mu/q0)^w (blue fails; zero mean gain).  Compare x_rand = p (1-mu)^w and the certified x.
FLOAT, exploration only."""
import sys, numpy as np
sys.path.insert(0, __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', '..', '..', 'tier2', 'ramsey-zbs', 'search'))
from ctlvec import xcert

def zmax(p, rhs):
    lo, hi = 0.0, 50.0
    for _ in range(200):
        m = 0.5 * (lo + hi)
        if p * np.exp(m) + (1 - p) * np.exp(-p * m / (1 - p)) <= rhs: lo = m
        else: hi = m
    return lo

def xsym(p, mu, w, n=4000):
    best = (np.inf, None, None)
    for q0 in np.linspace(1e-4, mu * (1 - 1e-9), n):
        Z = zmax(p, (mu / q0) ** w)
        x = p * (1 - q0) ** w * np.exp(-q0 * Z / (1 - q0))
        if x < best[0]: best = (x, q0, Z)
    return best

for (p, mu, w) in [(0.5, 0.4005, 0.4629), (0.5, 0.4036, 0.4812), (0.55, 0.38, 0.5), (0.6, 0.35, 0.6), (0.7, 0.3, 0.8),
                   (0.4, 0.45, 0.4), (0.5, 0.3, 0.3), (0.5, 0.5, 0.8)]:
    xs, q0, Z = xsym(p, mu, w)
    xr = p * (1 - mu) ** w
    xc = float(xcert(np.array([p - 1e-6]), np.array([mu]), np.array([w]))[0])
    print('p %.3f mu %.4f w %.4f | a_rand %.4f  a_sym %.4f (q0 %.3f, dzeta %.3f)  a_cert %.4f | sym share of gap %.2f'
          % (p, mu, w, -np.log(xr), -np.log(xs), q0, Z / (1 - p), -np.log(xc), (np.log(xr) - np.log(xs)) / (np.log(xr) - np.log(xc))))
