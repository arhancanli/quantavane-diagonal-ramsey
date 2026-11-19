"""Exploration (proves nothing): the adversary's problem with SELF-SIMILARITY, mean-field limit, at one control.
Rows in rank blocks (rank = blue-degree quantile).  Given x (and the control's p, mu, w, beta) and a desaturation
profile eta(tau) >= 0 on the block edges, the adversary needs a symmetric blue density W (blocks) with
  degree        sum_l W_kl D_l = Qbar_k                       (Q = ZBS argmax quantile at this x)
  ZBS per row   sum_l W_kl phibar_l D_l <= Psibar_k + s_k     (zeta <= M(Q), sum form; s_k >= 0 violation)
  self-sim      a(eta(T_L)) T_L <= sum_{l<=L} W_kl D_l <= mu T_L   for L >= k
with phi the drift whose cumulative is G(tau) = -w tau log tau - tau eta(tau) (saturated minus desaturation).
V = min sum_k D_k s_k  (0 means the adversary survives).  a(eta) solves G0(q) = beta eta on the left branch."""
import sys
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
from extremal import ROOT, envelope, G0


def a_of_eta(c, eta):
    p, mu, w, beta, x = c['p'], c['mu'], c['w'], c['beta'], c['x']
    out = np.zeros_like(np.atleast_1d(eta), dtype=float)
    for i, et in enumerate(np.atleast_1d(eta)):
        lo, hi = 1e-12, mu
        if G0(hi, p, mu, w, beta, x) >= beta * et: out[i] = mu; continue
        for _ in range(200):
            m = 0.5 * (lo + hi)
            if G0(m, p, mu, w, beta, x) < beta * et: hi = m
            else: lo = m
        out[i] = hi
    return out


def block_data(c, edges, e, eta_edges):
    """block means of Q, Q M(Q) (ZBS argmax at c['x']) and of phi with cumulative G - tau*eta (eta linear between edges)."""
    w = c['w']; q, M, H = e['q'], e['M'], e['H']
    n = len(edges) - 1
    Qb, Pb = np.zeros(n), np.zeros(n)
    for k in range(n):
        lo, hi = edges[k], edges[k + 1]
        t = np.geomspace(max(lo, 1e-300), hi, 801) if (lo == 0 or hi / max(lo, 1e-300) > 4) else np.linspace(lo, hi, 801)
        if lo == 0: t = np.concatenate([[0], t])
        ss = -np.log(np.maximum(t, 1e-300))
        idx = np.argmax(H[None, :] - w * q[None, :] * ss[:, None], axis=1)
        Qt, Mt = q[idx], M[idx]; L = hi - lo
        Qb[k] = np.trapezoid(Qt, t) / L; Pb[k] = np.trapezoid(Qt * Mt, t) / L
    G = np.array([0.0 if u == 0 else -w * u * np.log(u) for u in edges]) - edges * eta_edges
    Fb = np.diff(G) / np.diff(edges)
    return Qb, Pb, Fb


def solve(edges, Qb, Pb, Fb, alow, mu, upper=True):
    n = len(Qb); D = np.diff(edges); T = edges[1:]
    pairs = [(k, l) for k in range(n) for l in range(k, n)]
    pid = np.zeros((n, n), int)
    for i, (k, l) in enumerate(pairs): pid[k, l] = pid[l, k] = i
    npair = len(pairs); nv = npair + n
    r, ci, v = [], [], []
    for k in range(n):
        for l in range(n): r.append(k); ci.append(pid[k, l]); v.append(D[l])
    Aeq = coo_matrix((v, (r, ci)), shape=(n, nv)).tocsr()
    r, ci, v, b = [], [], [], []; row = 0
    for k in range(n):
        for l in range(n): r.append(row); ci.append(pid[k, l]); v.append(Fb[l] * D[l])
        r.append(row); ci.append(npair + k); v.append(-1.0); b.append(Pb[k]); row += 1
    for k in range(n):
        for L in range(k, n - 1):
            if alow is not None and alow[L] > 0:
                for l in range(L + 1): r.append(row); ci.append(pid[k, l]); v.append(-D[l])
                b.append(-alow[L] * T[L]); row += 1
            if upper:
                for l in range(L + 1): r.append(row); ci.append(pid[k, l]); v.append(D[l])
                b.append(mu * T[L]); row += 1
    Aub = coo_matrix((v, (r, ci)), shape=(row, nv)).tocsr()
    cvec = np.zeros(nv); cvec[npair:] = D
    res = linprog(cvec, A_ub=Aub, b_ub=np.array(b), A_eq=Aeq, b_eq=Qb,
                  bounds=[(0, 1)] * npair + [(0, None)] * n, method='highs')
    if res.x is None: return np.inf, None, res
    return res.fun, res.x[pid], res


def default_edges(ng=14, nu=36):
    return np.unique(np.concatenate([[0], np.geomspace(1e-12, 0.05, ng), np.linspace(0.05, 1, nu)]))


def V(c, eta_fn, edges=None, e=None, upper=True, selfsim=True):
    if edges is None: edges = default_edges()
    if e is None: e = envelope(c)
    eta_e = eta_fn(edges)
    Qb, Pb, Fb = block_data(c, edges, e, eta_e)
    alow = a_of_eta(c, eta_e[1:]) if selfsim else None
    val, W, res = solve(edges, Qb, Pb, Fb, alow, c['mu'], upper and selfsim)
    return val, dict(Qb=Qb, Pb=Pb, Fb=Fb, W=W, alow=alow, edges=edges, cert=e['cert'])


if __name__ == '__main__':
    c0 = dict(ROOT)
    print('a(eta) at root:', [(et, round(float(a_of_eta(c0, et)[0]), 4)) for et in [0, 0.01, 0.03, 0.1, 0.3]])
    for da in [0.0, -1e-3, -2e-3, -4e-3]:
        c = dict(c0); c['x'] = c0['x'] * np.exp(-da)
        e = envelope(c)
        v0, _ = V(c, lambda t: 0 * t, e=e, selfsim=False)
        v1, _ = V(c, lambda t: 0 * t, e=e)
        print('a - a_root = %+.4f  CERT %+.3e  V(ZBS only) %.3e  V(self-sim, eta=0) %.3e' % (da, e['cert'], v0, v1), flush=True)
