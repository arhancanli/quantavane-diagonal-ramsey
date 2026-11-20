"""Referee check (19 Nov 2026): a_GC on the subsampled control grid as in ramsey_agc_table.py, and again with the
corrected maximality constraint lambda <= w min{1, L(p)^-2}, L(p) = sup_{y>0} (Phibar(tau_p - y) - p)/(phi(tau_p) y)
(intermediate cap regime theta^2 ~ sqrt(R); L = 1 for p >= 1/2).  FLOAT.
usage: python3 ramsey_ref_agc_fix.py mustep wstep [out.npz]"""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dp import load_table
from math import erfc, sqrt, exp, pi

Phibar_s = lambda x: 0.5 * erfc(x / sqrt(2))
def Phibar(x):
    x = np.asarray(x, float)
    return 0.5 * np.vectorize(lambda t: erfc(t / sqrt(2)))(x) if x.size < 50 else _pb(x)
def _pb(x):  # A&S 7.1.26 as in ramsey_agc_table.py
    z = np.abs(x) / np.sqrt(2.0); t = 1.0 / (1.0 + 0.3275911 * z)
    y = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429)))) * np.exp(-z * z)
    return np.where(x >= 0, 0.5 * y, 1 - 0.5 * y)
def Phibar_inv(q):
    lo = np.full(np.shape(q), -12.0); hi = np.full(np.shape(q), 12.0)
    for _ in range(80):
        m = 0.5 * (lo + hi); b = _pb(m) > q
        lo = np.where(b, m, lo); hi = np.where(b, hi, m)
    return 0.5 * (lo + hi)
def Lp(p):
    lo, hi = -12.0, 12.0
    for _ in range(200):
        m = 0.5 * (lo + hi)
        lo, hi = (m, hi) if Phibar_s(m) > p else (lo, m)
    tp = 0.5 * (lo + hi); ph = exp(-tp * tp / 2) / sqrt(2 * pi)
    y = np.linspace(1e-5, 12, 120001)
    v = (np.array([Phibar_s(tp - t) for t in y[::20]]) - p) / (ph * y[::20])
    return max(1.0, v.max())

ms, ws = int(sys.argv[1]), int(sys.argv[2])
PP, MU, W, a = load_table(mustep=ms, wstep=ws)
p = (PP - 1e-6)[:, None, None, None, None]; mu = MU[None, :, None, None, None]; w = W[None, None, :, None, None]
tq = np.linspace(1e-3, 1 - 1e-9, 300)[None, None, None, :, None]
fk = np.linspace(0, 1, 60)[None, None, None, None, :]
tp = Phibar_inv(p)
L = np.array([Lp(float(x)) for x in PP - 1e-6])
res = {0: np.full((len(PP), len(MU), len(W)), np.inf), 1: np.full((len(PP), len(MU), len(W)), np.inf)}
lwopt = {0: np.full(res[0].shape, np.nan), 1: np.full(res[0].shape, np.nan)}
for i in range(len(PP)):
    pi_, tpi = p[i:i + 1], tp[i:i + 1]
    q0 = mu * tq; th = Phibar_inv(q0); phith = np.exp(-th * th / 2) / np.sqrt(2 * np.pi)
    for k, capf in [(0, 1.0), (1, min(1.0, 1 / L[i] ** 2))]:
        kmax = np.minimum(np.sqrt(2 * w * np.log(mu / q0)), np.sqrt(w * capf) * phith / q0)
        kB = kmax * fk * (1 - 1e-9)
        kR = q0 * kB / (1 - q0)
        x = (1 - q0) ** w * np.exp(kR * kR / 2) * _pb(tpi + kR)
        xx = x[0].reshape(len(MU), len(W), -1)
        j = np.argmin(xx, axis=2); res[k][i] = np.take_along_axis(xx, j[..., None], 2)[..., 0]
        lam_over_w = ((kB * q0 / phith) ** 2 / w)[0] * np.ones_like(x[0])
        lwopt[k][i] = np.take_along_axis(lam_over_w.reshape(len(MU), len(W), -1), j[..., None], 2)[..., 0]
P3 = (PP - 1e-6)[:, None, None]; arand = -np.log(P3 * (1 - MU[None, :, None]) ** W[None, None, :])
f = np.isfinite(a)
ag0, ag1 = -np.log(res[0]), -np.log(res[1])
print('cells', f.sum())
for k, ag in [(0, ag0), (1, ag1)]:
    sh = ((ag - arand) / (a - arand))[f]
    print('%s: a - a_GC min %.4f median %.4f; GC share median %.3f, range [%.3f, %.3f]; optimum lambda/w median %.3f max %.3f'
          % (['as drafted (lambda <= w)', 'corrected (lambda <= w min(1, L^-2))'][k], np.min((a - ag)[f]), np.median((a - ag)[f]),
             np.median(sh), np.min(sh), np.max(sh), np.nanmedian(lwopt[k][f]), np.nanmax(lwopt[k][f])))
viol = f & (lwopt[0] > np.minimum(1, 1 / L[:, None, None] ** 2) + 1e-9)
d = (ag0 - ag1)[f]
print('cells whose drafted optimum violates the corrected constraint: %d of %d; a_GC drop: max %.4f, mean over those %.4f'
      % (viol.sum(), f.sum(), d.max(), (ag0 - ag1)[viol].mean() if viol.any() else 0))
for i in range(len(PP)):
    fi = f[i]
    if not fi.any(): continue
    vi = viol[i]
    if vi.any() or PP[i] in (0.1, 0.2, 0.3, 0.5):
        print('p %.4f L %.4f cap %.3f | certified cells %4d, violating %4d | drafted lambda/w median %.3f max %.3f | max a_GC drop %.4f'
              % (PP[i], L[i], min(1, 1 / L[i] ** 2), fi.sum(), vi.sum(), np.nanmedian(lwopt[0][i][fi]), np.nanmax(lwopt[0][i][fi]),
                 (ag0 - ag1)[i][fi].max()))

if len(sys.argv) > 3:
    np.savez(sys.argv[3], PP=PP, MU=MU, W=W, agc=ag1, agc_drafted=ag0, a=a, L=L)
    old = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs', 'agc_m%dw%d.npz' % (ms, ws))
    if os.path.exists(old):
        t = np.load(old); ff = np.isfinite(t['agc']) & np.isfinite(ag0)
        print('check against logs/agc_m%dw%d.npz (drafted table): max |diff| %.2e' % (ms, ws, np.max(np.abs(t['agc'][ff] - ag0[ff]))))
