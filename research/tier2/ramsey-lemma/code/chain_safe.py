"""Conservative (adversary-favourable) evaluation of the flat chain (bounds + G, version A) after referee 2 (12:xx):
the cell-average drift used in selfsim2/chain_rows favours the DEFENDER when the drift varies inside a cell.
Fixes, for a drift whose cumulative Phi is known exactly (here Phi(v) = -w v log v - v eta(v)):
 - (G): the blue mass dF_k a row puts in scale cell k is placed at the LOW-drift end of the cell (density <= 1), so its
   contribution is bounded below by c_k(dF_k) = Phi(s_k) - Phi(s_k - dF_k), a convex function (Phi concave); epigraph
   variables t_k >= tangent lines of c_k (finitely many tangents give a smaller t, i.e. favour the adversary);
 - ZBS's aggregate: a row in cell (s_{j-1}, s_j] has drift >= phi(s_j) (right end, the smallest), so its objective
   H(q) - q(w + phi(u)) is bounded above by the value at phi(s_j);
 - H'_i: minimum of tangents (upper bound, favours the adversary), as before.
V_safe <= 0 everywhere means: for this eta the adversary fails even under these relaxations."""
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
from extremal import ROOT
from selfsim2 import grid, Hfun, tangents


def Phi_fun(w, eta_fun):
    return lambda v: np.where(v > 0, -w * v * np.log(np.where(v > 0, v, 1)) - v * eta_fun(v), 0.0)


def chain_safe(c, s, eta_fun, K=40, Kc=12, nsub=200, zbs_only=False):
    w, mu, x = c['w'], c['mu'], c['x']
    n = len(s); s0 = np.concatenate([[0], s]); D = np.diff(s0)
    Phi = Phi_fun(w, eta_fun)
    eta = eta_fun(s)
    phibar = Phi(s) / s
    # right-end drift of each cell: phi(s_j) = Phi'(s_j) (numerical derivative from the left)
    h = 1e-9 * s
    phiR = (Phi(s) - Phi(s - h)) / h
    # convex lower bounds c_k(x) = Phi(s_k) - Phi(s_k - x), x in [0, D_k]; tangents at Kc points
    ctan = []
    for k in range(n):
        xs = D[k] * (np.arange(Kc) + 0.5) / Kc
        val = Phi(s[k]) - Phi(s[k] - xs)
        der = (Phi(s[k] - xs + 1e-9 * D[k]) - Phi(s[k] - xs - 1e-9 * D[k])) / (2e-9 * D[k])   # = phi(s_k - x)
        ctan.append((xs, val, der))                              # c_k(x) >= val_m + der_m (x - xs_m)
    T = []
    for i in range(n):
        xp, mup = x * np.exp(eta[i]), mu * np.exp(eta[i] / w)
        if not (np.isfinite(eta[i]) and xp < c['p'] and mup < 1):
            # 18 Nov 15:4x: shifted control outside the valid domain -> DROP (B'_i) and (G_i) at this scale
            # (adversary-favourable relaxation; before this fix such scales could make the LP infeasible -> -inf,
            # which favoured the defender)
            T.append(None); continue
        H, a = Hfun(c, xp, mup)
        gs, hv, hd = tangents(H, a * (1 + 1e-9), mu, K)
        ok = np.isfinite(hv) & np.isfinite(hd)                  # fewer tangents = larger envelope (relaxation)
        T.append((a, gs[ok], hv[ok], hd[ok]) if ok.any() else None)
    Hroot, aroot = Hfun(c, x, mu)
    qgrid = np.linspace(aroot * (1 + 1e-9), mu, 4001); Hq = Hroot(qgrid)
    V = 0.0
    for j in range(n):
        # variables: F_0..F_{n-1}, t_0..t_{n-1}
        nv = 2 * n
        r, ci, vv, b = [], [], [], []; row = 0
        def add(cols, vals, rhs):
            nonlocal row
            r.extend([row] * len(cols)); ci.extend(cols); vv.extend(vals); b.append(rhs); row += 1
        for i in range(1, n):
            add([i - 1, i], [1, -1], 0.0)                       # F_{i-1} <= F_i
            add([i, i - 1], [1, -1], D[i])                      # F_i - F_{i-1} <= D_i
        for k in range(n):
            xs, val, der = ctan[k]
            for m in range(len(xs)):
                # t_k >= val_m + der_m (dF_k - xs_m)  <=>  der_m dF_k - t_k <= der_m xs_m - val_m
                if k == 0: add([0, n + k], [der[m], -1], der[m] * xs[m] - val[m])
                else: add([k, k - 1, n + k], [der[m], -der[m], -1], der[m] * xs[m] - val[m])
        bounds = [(0, s[i]) for i in range(n)] + [(None, None)] * n
        bounds[0] = (0, D[0])
        for i in (range(j, n) if not zbs_only else [n - 1]):
            if T[i] is None: continue
            a, gs, hv, hd = T[i]
            bounds[i] = (max(bounds[i][0], a * s[i]), min(bounds[i][1], mu * s[i]))
            # G: sum_{k<=i} t_k + (w - phibar_i) F_i <= s_i T_m(F_i/s_i)
            for m in range(len(gs)):
                cols = list(range(n, n + i + 1)) + [i]
                vals = [1.0] * (i + 1) + [w - phibar[i] - hd[m]]
                add(cols, vals, s[i] * (hv[m] - hd[m] * gs[m]))
        A = coo_matrix((vv, (r, ci)), shape=(row, nv)).tocsr(); b = np.array(b)
        ends = []
        for sgn in (1, -1):
            cvec = np.zeros(nv); cvec[n - 1] = sgn
            res = linprog(cvec, A_ub=A, b_ub=b, bounds=bounds, method='highs')
            if res.status == 2: ends.append(np.nan); continue            # infeasible: no reachable q (genuine)
            if res.status != 0: raise RuntimeError('LP status %d at cell %d (referee 3: never score as -inf)' % (res.status, j))
            ends.append(res.x[n - 1])
        qlo, qhi = ends
        if not np.isfinite(qlo): return -np.inf
        msk = (qgrid >= qlo - 1e-12) & (qgrid <= qhi + 1e-12)
        if not msk.any(): return -np.inf
        # rows of scale cell j share the same reachable interval; integrate their objective over nsub sub-cells,
        # each with its own smallest (right-end) drift
        lo_ = s0[j]; hi_ = s[j]
        edges = np.geomspace(max(lo_, hi_ * 1e-12), hi_, nsub + 1) if lo_ == 0 else np.linspace(lo_, hi_, nsub + 1)
        if lo_ == 0: edges[0] = 0.0
        right = edges[1:]; hh = 1e-9 * right
        phisub = (Phi(right) - Phi(right - hh)) / hh
        qe = np.array([max(qlo, qgrid[0]), min(qhi, mu)]); He = Hroot(qe)       # exact interval ends (referee 3)
        Hm, qm = np.concatenate([Hq[msk], He]), np.concatenate([qgrid[msk], qe])
        best = np.max(Hm[None, :] - qm[None, :] * (w + phisub[:, None]), axis=1)
        V += np.sum(np.diff(edges) * best)
    return V


if __name__ == '__main__':
    import sys, time
    c0 = dict(ROOT)
    for (nl, nn) in [(10, 30), (16, 50)]:
        s = grid(nl, nn, 1e-6)
        # calibration: ZBS alone (constraints only at v = 1) must be ~0 at a_root and > 0 above
        for da in [0.0, -0.001, -0.0015, -0.002, -0.0025]:
            c = dict(c0); c['x'] = c0['x'] * np.exp(-da); t0 = time.time()
            vz = chain_safe(c, s, lambda v: 0 * v, zbs_only=True)
            print('cells %d da %+.4f: ZBS-only calibration V %+.2e' % (len(s), da, vz), flush=True)
            vals = []
            for A in (0.01, 0.02, 0.03):
                vals.append(chain_safe(c, s, lambda v, A=A: A * np.log(1 / np.maximum(v, 1e-300))))
            print('cells %d da %+.4f: V_safe for A=.01/.02/.03: %s  (%.0f s)' % (len(s), da, ' '.join('%+.2e' % v for v in vals), time.time() - t0), flush=True)
