"""Float view of the ZBS bank (exploration only). Loads zbs_bank.json (parse_zbs.py) and LW source.json."""
import json, math, bisect
import numpy as np
from fractions import Fraction as Fr
def fr(s): return float(Fr(s))
class LWf:
    def __init__(self, path):
        d = json.load(open(path))
        self.x = np.array([float(Fr(a)) for a in d['nodes']]); self.v = np.array([float(Fr(a)) for a in d['values']])
        self.dv = np.array([float(Fr(a)) for a in d['derivatives']])
    def P(self, t):
        t = np.asarray(t, float); i = np.clip(np.searchsorted(self.x, t, 'right') - 1, 0, len(self.x) - 2)
        a, b = self.x[i], self.x[i + 1]; dl = b - a; u = t - a; D = self.v[i + 1] - self.v[i]
        return (self.v[i] + self.dv[i] * u + (3 * D / dl - 2 * self.dv[i] - self.dv[i + 1]) / dl * u ** 2
                + (self.dv[i] + self.dv[i + 1] - 2 * D / dl) / dl ** 2 * u ** 3)
    def f(self, s):
        s = np.asarray(s, float)
        with np.errstate(all='ignore'):
            h = (1 + s) * np.log1p(s) - np.where(s > 0, s * np.log(np.where(s > 0, s, 1)), 0)
        return h + s * np.exp(-s) * self.P(s)
    def fhat(self, lam):
        lam = np.asarray(lam, float)
        return np.where(lam <= 1, self.f(np.minimum(lam, 1)), lam * self.f(1 / np.maximum(lam, 1)))
class Prof:
    def __init__(self, d):
        self.p = fr(d['p']); self.xs = np.array([fr(a) for a in d['xs']]); self.ys = np.array([fr(a) for a in d['ys']])
    def __call__(self, r):
        return np.interp(r, self.xs, self.ys, left=np.nan, right=np.nan)
def load(bankp, lwp):
    b = json.load(open(bankp))
    bank = {'A': np.array([fr(a) for a in b['A']]), 'B': np.array([fr(a) for a in b['B']]),
            'ctl': np.array([[fr(a) for a in c] for c in b['ctl']]),
            'raw': [Prof(d) for d in b['raw']], 'closed': [Prof(d) for d in b['closed']]}
    return bank, LWf(lwp)
