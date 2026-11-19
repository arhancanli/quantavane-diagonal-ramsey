"""Exploration (proves nothing): can ZBS's extremal limiting configuration be realised by a symmetric blue graph?

Rows are cut into n quantile blocks (in blue-degree order).  Block k has blue degree Qbar_k (block mean of Q(t)),
drift phibar_k (block mean of -w(1+log t)) and needed row sum Psibar_k (block mean of Q M(Q)).  A blockwise-constant
symmetric W in [0,1] must satisfy  (1/n) sum_l W_kl = Qbar_k  and  (1/n) sum_l W_kl phibar_l <= Psibar_k + s.
We minimise the uniform slack s.  If min s stays clearly positive as n grows, ZBS's relaxation cannot be attained
and the per-row identity  zeta_i = avg_{j in B_i} phi_j  carries information that CERT throws away.
"""
import sys
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix
from extremal import ROOT, envelope


def block_data(c, n, e=None):
    if e is None: e = envelope(c)
    q, M, w = e['q'], e['M'], c['w']
    H = e['H']
    edges = np.linspace(0, 1, n + 1)
    Qb, Pb, Fb = np.zeros(n), np.zeros(n), np.zeros(n)
    for k in range(n):
        lo, hi = edges[k], edges[k + 1]
        # fine t grid inside the block, geometric near 0
        if lo == 0: t = np.geomspace(1e-30, hi, 4001)
        else: t = np.linspace(lo, hi, 2001)
        ss = -np.log(t)
        idx = np.argmax(H[None, :] - w * q[None, :] * ss[:, None], axis=1)
        Qt, Mt = q[idx], M[idx]
        L = hi - lo
        Qb[k] = np.trapezoid(Qt, t) / L
        Pb[k] = np.trapezoid(Qt * Mt, t) / L
        # exact block mean of -w(1+log t)
        def I(u): return 0.0 if u == 0 else u * np.log(u)   # int_0^u (1+log t) dt = u log u
        Fb[k] = -w * (I(hi) - I(lo)) / L
    return Qb, Pb, Fb


def min_slack(Qb, Pb, Fb, eq_deg=True):
    n = len(Qb)
    # variables: W_kl for k<=l (upper triangle incl diag), then s
    pairs = [(k, l) for k in range(n) for l in range(k, n)]
    pid = {pr: i for i, pr in enumerate(pairs)}
    nv = len(pairs) + 1
    Aeq = lil_matrix((n, nv)); beq = Qb.copy()
    Aub = lil_matrix((n, nv)); bub = Pb.copy()
    for k in range(n):
        for l in range(n):
            i = pid[(min(k, l), max(k, l))]
            Aeq[k, i] += 1.0 / n
            Aub[k, i] += Fb[l] / n
        Aub[k, nv - 1] = -1.0
    cvec = np.zeros(nv); cvec[-1] = 1.0
    bounds = [(0, 1)] * len(pairs) + [(None, None)]
    if eq_deg:
        res = linprog(cvec, A_ub=Aub.tocsr(), b_ub=bub, A_eq=Aeq.tocsr(), b_eq=beq, bounds=bounds, method='highs')
    else:
        res = linprog(cvec, A_ub=Aub.tocsr(), b_ub=bub, bounds=bounds, method='highs')
    W = np.zeros((n, n))
    for (k, l), i in pid.items(): W[k, l] = W[l, k] = res.x[i]
    return res.x[-1], W, res


if __name__ == '__main__':
    c = ROOT
    e = envelope(c)
    for n in [int(a) for a in sys.argv[1:]] or [20, 40, 80]:
        Qb, Pb, Fb = block_data(c, n, e)
        agg = np.mean(Qb * Fb) - np.mean(Pb)
        s, W, res = min_slack(Qb, Pb, Fb)
        print('n=%4d  aggregate (1/n)sum Q phi - (1/n)sum Psi = %+.3e   min uniform slack s = %+.5f  (%s)' % (
            n, agg, s, res.message[:40]), flush=True)
        if n <= 40:
            np.set_printoptions(precision=2, suppress=True, linewidth=200)
            print('Qbar', Qb); print('Psibar/Qbar', Pb / Qb); print('phibar', Fb)
            print('row values', (W @ Fb) / n / Qb)
