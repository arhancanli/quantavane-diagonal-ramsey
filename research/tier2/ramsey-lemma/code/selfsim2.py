"""Exploration (float, proves nothing): FULL self-similarity, convex model in drift-rank coordinates.

Rows ranked by drift (u), phi saturated: phi(u) = -w(1 + log u) minus desaturation eta (G_eta).  Scales v on the same
grid.  For a row in cell j and a scale s_i >= s_j (the row lies in T_{s_i}):
  F_{j,i} = |B_row cap T_{s_i}| / N    (cumulative in i, increments in [0, s_i - s_{i-1}])
  g = F_{j,i}/s_i in [a'_i, mu]        (Step 5 inside T_{s_i}; books cap at mu)
  (G)  sum_{k<=i} phi(s_k) dF_{j,k} - phibar_i F_{j,i} <= s_i H'_i(g) - w F_{j,i}   (zeta' <= M'(g), per row)
  (L)  sum_{j<=i} D_j [H'_i(g_{j,i}) - g_{j,i}(w + phi(s_j) - phibar_i)] >= 0      (within-T aggregate, exact symmetry)
i = n is ZBS's own condition (L at v = 1) plus the per-row global bound.  H'_i = H at (x e^eta_i, mu e^{eta_i/w}),
concave; replaced by the minimum of K tangents (an upper bound, so the model favours the adversary).  phi(s_k) at the
right end of a cell is the smallest drift in it (also favours the adversary).
Minimise total violation; 0 means the adversary survives at this x."""
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
from extremal import ROOT, parts, G0


def Hfun(c, x, mu):
    p, w, beta = c['p'], c['w'], c['beta']
    def H(g):
        A, B, M, C, feas = parts(np.atleast_1d(g), p, mu, w, beta, x)
        return np.where(feas, g * M + w * g, -np.inf)
    lo, hi = 1e-12, mu
    for _ in range(200):
        m = 0.5 * (lo + hi)
        if G0(m, p, mu, w, beta, x) < 0: hi = m
        else: lo = m
    return H, hi


def tangents(H, a, top, K=40):
    gs = a + (top - a) * (np.arange(1, K + 1) / K) ** 2
    gs = np.minimum(gs, top)
    eps = 1e-7
    vals = H(gs); d = (H(gs + eps) - H(gs - eps)) / (2 * eps)
    d[-1] = ((H(gs[-1]) - H(gs[-1] - eps)) / eps)[0]
    return gs, vals, d          # T_m(g) = vals_m + d_m (g - gs_m)


def model(c, s, eta, w_viol=1.0, version='A', selfsim=True, drift='right', sym=False, use=('bounds', 'G', 'L'), scales=None, box=None, nonflat=None):
    """s: grid s_1..s_n (s_n = 1).  eta: array on the grid (eta_n = 0).  Returns min total violation."""
    w, mu, x = c['w'], c['mu'], c['x']
    SC = set(range(len(s))) if scales is None else set(scales)
    n = len(s); s0 = np.concatenate([[0], s]); D = np.diff(s0)
    Phi = np.where(s0 > 0, -w * s0 * np.log(np.where(s0 > 0, s0, 1)), 0) - s0 * np.concatenate([[eta[0]], eta])
    slackG = np.zeros(len(s))
    if nonflat is not None:
        # crude worst case for non-flat top sets: Jensen gap J_i lowers the drift of T_i by s_i J_i and gives EVERY row's
        # (G) at scale i a slack (2 J_i + kappa sqrt(J_i)) per unit of blue mass inside T_i (reference shift + chi bound)
        kappa, J = nonflat
        Phi = Phi - s0 * np.concatenate([[J[0]], J])
        slackG = 2 * J + kappa * np.sqrt(J)
    phicell = np.diff(Phi) / D                  # cell-average drift (used as phi at the right end: conservative?)
    # right-end drift = smallest in the cell for decreasing phi: use cell average shifted to the right end
    phiR = np.array([-w * (1 + np.log(si)) for si in s]) - eta - s * np.gradient(eta, s)
    phiR = np.minimum(phiR, phicell)
    if drift == 'avg': phiR = phicell
    phibar = Phi[1:] / s
    if box is not None:
        # robust version: eta_i anywhere in [lo_i, hi_i]; use the adversary-favourable end in every coefficient
        elo, ehi = box
        Gc = np.where(s0 > 0, -w * s0 * np.log(np.where(s0 > 0, s0, 1)), 0)
        lo0 = np.concatenate([[elo[0]], elo]); hi0 = np.concatenate([[ehi[0]], ehi])
        phiR = (np.diff(Gc) - (s0[1:] * hi0[1:] - s0[:-1] * lo0[:-1])) / D      # smallest cell drift
        phibar = Gc[1:] / s - elo                                                  # largest phibar
        eta = ehi                                                                  # H' at the largest gap
    # variable layout
    idxF = {}; idxh = {}; nv = 0
    for j in range(n):
        for i in range(n):
            idxF[(j, i)] = nv; nv += 1
    irange = (lambda j: range(j, n)) if version == 'A' else (lambda j: range(n))
    for j in range(n):
        for i in irange(j):
            idxh[(j, i)] = nv; nv += 1
    idxL = nv; nv += n                          # sigma_i >= 0 (violation of L_i)
    idxG = {}
    for j in range(n):
        for i in irange(j):
            idxG[(j, i)] = nv; nv += 1          # rho_{j,i} >= 0
    rows, cols, vals, b = [], [], [], []; r = 0
    lb = np.zeros(nv); ub = np.full(nv, np.inf)
    lb[:] = 0
    Hs = []
    for i in range(n):
        xp, mup = x * np.exp(eta[i]), mu * np.exp(eta[i] / w)
        H, a = Hfun(c, xp, mup)
        top = mu
        gs, hv, hd = tangents(H, a * (1 + 1e-9), top)
        Hs.append((a, gs, hv, hd))
    for j in range(n):
        for i in range(n):
            k = idxF[(j, i)]; lb[k] = 0; ub[k] = s[i]
            # monotone with bounded increments
            if i > 0:
                kp = idxF[(j, i - 1)]
                rows += [r, r]; cols += [kp, k]; vals += [1, -1]; b.append(0); r += 1          # F_{i-1} - F_i <= 0
                rows += [r, r]; cols += [k, kp]; vals += [1, -1]; b.append(D[i]); r += 1       # F_i - F_{i-1} <= D_i
            else:
                ub[k] = D[0]
    for j in range(n):
        for i in irange(j):
            a, gs, hv, hd = Hs[i]
            kF = idxF[(j, i)]; kh = idxh[(j, i)]
            lb[kh] = -np.inf
            if (selfsim and 'bounds' in use and i in SC) or i == n - 1:
                lb[kF] = max(lb[kF], a * s[i])
                if i >= j: ub[kF] = min(ub[kF], mu * s[i])     # book cap only for rows of T (helper, 12:0x)
            # h <= s_i (hv_m + hd_m (F/s_i - gs_m)) = s_i (hv_m - hd_m gs_m) + hd_m F
            for m in range(len(gs)):
                rows += [r, r]; cols += [kh, kF]; vals += [1, -hd[m]]; b.append(s[i] * (hv[m] - hd[m] * gs[m])); r += 1
            if (selfsim and 'G' in use and i in SC) or i == n - 1:
                # (G): sum_{k<=i} phiR_k (F_k - F_{k-1}) - phibar_i F_i - h + w F_i <= rho
                coef = {}
                for kk in range(i + 1):
                    coef[idxF[(j, kk)]] = coef.get(idxF[(j, kk)], 0) + phiR[kk]
                    if kk > 0: coef[idxF[(j, kk - 1)]] = coef.get(idxF[(j, kk - 1)], 0) - phiR[kk]
                coef[kF] = coef.get(kF, 0) - phibar[i] + w - slackG[i]
                coef[kh] = coef.get(kh, 0) - 1
                coef[idxG[(j, i)]] = -1
                for kk, vv in coef.items(): rows.append(r); cols.append(kk); vals.append(vv)
                b.append(0); r += 1
    for i in range(n):
        if (not selfsim or 'L' not in use or i not in SC) and i < n - 1: continue
        # (L_i): - sum_{j<=i} D_j [h_{j,i}/s_i - (F_{j,i}/s_i)(w + phiR_j - phibar_i)] <= sigma_i
        for j in range(i + 1):
            rows.append(r); cols.append(idxh[(j, i)]); vals.append(-D[j] / s[i])
            rows.append(r); cols.append(idxF[(j, i)]); vals.append(D[j] * (w + phiR[j] - phibar[i]) / s[i])
        rows.append(r); cols.append(idxL + i); vals.append(-1); b.append(0); r += 1
    nub = r
    eqr, eqc, eqv = [], [], []; re = 0
    if sym:
        # block symmetry of the blue graph: D_j (F_{j,k} - F_{j,k-1}) = D_k (F_{k,j} - F_{k,j-1}), j < k
        for j in range(n):
            for k in range(j + 1, n):
                eqr += [re, re]; eqc += [idxF[(j, k)], idxF[(j, k - 1)]]; eqv += [D[j], -D[j]]
                eqr += [re]; eqc += [idxF[(k, j)]]; eqv += [-D[k]]
                if j > 0: eqr += [re]; eqc += [idxF[(k, j - 1)]]; eqv += [D[k]]
                re += 1
        # diagonal blocks need no constraint
    A = coo_matrix((vals, (rows, cols)), shape=(r, nv)).tocsr()
    Aeq = coo_matrix((eqv, (eqr, eqc)), shape=(re, nv)).tocsr() if re else None
    cvec = np.zeros(nv)
    cvec[idxL:idxL + n] = s                          # weight L_i violation by its scale (integral units)
    for (j, i), k in idxG.items(): cvec[k] = D[j] * w_viol
    for (j, i), k in idxF.items():
        if i < j and version == 'A': pass            # free (row outside T_{s_i})
    res = linprog(cvec, A_ub=A, b_ub=np.array(b), A_eq=Aeq, b_eq=(np.zeros(re) if re else None),
                  bounds=list(zip(lb, np.where(np.isinf(ub), None, ub))), method='highs')
    return res.fun if res.status == 0 else np.inf, res


def grid(nlog=10, nlin=30, smin=1e-5):
    return np.unique(np.concatenate([np.geomspace(smin, 0.05, nlog), np.linspace(0.05, 1, nlin + 1)[1:]]))


if __name__ == '__main__':
    import sys
    c0 = dict(ROOT); s = grid()
    print('grid points', len(s), flush=True)
    for da in [0.0, -1e-3, -3e-3, -1e-2, -3e-2]:
        c = dict(c0); c['x'] = c0['x'] * np.exp(-da)
        v0, r0 = model(c, s, 0 * s, selfsim=False)
        v1, r1 = model(c, s, 0 * s, selfsim=True)
        print('a-a_root %+.3f: violation ZBS-only %.3e   full self-sim (eta=0) %.3e   [%s]' % (da, v0, v1, r1.message[:25]), flush=True)
