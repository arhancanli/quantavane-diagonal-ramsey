"""Referee search (19 Nov 2026): try to break maximality of the GC Monte Carlo host beyond caps.
Host exactly as code/ramsey_gc_montecarlo.py (same seed -> same F, U), plus M2 held-out columns U2 drawn afterwards.
Ratio (beta -> 1, Y' = Y, exp form, as in PROOF_GC (d)): log ratio(S) = w log(|S|/N) + log mean_y exp((g^S_y - g_y)/eps).
Also: the same on held-out columns (no column overfitting), the row-noise factor exp(s^2/2) with
s^2 = mean_y g^S(1-g^S) (1/|S| - 1/N)/eps^2, and the exact finite-r beta = 1 ratio for c = p - Hs:
(|S|/N)^w sum_y (g^S_y - c)_+^r / sum_y (g_y - c)^r with r = Hs/eps.
usage: python3 ramsey_ref_gc_search.py R N M M2 lambda_over_w seed Hs"""
import sys, time, numpy as np
from math import erf, sqrt, exp, log, pi
import warnings; warnings.filterwarnings("ignore", message=".*encountered in matmul")
R, N, M, M2 = (int(v) for v in sys.argv[1:5]); lw = float(sys.argv[5]); seed = int(sys.argv[6]); Hs = float(sys.argv[7])
p, w, q0 = 0.5, 0.4629, 0.342
rng = np.random.default_rng(seed)
def Phibar(x): return 0.5 * (1 - erf(x / sqrt(2)))
def Pinv(q):
    lo, hi = -12, 12
    for _ in range(200):
        m = 0.5 * (lo + hi)
        lo, hi = (m, hi) if Phibar(m) > q else (lo, m)
    return 0.5 * (lo + hi)
tp = Pinv(p); phip = exp(-tp * tp / 2) / sqrt(2 * pi)
lam = lw * w; eps = phip / sqrt(lam * R); r_exact = Hs / eps; c = p - Hs
F = rng.standard_normal((N, R)); F /= np.linalg.norm(F, axis=1, keepdims=True)
U = rng.standard_normal((M, R)); U *= sqrt(R) / np.linalg.norm(U, axis=1, keepdims=True)
U2 = rng.standard_normal((M2, R)); U2 *= sqrt(R) / np.linalg.norm(U2, axis=1, keepdims=True)
def redmat(UU):
    out = np.empty((N, len(UU)), np.float32)
    for i in range(0, N, 2000):
        out[i:i + 2000] = (F[i:i + 2000] @ UU.T > tp)
    return out
H = redmat(U); H2 = redmat(U2)
g = H.mean(axis=0, dtype=np.float64); g2 = H2.mean(axis=0, dtype=np.float64)
print('R %d N %d M %d M2 %d lambda/w %.2f eps %.4f | exact-r check: Hs %.2f r %.2f' % (R, N, M, M2, lw, eps, Hs, r_exact))
print('size thresholds: single-row bound tau^w e^{(1-p)/eps} <= 1 needs tau <= %.3g (N >= %.3g); one column with D = 1-p adds %.3g/M'
      % (exp(-(1 - p) / (w * eps)), exp((1 - p) / (w * eps)), exp((1 - p) / eps)))

def stats(S):
    S = np.asarray(S, bool); n = int(S.sum())
    if n == 0: return None
    sv = S.astype(np.float32)
    gS = (sv @ H).astype(np.float64) / n; gS2 = (sv @ H2).astype(np.float64) / n
    lt = log(n / N)
    lr = w * lt + log(np.mean(np.exp((gS - g) / eps)))
    lr2 = w * lt + log(np.mean(np.exp((gS2 - g2) / eps)))
    s2 = np.mean(gS2 * (1 - gS2)) * (1.0 / n - 1.0 / N) / eps ** 2
    lrr = w * lt + log(np.sum(np.clip(gS - c, 0, None) ** r_exact) / np.sum((g - c) ** r_exact))
    return dict(n=n, tau=n / N, lr=lr, lr_ho=lr2, noise=s2 / 2, lr_ho_nc=lr2 - s2 / 2, lr_exact=lrr)

results = []
def rec(kind, S):
    st = stats(S)
    if st: st['kind'] = kind; results.append(st)
    return st

a_rand = lambda: (lambda e: e / np.linalg.norm(e))(rng.standard_normal(R))
t0 = time.time()
# A. caps, random directions
for t in [-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
    for _ in range(8): rec('cap t=%.1f' % t, (F @ a_rand()) * sqrt(R) > t)
# B. caps aligned with one sampled column (column overfit)
for y in rng.choice(M, 8, replace=False):
    e = U[y] / sqrt(R)
    for t in [0.0, 0.5, 1.0, 2.0]: rec('column-aligned cap t=%.1f' % t, (F @ e) * sqrt(R) > t)
# C. intersections / unions of two or three caps in random directions
for t in [-1.0, -0.5, 0.0, 0.5, 1.0, 1.5]:
    for _ in range(6):
        A1, A2, A3 = ((F @ a_rand()) * sqrt(R) > t for _ in range(3))
        rec('2-cap intersection t=%.1f' % t, A1 & A2); rec('3-cap intersection t=%.1f' % t, A1 & A2 & A3)
        rec('2-cap union t=%.1f' % t, A1 | A2)
# D. slabs t1 < a < t2
for (t1, t2) in [(-0.25, 0.25), (0.0, 0.5), (0.5, 1.0), (1.0, 1.5), (1.5, 2.5), (-1.0, 1.0), (0.0, 1.0)]:
    for _ in range(6):
        a = (F @ a_rand()) * sqrt(R); rec('slab (%.2f,%.2f)' % (t1, t2), (a > t1) & (a < t2))
# E. red degree into a random column subset
for k in [1, 5, 20, 100, 500]:
    for _ in range(4):
        Yc = rng.choice(M, k, replace=False); sc = H[:, Yc].sum(axis=1)
        for q in [0.5, 0.2, 0.05, 0.01]:
            thr = np.quantile(sc, 1 - q); rec('red-degree into %d columns, top %.2f' % (k, q), sc >= thr)
# F. spectral: top right/left singular vectors of the centred red matrix (power iteration)
Hc = H - g[None, :].astype(np.float32)
v = rng.standard_normal(M).astype(np.float32)
for _ in range(60):
    v = Hc.T @ (Hc @ v); v /= np.linalg.norm(v)
sc = Hc @ v
for q in [0.5, 0.3, 0.1, 0.03]:
    rec('spectral top %.2f' % q, sc >= np.quantile(sc, 1 - q)); rec('spectral bottom %.2f' % q, sc <= np.quantile(sc, q))
del Hc
print('families A-F done (%.0f s)' % (time.time() - t0))

# G. greedy 1-flip local search (exact marginal gains, batch moves with halving)
def local_search(S, label, iters=400):
    S = S.copy(); B = max(1, int(0.002 * S.sum()))
    def cur(S):
        n = S.sum(); cS = S.astype(np.float32) @ H
        return w * log(n / N) + log(np.mean(np.exp((cS / n - g) / eps)))
    lr = cur(S)
    for it in range(iters):
        n = int(S.sum()); cS = (S.astype(np.float32) @ H).astype(np.float64)
        Am = np.exp((cS / (n - 1) - g) / eps) if n > 1 else None
        Ap = np.exp((cS / (n + 1) - g) / eps)
        gain = np.full(N, -np.inf)
        if n > 1:
            km = exp(-1 / ((n - 1) * eps))
            Erem = Am.mean() + (km - 1) * (H @ Am.astype(np.float32)) / M
            gain[S] = (w * log((n - 1) / N) + np.log(Erem[S])) - lr
        kp = exp(1 / ((n + 1) * eps))
        Eadd = Ap.mean() + (kp - 1) * (H @ Ap.astype(np.float32)) / M
        gain[~S] = (w * log((n + 1) / N) + np.log(Eadd[~S])) - lr
        pos = np.flatnonzero(gain > 1e-12)
        if len(pos) == 0: break
        top = pos[np.argsort(-gain[pos])[:B]]
        S2 = S.copy(); S2[top] = ~S2[top]
        lr2 = cur(S2)
        if lr2 > lr: S, lr = S2, lr2; B = min(2 * B, 2000)
        elif B > 1: B //= 2
        else: break
    st = rec('local search from ' + label, S)
    print('  local search from %-28s -> n %6d  log ratio in-sample %.5f  held-out %.5f  (iters %d)' % (label, st['n'], st['lr'], st['lr_ho'], it + 1))
    return S

t1 = time.time()
local_search(np.ones(N, bool), 'whole X')
local_search(np.random.default_rng(seed + 7).random(N) < 0.5, 'random half')
for t in [-1.0, 0.0, 1.0]:
    local_search((F @ a_rand()) * sqrt(R) > t, 'cap t=%.1f' % t)
local_search((F @ (U[0] / sqrt(R))) * sqrt(R) > 0.0, 'column-aligned cap t=0')
print('local searches done (%.0f s)' % (time.time() - t1))

# report: best per family (in-sample, held-out, held-out noise-corrected, exact finite r)
fam = {}
for st in results:
    k = st['kind'].split(' t=')[0].split(' (')[0].split(', top')[0]
    for key in ['lr', 'lr_ho', 'lr_ho_nc', 'lr_exact']:
        if key not in fam.get(k, {}) or st[key] > fam[k][key][key]:
            fam.setdefault(k, {})[key] = st
print('\nbest ratio per family  [in-sample | held-out cols | held-out minus row noise | exact finite r (beta=1)]  (n, kind of the in-sample best)')
for k, d in fam.items():
    b = d['lr']
    print('%-38s %8.4f | %8.4f | %8.4f | %8.4f   (n %d, %s, noise %.3f)' % (k, exp(d['lr']['lr']), exp(d['lr_ho']['lr_ho']), exp(d['lr_ho_nc']['lr_ho_nc']),
          exp(d['lr_exact']['lr_exact']), b['n'], b['kind'], b['noise']))
big = [st for st in results if st['n'] >= 1000]
for key, nm in [('lr', 'in-sample'), ('lr_ho', 'held-out'), ('lr_ho_nc', 'held-out, noise-corrected'), ('lr_exact', 'exact finite r')]:
    st = max(results, key=lambda s: s[key]); st2 = max(big, key=lambda s: s[key])
    print('largest %-26s all sets: %.4f (%s, n %d) | sets with n >= 1000: %.4f (%s, n %d)'
          % (nm, exp(st[key]), st['kind'], st['n'], exp(st2[key]), st2['kind'], st2['n']))
# single rows and tiny random sets (finite-N artefact)
for n in [1, 3, 5, 8, 10, 15, 30]:
    vals = [stats(np.isin(np.arange(N), rng.choice(N, n, replace=False))) for _ in range(20)]
    print('random sets of %3d rows: mean in-sample ratio %.3g, held-out %.3g, exact finite r %.3g'
          % (n, np.mean([exp(v['lr']) for v in vals]), np.mean([exp(v['lr_ho']) for v in vals]), np.mean([exp(v['lr_exact']) for v in vals])))
