"""a_GC with lambda (phi(0)/phi(tau_p))^2 <= 0.9 w at every p (the range the finite-host proof covers). FLOAT.
usage: python3 ramsey_agc_table.py mustep wstep out.npz"""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dp import load_table

def Phibar(x):
    # Phibar(x) = erfc(x/sqrt2)/2, erfc by W. J. Cody-free rational approx (A&S 7.1.26, |err| < 1.5e-7), sign-folded
    z = np.abs(x) / np.sqrt(2.0)
    t = 1.0 / (1.0 + 0.3275911 * z)
    y = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429)))) * np.exp(-z * z)
    return np.where(x >= 0, 0.5 * y, 1 - 0.5 * y)

def Phibar_inv(q):
    lo = np.full(np.shape(q), -12.0); hi = np.full(np.shape(q), 12.0)
    for _ in range(80):
        m = 0.5 * (lo + hi); b = Phibar(m) > q
        lo = np.where(b, m, lo); hi = np.where(b, hi, m)
    return 0.5 * (lo + hi)

ms, ws, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
PP, MU, W, a = load_table(mustep=ms, wstep=ws)
p = (PP - 1e-6)[:, None, None, None, None]; mu = MU[None, :, None, None, None]; w = W[None, None, :, None, None]
tq = np.linspace(1e-3, 1 - 1e-9, 300)[None, None, None, :, None]
fk = np.linspace(0, 1, 60)[None, None, None, None, :]
tp = Phibar_inv(p)
res = np.full((len(PP), len(MU), len(W)), np.inf)
for i in range(len(PP)):                                   # chunk over densities
    pi = p[i:i + 1]; tpi = tp[i:i + 1]
    q0 = mu * tq
    th = Phibar_inv(q0)
    phith = np.exp(-th * th / 2) / np.sqrt(2 * np.pi)
    lmax = 0.9 * w * (np.exp(-tpi * tpi / 2)) ** 2
    kmax = np.minimum(np.sqrt(2 * w * np.log(mu / q0)), np.sqrt(lmax) * phith / q0)
    kB = kmax * fk * (1 - 1e-9)
    kR = q0 * kB / (1 - q0)
    x = (1 - q0) ** w * np.exp(kR * kR / 2) * Phibar(tpi + kR)
    res[i] = x.min(axis=(3, 4))[0]
agc = -np.log(res)
P3x = (PP - 1e-6)[:, None, None]
pass
np.savez(out, PP=PP, MU=MU, W=W, agc=agc, a=a)
P3 = (PP - 1e-6)[:, None, None]; arand = -np.log(P3 * (1 - MU[None, :, None]) ** W[None, None, :])
f = np.isfinite(a)
print('cells', f.sum(), 'a - a_GC: min %.4f median %.4f; a_GC - a_rand median %.4f; GC share median %.3f'
      % (np.min((a - agc)[f]), np.median((a - agc)[f]), np.median((agc - arand)[f]), np.median(((agc - arand) / (a - arand))[f])))
