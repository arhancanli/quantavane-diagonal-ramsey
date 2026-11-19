"""Float evaluator (exploration; proves nothing) of the per-row chain in its comparison form (CERT_DESIGN.md S-C):

For a drift given by a concave piecewise-linear Phi on a scale grid t_0 < ... < t_n = 1 (Phi(0) = 0), cell k = (t_{k-1}, t_k]
has drift phi_k; Gamma_k = Phi(t_k)/t_k - phi_k (spread of T_k), eta_k = -w log t_k - Phi(t_k)/t_k (desaturation).
A row of cell j (in T_k for k >= j) with blue counts F_k = |B cap T_k|/N (nondecreasing, 1-Lipschitz):
  S_k = sum_{i<k} F_i (phi_i - phi_{i+1})                       (S4 summation by parts)
  (G_k)  S_k <= F_k (Gamma_k + M'_k(g_k)),  g_k = F_k / t_k in [a(eta_k), mu]
and (G_n) at t_n = 1 is ZBS's row bound.  Equivalently D_k = Gamma_k - S_k/F_k >= -M'_k(g_k), and in the continuum
dD = -D dlog t + (S/F) dlog g: drift drops cancel, the chain advances only through the row's growth of g.
q_min(j) = least reachable F_n (greedy: least feasible F_k at every scale).  V = int sup_{q in [q_min, mu] cap F}
q (M(q) - phi(u)) du; the adversary survives iff V >= 0 (with every row reachable)."""
import sys
import numpy as np

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from explore1 import parts, a_of   # noqa: E402


class Chain:
    def __init__(self, c, t, nq=3000):
        self.c = c; self.t = t; self.w = c['w']; self.mu = c['mu']
        p, mu, w, beta, x = c['p'], c['mu'], c['w'], c['beta'], c['x']
        self.a0 = a_of(0, c)
        self.qg = np.linspace(self.a0 * 0.5, mu, nq)          # q grid (shifted feasible sets extend left)
        M0 = parts(self.qg, p, mu, w, beta, x)
        self.M0 = np.where(np.isfinite(M0), M0, -np.inf)

    def Mshift(self, eta):
        c = self.c
        out = []
        for e in eta:
            M = parts(self.qg, c['p'], c['mu'] * np.exp(e / c['w']), c['w'], c['beta'], c['x'] * np.exp(e))
            out.append(np.where(np.isfinite(M), M, -np.inf))
        return np.array(out)

    def V(self, Phi, detail=False):
        t = self.t; w = self.w; mu = self.mu; n = len(t)
        t0 = np.concatenate([[0.0], t]); P0 = np.concatenate([[0.0], Phi])
        phi = np.diff(P0) / np.diff(t0)                       # cell drifts, phi[k] on (t_{k-1}, t_k]
        if np.any(np.diff(phi) > 1e-9) or phi[-1] < -w - 1e-9:
            return np.nan
        Phibar = Phi / t
        Gam = Phibar - phi
        eta = np.maximum(-w * np.log(t) - Phibar, 0.0)
        eta[-1] = 0.0
        Ms = self.Mshift(eta); Ms[-1] = self.M0
        qg = self.qg
        cap = qg <= mu
        drop = np.concatenate([phi[:-1] - phi[1:], [0.0]])      # drop at t_k between cell k and k+1
        Vtot = 0.0; qmins = np.full(n, np.nan); bad = 0.0
        for j in range(n):
            # rows of cell j; constraints at scales k >= j
            F = 0.0; S = 0.0; ok = True
            for k in range(j, n):
                lo_F = F if k > j else 0.0
                hi_F = (F + (t[k] - (t[k - 1] if k > 0 else 0.0))) if k > j else t[k]
                gl = np.maximum(qg, 0) * t[k]
                if k == j:
                    # neighbours above the row packed at the bottom of T_k: F_i = max(0, F_j - (t_j - t_i))
                    Ssum = np.array([np.sum(np.maximum(0.0, f - (t[k] - t[:k])) * drop[:k]) for f in gl])
                else:
                    Ssum = np.full_like(gl, S)
                rhs = gl * (Gam[k] + Ms[k])
                feas = cap & np.isfinite(Ms[k]) & (rhs >= Ssum) & (gl >= lo_F - 1e-15) & (gl <= hi_F + 1e-15)
                if not feas.any():
                    ok = False; break
                i0 = np.argmax(feas)
                Fnew = gl[i0]
                if k == j:
                    S = Ssum[i0]
                if k < n - 1:
                    S = S + Fnew * drop[k]
                F = Fnew
            width = t[j] - (t[j - 1] if j > 0 else 0.0)
            if not ok:
                qmins[j] = np.inf; bad += width
                continue
            qmin = F
            qmins[j] = qmin
            sel = (qg >= qmin - 1e-15) & cap & np.isfinite(self.M0) & (qg > self.a0)
            Vtot += width * np.max(qg[sel] * (self.M0[sel] - phi[j]))
        # infeasible rows: the drift is impossible (V = -inf); 'pen' is a guide for searches
        self.bad = bad
        pen = Vtot - 10.0 * bad
        if detail: return (Vtot if bad == 0 else -np.inf), pen, qmins
        return Vtot if bad == 0 else -np.inf

    def V_zbs(self, Phi):
        t = self.t; t0 = np.concatenate([[0.0], t]); P0 = np.concatenate([[0.0], Phi])
        phi = np.diff(P0) / np.diff(t0)
        sel = np.isfinite(self.M0) & (self.qg > self.a0) & (self.qg <= self.mu)
        q, M = self.qg[sel], self.M0[sel]
        return float(np.sum(np.diff(t0) * np.max(q[None, :] * (M[None, :] - phi[:, None]), axis=1)))


def sat(t, w):
    return -w * t * np.log(t)


def from_eta(t, w, eta_fun):
    return -w * t * np.log(t) - t * eta_fun(t)


if __name__ == '__main__':
    import json, time
    from fractions import Fraction as Fr
    ctl = {k: float(Fr(v)) for k, v in json.load(open(sys.argv[1])).items()}
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    t = np.geomspace(1e-8, 1, n)
    for da in [0.0, -5e-4, -1e-3]:
        c = dict(ctl); c['x'] = ctl['x'] * np.exp(-da)
        C = Chain(c, t); w = c['w']
        P = sat(t, w); t1 = time.time()
        print('da %+.4f: ZBS %.3e  chain(saturated) %.3e  (%.1fs)' % (da, C.V_zbs(P), C.V(P), time.time() - t1), flush=True)


class Chain2(Chain):
    """Scales are a SUBSET of the drift grid: the drift is piecewise linear on the fine grid t (so drops happen
    anywhere between scales: the within-cell shape is the adversary's), (G) and (B) hold only at the scales
    t[sidx].  Rows choose F on the fine grid: between scales F stays as low as monotonicity and the 1-Lipschitz bound
    allow (that minimises S), so S over a scale cell is sum_k max(F_prev, F_next - (t_next - t_k)) drop_k."""

    def __init__(self, c, t, sidx, nq=3000):
        super().__init__(c, t, nq)
        self.sidx = np.asarray(sidx)

    def V(self, Phi, detail=False):
        t = self.t; w = self.w; mu = self.mu; n = len(t); sidx = self.sidx; m = len(sidx)
        t0 = np.concatenate([[0.0], t]); P0 = np.concatenate([[0.0], Phi])
        phi = np.diff(P0) / np.diff(t0)
        if np.any(np.diff(phi) > 1e-9) or phi[-1] < -w - 1e-9:
            return np.nan
        drop = np.concatenate([phi[:-1] - phi[1:], [0.0]])     # drop located at t_k
        ts = t[sidx]; Phibar = Phi[sidx] / ts
        Gam = Phibar - phi[sidx]                                 # smallest drift in T_s is the cell below t_s
        eta = np.maximum(-w * np.log(ts) - Phibar, 0.0); eta[-1] = 0.0
        Ms = self.Mshift(eta); Ms[-1] = self.M0
        qg = self.qg; cap = qg <= mu
        qmin_s = np.full(m, np.inf)
        for a in range(m):                       # rows of scale cell a enter at scale a
            F = 0.0; S = 0.0; ok = True
            for i in range(a, m):
                k1 = sidx[i]
                k0 = sidx[i - 1] if i > 0 else -1
                gl = np.maximum(qg, 0) * ts[i]
                if i == a:
                    ks = np.arange(0, k1)                # every fine point above the scale (drops at t_k, k < k1)
                    Fk = np.maximum(0.0, gl[:, None] - (ts[i] - t[ks])[None, :])
                    Ssum = Fk @ drop[ks]
                    lo_F, hi_F = 0.0, ts[i]
                else:
                    ks = np.arange(k0, k1)               # drops at t_k0 .. t_{k1-1}
                    Fk = np.maximum(F, gl[:, None] - (ts[i] - t[ks])[None, :])
                    Ssum = S + Fk @ drop[ks]
                    lo_F, hi_F = F, F + (ts[i] - ts[i - 1])
                rhs = gl * (Gam[i] + Ms[i])
                feas = cap & np.isfinite(Ms[i]) & (rhs >= Ssum) & (gl >= lo_F - 1e-15) & (gl <= hi_F + 1e-15)
                if not feas.any():
                    ok = False; break
                i0 = np.argmax(feas)
                F = gl[i0]; S = Ssum[i0]
            if ok: qmin_s[a] = F
        # rows: fine cell k belongs to scale cell a(k) = first scale index with sidx >= k
        acell = np.searchsorted(sidx, np.arange(n))
        width = np.diff(t0)
        Vtot = 0.0; bad = 0.0
        sel0 = np.isfinite(self.M0) & (qg > self.a0) & cap
        for k in range(n):
            qm = qmin_s[acell[k]]
            if not np.isfinite(qm):
                bad += width[k]; continue
            sel = sel0 & (qg >= qm - 1e-15)
            Vtot += width[k] * np.max(qg[sel] * (self.M0[sel] - phi[k]))
        self.bad = bad
        pen = Vtot - 10.0 * bad
        if detail: return (Vtot if bad == 0 else -np.inf), pen, qmin_s
        return Vtot if bad == 0 else -np.inf
