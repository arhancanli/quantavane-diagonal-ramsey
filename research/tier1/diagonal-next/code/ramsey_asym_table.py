"""Table of a_sym(p, mu, w) = -log x_sym (symmetric-split adversary, r -> infinity limit) on the (subsampled) control grid.
FLOAT, exploration only.  usage: python3 ramsey_asym_table.py mustep wstep out.npz"""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dp import load_table
ms, ws, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
PP, MU, W, a = load_table(mustep=ms, wstep=ws)
p = (PP - 1e-6)[:, None, None, None]; mu = MU[None, :, None, None]; w = W[None, None, :, None]
t = np.linspace(1e-4, 1 - 1e-9, 600)[None, None, None, :]
q0 = mu * t
rhs = (mu / q0) ** w
lo = np.zeros(np.broadcast(p, mu, w, t).shape); hi = np.full(lo.shape, 60.0)
for _ in range(80):
    m = 0.5 * (lo + hi)
    ok = p * np.exp(m) + (1 - p) * np.exp(-p * m / (1 - p)) <= rhs
    lo = np.where(ok, m, lo); hi = np.where(ok, hi, m)
x = p * (1 - q0) ** w * np.exp(-q0 * lo / (1 - q0))
asym = -np.log(x.min(axis=3))
arand = -np.log(p[..., 0] * (1 - mu[..., 0]) ** w[..., 0])
np.savez(out, PP=PP, MU=MU, W=W, asym=asym, arand=arand, a=a)
f = np.isfinite(a)
share = (asym - arand)[f] / (a - arand)[f]
print('cells', f.sum(), 'a - asym: min %.4f median %.4f max %.4f' % (np.min((a - asym)[f]), np.median((a - asym)[f]), np.max((a - asym)[f])))
print('symmetric share of the CERT-vs-random gap: median %.3f, 10%% %.3f, 90%% %.3f' % tuple(np.percentile(share, [50, 10, 90])))
