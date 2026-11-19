"""Second, independent evaluation (float, exploration) of the flat model WITHOUT the within-T aggregate (L) and
without symmetry: per-row chain only.  For each drift-rank cell j the set of reachable degrees q = F(1) of a row in
that cell is an interval [qlo, qhi] (the per-row constraint set is convex); each end is one small LP in the row's
cumulative blue profile F(s_1..s_n) with EXACT H' evaluated through dense tangents.  Then
  V = sum_j D_j sup_{q in [qlo_j, qhi_j]} [H(q) - q (w + phi_j)]   (ZBS's aggregate with the restricted rows);
V < 0 means the adversary fails.  Must agree with selfsim2.model(..., use=('bounds','G')) on the sign."""
import numpy as np
from scipy.optimize import linprog
from extremal import ROOT, parts, G0
from selfsim2 import grid, Hfun, tangents


def chain_value(c, s, eta, K=80, version='A'):
    w, mu, x = c['w'], c['mu'], c['x']
    n = len(s); s0 = np.concatenate([[0], s]); D = np.diff(s0)
    Phi = np.where(s0 > 0, -w * s0 * np.log(np.where(s0 > 0, s0, 1)), 0) - s0 * np.concatenate([[eta[0]], eta])
    phi = np.diff(Phi) / D; phibar = Phi[1:] / s
    T = []
    for i in range(n):
        H, a = Hfun(c, x * np.exp(eta[i]), mu * np.exp(eta[i] / w))
        gs, hv, hd = tangents(H, a * (1 + 1e-9), mu, K)
        T.append((a, gs, hv, hd))
    Hroot, aroot = Hfun(c, x, mu)
    qgrid = np.linspace(aroot * (1 + 1e-9), mu, 4001); Hq = Hroot(qgrid)
    V = 0.0; rows = []
    for j in range(n):
        # variables F_0..F_{n-1}; constraints for i >= j
        A, b = [], []
        for i in range(n):
            if i > 0:
                r1 = np.zeros(n); r1[i - 1] = 1; r1[i] = -1; A.append(r1); b.append(0)
                r2 = np.zeros(n); r2[i] = 1; r2[i - 1] = -1; A.append(r2); b.append(D[i])
        bounds = [(0, s[i]) for i in range(n)]; bounds[0] = (0, D[0])
        for i in (range(j, n) if version == 'A' else range(n)):
            a, gs, hv, hd = T[i]
            # version B (rows outside T_i too, global coordinates; flatness helper 12:0x): lower bound and G, no book cap
            bounds[i] = (max(bounds[i][0], a * s[i]), min(bounds[i][1], mu * s[i]) if i >= j else bounds[i][1])
            # G: sum_k phi_k dF_k - phibar_i F_i + w F_i <= s_i T_m(F_i/s_i) for every tangent m
            base = np.zeros(n)
            for k in range(i + 1):
                base[k] += phi[k]
                if k > 0: base[k - 1] -= phi[k]
            base[i] += -phibar[i] + w
            for m in range(len(gs)):
                rr = base.copy(); rr[i] -= hd[m]
                A.append(rr); b.append(s[i] * (hv[m] - hd[m] * gs[m]))
        A = np.array(A); b = np.array(b)
        ends = []
        for sgn in (1, -1):
            cvec = np.zeros(n); cvec[-1] = sgn
            res = linprog(cvec, A_ub=A, b_ub=b, bounds=bounds, method='highs')
            ends.append(res.x[-1] if res.status == 0 else np.nan)
        qlo, qhi = ends
        if not np.isfinite(qlo): return -np.inf, None
        m = (qgrid >= qlo - 1e-12) & (qgrid <= qhi + 1e-12)
        if not m.any(): return -np.inf, None
        best = np.max(Hq[m] - qgrid[m] * (w + phi[j]))
        V += D[j] * best; rows.append((s[j], qlo, qhi))
    return V, rows


if __name__ == '__main__':
    c0 = dict(ROOT); s = grid(10, 30, 1e-6)
    for da in [0.0, -0.001, -0.002]:
        c = dict(c0); c['x'] = c0['x'] * np.exp(-da)
        v0, _ = chain_value(c, s, 0 * s)
        print('a-a_root %+.4f eta = 0: chain-only V = %+.4e' % (da, v0), flush=True)
