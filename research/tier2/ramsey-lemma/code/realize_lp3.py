"""Exploration (proves nothing): realisability of ZBS's extremal configuration under SELF-SIMILARITY.
Rows in rank blocks (rank = blue-degree quantile), geometric near 0.  W_kl = blue density between blocks (symmetric).
  degree        sum_l W_kl D_l = Qbar_k
  ZBS per row   sum_l W_kl phibar_l D_l <= Psibar_k + s           (zeta <= M(Q), sum form)
  self-sim      sum_{l<=L} W_kl D_l >= a(L) T_L   for all L >= k     (relative blue degree >= a inside S_{T_L})
Minimise the measure-weighted total violation sum_k D_k s_k, s_k >= 0.  a(L) = a(x e^eta, mu e^{eta/w}); eta = 0 gives ZBS's left end a."""
import sys
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
from extremal import ROOT, envelope, left_end


def blocks(c, edges, e):
    w = c['w']; q, M, H = e['q'], e['M'], e['H']
    n = len(edges) - 1
    Qb, Pb, Fb = np.zeros(n), np.zeros(n), np.zeros(n)
    for k in range(n):
        lo, hi = edges[k], edges[k + 1]
        t = np.geomspace(max(lo, 1e-300), hi, 801) if lo == 0 or hi / max(lo, 1e-300) > 4 else np.linspace(lo, hi, 801)
        if lo == 0: t = np.concatenate([[0], t])
        ss = -np.log(np.maximum(t, 1e-300))
        idx = np.argmax(H[None, :] - w * q[None, :] * ss[:, None], axis=1)
        Qt, Mt = q[idx], M[idx]; L = hi - lo
        Qb[k] = np.trapezoid(Qt, t) / L; Pb[k] = np.trapezoid(Qt * Mt, t) / L
        I = lambda u: 0.0 if u == 0 else u * np.log(u)
        Fb[k] = -w * (I(hi) - I(lo)) / L
    return Qb, Pb, Fb


def solve(edges, Qb, Pb, Fb, aL, extra_rows=None):
    n = len(Qb); D = np.diff(edges); T = edges[1:]
    pairs = [(k, l) for k in range(n) for l in range(k, n)]
    pid = np.zeros((n, n), int)
    for i, (k, l) in enumerate(pairs): pid[k, l] = pid[l, k] = i
    nv = len(pairs) + n
    r, cidx, v = [], [], []
    # degree equalities
    for k in range(n):
        for l in range(n): r.append(k); cidx.append(pid[k, l]); v.append(D[l])
    Aeq = coo_matrix((v, (r, cidx)), shape=(n, nv)).tocsr()
    r, cidx, v = [], [], []; b = []
    row = 0
    for k in range(n):
        for l in range(n): r.append(row); cidx.append(pid[k, l]); v.append(Fb[l] * D[l])
        r.append(row); cidx.append(len(pairs) + k); v.append(-1.0); b.append(Pb[k]); row += 1
    if aL is not None:
        for k in range(n):
            for L in range(k, n - 1):
                # -sum_{l<=L} W_kl D_l <= -a(L) T_L
                for l in range(L + 1): r.append(row); cidx.append(pid[k, l]); v.append(-D[l])
                b.append(-aL[L] * T[L]); row += 1
    Aub = coo_matrix((v, (r, cidx)), shape=(row, nv)).tocsr()
    cvec = np.zeros(nv); cvec[len(pairs):] = D
    res = linprog(cvec, A_ub=Aub, b_ub=np.array(b), A_eq=Aeq, b_eq=Qb,
                  bounds=[(0, 1)] * len(pairs) + [(0, None)] * n, method='highs')
    W = res.x[pid] if res.x is not None else None
    return (res.fun if res.x is not None else np.nan), W, res


if __name__ == '__main__':
    c = ROOT; e = envelope(c)
    a0 = left_end(c['p'], c['mu'], c['w'], c['beta'], c['x'])
    print('a0 =', a0)
    for ng, nu in [(12, 24), (16, 40)]:
        edges = np.unique(np.concatenate([[0], np.geomspace(1e-12, 0.05, ng), np.linspace(0.05, 1, nu)]))
        Qb, Pb, Fb = blocks(c, edges, e)
        s0, _, _ = solve(edges, Qb, Pb, Fb, None)
        s1, W, res = solve(edges, Qb, Pb, Fb, np.full(len(Qb), a0))
        print('blocks %d: weighted violation without self-sim %.3e, with self-sim (eta=0) %.3e  [%s]' % (
            len(Qb), s0, s1, res.message[:30]), flush=True)
