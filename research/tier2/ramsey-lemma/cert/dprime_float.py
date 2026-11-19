"""Float evaluator (exploration; proves nothing) of Lemma D' with Lemma DL (a)'s grid relaxation.

For a drift given by its cumulative Phi on a fine grid, the u_b-row's GRID CHAIN is the LP
  min F_m  s.t.  F nondecreasing, DF_k <= Delta_k, F_k >= 0;  for every chain scale i (v_i > u_b):
                 a(eta~_i) v_i <= F_i <= mu v_i,
                 sum_{k <= i} DF_k sigma_{k+1} - Phibar_i F_i <= tau_i,  tau_i <= v_i T_ij(F_i / v_i)  (tangents of g M'_i(g))
(sigma = next chord slope, Lemma DL (a); tangents of the concave g M'_i(g) are upper bounds, so the LP value is a
LOWER bound of Q~ and of Q_min).  V_D' = int_0^{u_b} sup_{q >= Q_min} [q M(q) - q phi(u)] + int_{u_b}^1 Hhat(phi)."""
import sys
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from explore1 import parts, a_of   # noqa: E402


def left_end(c, eta):
    """a(eta): left root of G0 = beta eta (0 if none)."""
    return a_of(eta, c)


class DPrime:
    def __init__(self, c, scales, ub, nq=4000, K=30):
        self.c = c; self.w = c['w']; self.mu = c['mu']; self.ub = ub
        self.v = np.asarray(scales); assert abs(self.v[-1] - 1) < 1e-15
        self.b = int(np.searchsorted(self.v, ub)); assert abs(self.v[self.b] - ub) < 1e-12
        self.K = K
        self.a0 = a_of(0, c)
        self.qg = np.linspace(self.a0 * (1 + 1e-9), self.mu, nq)
        M0 = parts(self.qg, c['p'], c['mu'], c['w'], c['beta'], c['x'])
        self.M0 = M0; self.ok0 = np.isfinite(M0)

    def gM_tangents(self, eta):
        c = self.c
        a = left_end(c, eta) if eta > 0 else self.a0
        lo = max(a, 1e-6) * (1 + 1e-7)
        gs = lo + (self.mu - lo) * (np.arange(1, self.K + 1) / self.K) ** 1.5
        f = lambda g: g * parts(np.atleast_1d(g), c['p'], c['mu'] * np.exp(eta / c['w']), c['w'], c['beta'], c['x'] * np.exp(eta))
        val = f(gs); h = 1e-7
        d = (f(np.minimum(gs + h, self.mu)) - f(gs - h)) / (np.minimum(gs + h, self.mu) - (gs - h))
        okk = np.isfinite(val) & np.isfinite(d)
        return a, gs[okk], val[okk], d[okk]

    def qmin(self, Phi_at_v, phi_last=None):
        """Phi_at_v: Phi at the scales v (cumulative).  Returns the LP lower bound of Q_min (np.inf if infeasible)."""
        v = self.v; w = self.w; n = len(v); b = self.b
        v0 = np.concatenate([[0.0], v]); P0 = np.concatenate([[0.0], Phi_at_v])
        Dl = np.diff(v0)
        sig = np.diff(P0) / Dl                      # sigma_k, k = 1..n  (index 0..n-1)
        signext = np.concatenate([sig[1:], [-w]])   # sigma_{k+1} for cell k
        Phibar = Phi_at_v / v
        eta = np.maximum(-w * np.log(v) - Phibar, 0.0); eta[-1] = 0.0
        # variables: F_0..F_{n-1} (F at v_k), tau_i for chain scales i > b
        chain = list(range(b + 1, n)); nc = len(chain)
        nv = n + nc
        rows, cols, vals, rhs = [], [], [], []; r = 0
        def add(cs, vs, rh):
            nonlocal r
            rows.extend([r] * len(cs)); cols.extend(cs); vals.extend(vs); rhs.append(rh); r += 1
        lb = np.zeros(nv); ub = np.full(nv, np.inf)
        ub[0] = Dl[0]
        for k in range(1, n):
            add([k - 1, k], [1, -1], 0.0)            # F_{k-1} <= F_k
            add([k, k - 1], [1, -1], Dl[k])          # F_k - F_{k-1} <= Delta_k
            ub[k] = v[k]
        # shifted control (x e^eta, mu e^{eta/w}) must stay in the domain x' < p, mu' < 1; outside it Lemma D' gives no
        # (B') or (G') constraint at that scale, so none is imposed (adversary-favourable; 18 Nov, lane agent's finding)
        cc = self.c
        dom = (cc['x'] * np.exp(eta) < cc['p']) & (cc['mu'] * np.exp(eta / w) < 1)
        for jj, i in enumerate(chain):
            if not dom[i]:
                ub[i] = min(ub[i], v[i]); lb[n + jj] = -np.inf
                continue
            a, gs, val, d = self.gM_tangents(eta[i])
            lb[i] = max(lb[i], a * v[i]); ub[i] = min(ub[i], self.mu * v[i])
            ti = n + jj; lb[ti] = -np.inf
            # sum_{k<=i} DF_k sig_{k+1} - Phibar_i F_i - tau_i <= 0 ; DF_k = F_k - F_{k-1}
            coef = {}
            for k in range(0, i + 1):
                coef[k] = coef.get(k, 0.0) + signext[k]
                if k > 0: coef[k - 1] = coef.get(k - 1, 0.0) - signext[k]
            coef[i] = coef.get(i, 0.0) - Phibar[i]
            coef[ti] = -1.0
            add(list(coef.keys()), list(coef.values()), 0.0)
            # tau_i <= v_i (val_m + d_m (F_i/v_i - gs_m))
            for m_ in range(len(gs)):
                add([ti, i], [1.0, -d[m_]], v[i] * (val[m_] - d[m_] * gs[m_]))
        A = coo_matrix((vals, (rows, cols)), shape=(r, nv)).tocsr()
        cvec = np.zeros(nv); cvec[n - 1] = 1.0
        res = linprog(cvec, A_ub=A, b_ub=np.array(rhs), bounds=list(zip(lb, np.where(np.isinf(ub), None, ub))),
                      method='highs')
        if res.status == 2: return np.inf
        if res.status != 0: raise RuntimeError('LP status %d' % res.status)
        return res.fun

    def V(self, t, Phi):
        """t: fine grid with t[-1] = 1 containing the scales; Phi on t (concave).  Returns V_D' and Q_min."""
        w = self.w
        t0 = np.concatenate([[0.0], t]); P0 = np.concatenate([[0.0], Phi])
        phi = np.diff(P0) / np.diff(t0)
        if np.any(np.diff(phi) > 1e-9) or phi[-1] < -w - 1e-9: return np.nan, np.nan
        Pv = np.interp(self.v, t, Phi)
        Q = self.qmin(Pv)
        width = np.diff(t0)
        q, M = self.qg[self.ok0], self.M0[self.ok0]
        Vt = 0.0
        selQ = q >= Q
        if not selQ.any(): return -np.inf, Q
        for k in range(len(t)):
            if t[k] <= self.ub:
                Vt += width[k] * np.max(q[selQ] * (M[selQ] - phi[k]))
            else:
                Vt += width[k] * np.max(q * (M - phi[k]))
        return Vt, Q
