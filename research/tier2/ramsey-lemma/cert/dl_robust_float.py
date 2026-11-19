"""Float estimate (exploration; proves nothing) of what a LINEARISED robust bound for Lemma D' keeps at the saturated box
(Phi_b = g(u_b), m_b = 0).  Design "L1" (the simplest bound that is valid for every row profile F):

Reference LP at m = 0 (grid chain of Lemma DL (a), with B1's fix: supporting planes P_r of the jointly concave
K(g, eta) = g M_eta(g) + w g - g eta, valid on the whole domain {g > a(eta)}), plus F_i >= a(eta_i) v_i >= (a0 v_i - alpha m_i):
  min F_n  s.t.  sum_{k<=i} DF_k sig_{k+1} + F_i w (1 + log v_i) <= v_i P_r(F_i/v_i, eta_i)  (chain scales i, planes r),
                 0 <= DF_k <= Delta_k,  F_i <= mu v_i,  F_i >= a0 v_i.
Partial Lagrangian with the optimal duals y (planes) and z (lower bounds), keeping 0 <= DF_k <= Delta_k inside:
for every deficit vector m and every F feasible under m,
  F_n >= Q_ref - S(m),  S(m) = sum_k Delta_k Y_k ((m_{k+1} - m_k)/Delta_{k+1})_+ + sum_i (E_i)_+ m_i + alpha sum_i z_i m_i,
  Y_k = sum_{i >= k} sum_r y_ir,  E_i = sum_r y_ir dK/deta_r  (eta_i <= m_i / v_i).
Left region: IL(Q) is concave in Q, so IL(Q_ref - S) <= IL(Q_ref) + |IL'(Q_ref)| S.
Right region (Lemma D (B), first order of the charge): int Hhat(phi) <= int Hhat(phi_s) - int m dQ, and int m dQ >= sum over
chain cells of kappa(level) m_k drop_k(m) with drop_k(m) the ACTUAL chord drop (>= 0), kappa = local slope of qhat (optimistic).
So V(m) <= V_ref + |IL'| S(m) - Z(m), and the certificate at this box needs  V_ref + sup_m [|IL'| S(m) - Z(m)] < 0.
The sup is searched over bump families plus a local refinement (an ESTIMATE of the bound's loss, not a bound).
Constraints on m: m >= 0, m_b = m_end = 0, drift nonincreasing and >= -w, m_k <= g(v_k) + (1 - v_k) sig_k(m)."""
import sys
import numpy as np
from scipy.optimize import linprog, minimize
from scipy.sparse import coo_matrix

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from explore1 import parts, a_of   # noqa: E402
from dprime_float import DPrime   # noqa: E402


def Kfun(c, g, eta):
    M = parts(np.atleast_1d(g), c['p'], c['mu'] * np.exp(eta / c['w']), c['w'], c['beta'], c['x'] * np.exp(eta))
    return g * M + c['w'] * g - g * eta


def planes(c, a0, mu, etas=(0.0, 0.005, 0.02, 0.05, 0.1), ng=40):
    out = []
    for e in etas:
        lo = a_of(e, c) if e > 0 else a0
        for g in lo + (mu - lo) * (np.arange(1, ng + 1) / (ng + 1)) ** 1.5:
            h = 1e-7
            K0 = Kfun(c, g, e)[0]
            Kg = (Kfun(c, min(g + h, mu), e)[0] - Kfun(c, g - h, e)[0]) / (min(g + h, mu) - g + h)
            Ke = (Kfun(c, g, e + h)[0] - Kfun(c, g, max(e - h, 0))[0]) / (h + min(h, e))
            if np.isfinite(K0) and np.isfinite(Kg) and np.isfinite(Ke):
                out.append((K0, Kg, Ke, g, e))
    return out


def reference(c, v, b):
    w, mu = c['w'], c['mu']; n = len(v)
    a0 = a_of(0, c); P = planes(c, a0, mu)
    v0 = np.concatenate([[0.0], v]); Dl = np.diff(v0)
    sig = np.diff(np.concatenate([[0.0], -w * v * np.log(v)])) / Dl
    signext = np.concatenate([sig[1:], [-w]])
    rows, cols, vals, rhs, tags = [], [], [], [], []; r = 0
    def add(cs, vs, rh, tag=None):
        nonlocal r
        rows.extend([r] * len(cs)); cols.extend(cs); vals.extend(vs); rhs.append(rh); tags.append(tag); r += 1
    lb = np.zeros(n); ub = np.array(v, dtype=float); ub[0] = Dl[0]
    for k in range(1, n):
        add([k - 1, k], [1, -1], 0.0); add([k, k - 1], [1, -1], Dl[k])
    for i in range(b + 1, n):
        ub[i] = min(ub[i], mu * v[i])
        add([i], [-1.0], -a0 * v[i], ('low', i, 0.0))
        base = {}
        for k in range(0, i + 1):
            base[k] = base.get(k, 0.0) + signext[k]
            if k > 0: base[k - 1] = base.get(k - 1, 0.0) - signext[k]
        base[i] = base.get(i, 0.0) + w * (1 + np.log(v[i]))
        for (K0, Kg, Ke, g0, e0) in P:
            coef = dict(base); coef[i] = coef.get(i, 0.0) - Kg
            add(list(coef.keys()), list(coef.values()), v[i] * (K0 - Kg * g0 - Ke * e0), ('pl', i, Ke))
    A = coo_matrix((vals, (rows, cols)), shape=(r, n)).tocsr()
    cvec = np.zeros(n); cvec[-1] = 1.0
    res = linprog(cvec, A_ub=A, b_ub=np.array(rhs), bounds=list(zip(lb, ub)), method='highs')
    assert res.status == 0, res.message
    y = -res.ineqlin.marginals
    yi = np.zeros(n); E = np.zeros(n); z = np.zeros(n)
    for yy, tg in zip(y, tags):
        if tg is None or yy <= 0: continue
        if tg[0] == 'pl': yi[tg[1]] += yy; E[tg[1]] += yy * tg[2]
        else: z[tg[1]] += yy
    Y = np.cumsum(yi[::-1])[::-1]
    return res.fun, Y, E, z, Dl, sig, res.x


class Adv:
    def __init__(self, c, v, b, ILp, Y, E, z, alpha, Dl, sig, kap_of, chain_only, Hhat=None):
        self.v, self.b, self.ILp, self.Y, self.E, self.z, self.alpha = v, b, ILp, Y, E, z, alpha
        self.Dl, self.sig, self.kap_of, self.w = Dl, sig, kap_of, c['w']
        n = len(v); self.n = n
        lo = b if chain_only else 1
        self.idx = np.array([k for k in range(lo, n - 1) if k != b])
        self.gv = -self.w * v * np.log(v)
        self.Hhat = Hhat; self.grid_right = Hhat is not None

    def full(self, x):
        m = np.zeros(self.n); m[self.idx] = x; return m

    def drift(self, m):
        return self.sig - np.diff(np.concatenate([[0.0], m])) / self.Dl          # sig_k(m), k = 0..n-1

    def feasible(self, m, tol=1e-12):
        s = self.drift(m)
        return (m.min() >= -tol and np.all(np.diff(s) <= tol) and s[-1] >= -self.w - tol
                and np.all(m <= self.gv + (1 - self.v) * s + tol))

    def S(self, m, smooth=0.0):
        sl = np.diff(m) / self.Dl[1:]
        pos = np.maximum(sl, 0) if smooth == 0 else smooth * np.logaddexp(0, sl / smooth)
        return (np.sum(self.Dl[:-1] * self.Y[:-1] * pos) + np.sum(np.maximum(self.E, 0) * m)
                + self.alpha * np.sum(self.z * m))

    def Z(self, m):
        s = self.drift(m)
        if self.grid_right:
            # exact grid form of the right region (keeps the Bregman term that (B) drops): cells k > b
            k = np.arange(self.b + 1, self.n)
            return -np.sum(self.Dl[k] * (self.Hhat(s[k]) - self.Hhat(self.sig[k])))
        drop = s[:-1] - s[1:]                                                    # (B): drop at v_k, cells k, k+1
        k = np.arange(self.b, self.n - 1)
        return np.sum(self.kap_of(s[k]) * m[k] * drop[k])

    def profit(self, m, smooth=0.0):
        return self.ILp * self.S(m, smooth) - self.Z(m)


def run(ctl, da, nchain, nbelow=40, ub_=0.03, chain_only=False, verbose=True, grid_right=False):
    c = dict(ctl); c['x'] = ctl['x'] * np.exp(-da); w = c['w']
    below = np.geomspace(1e-5, ub_, nbelow)[:-1]; chain = np.geomspace(ub_, 1, nchain + 1)
    v = np.concatenate([below, chain]); b = int(np.searchsorted(v, ub_ - 1e-15))
    Q, Y, E, z, Dl, sig, Fref = reference(c, v, b)
    a0 = a_of(0, c)
    # alpha >= |a'(eta)| near 0: beta / |G0'(a(0))| (float)
    from explore1 import G0
    h = 1e-7; dG = (G0(a0 + h, c['p'], c['mu'], w, c['beta'], c['x']) - G0(a0 - h, c['p'], c['mu'], w, c['beta'], c['x'])) / (2 * h)
    alpha = c['beta'] / abs(dG)
    # V_ref and Q from DPrime (independent LP with per-eta tangents) on a fine grid
    t = np.unique(np.concatenate([np.geomspace(1e-14, 1, 6000), v])); t[-1] = 1.0
    D = DPrime(c, v, v[b], nq=6000)
    Vref, Qd = D.V(t, -w * t * np.log(t))
    qg, M0 = D.qg[D.ok0], D.M0[D.ok0]; Ht = qg * M0
    dHt = np.gradient(Ht, qg)                                      # decreasing in q
    Htp_Q = np.interp(Q, qg, dHt)
    uu = np.geomspace(1e-14, v[b], 20000); du = np.diff(np.concatenate([[0], uu]))
    ILp = np.sum(np.maximum(-w * (1 + np.log(uu)) - Htp_Q, 0) * du)
    d2 = np.abs(np.gradient(dHt, qg))
    def kap_of(y):
        qh = np.interp(-np.asarray(y), -dHt, qg)                   # qhat(y): Ht'(qhat) = y (dHt decreasing)
        k = 1.0 / np.interp(qh, qg, d2)
        return np.where(np.asarray(y) <= dHt[-1], 0.0, k)            # cap band: qhat = mu, no charge
    yg = np.linspace(-w - 0.01, sig.max() + 0.01, 40001)
    Hg = np.array([np.max(Ht - qg * y) for y in yg])
    Hhat = (lambda y: np.interp(y, yg, Hg)) if grid_right else None
    A = Adv(c, v, b, ILp, Y, E, z, alpha, Dl, sig, kap_of, chain_only, Hhat)
    if verbose:
        print('da %+.1e  chain %d below %d: Q_ref %.5f (DPrime %.5f)  V_ref %.3e  |IL\'| %.4f  Y_max %.3f  sum E+ %.3f'
              '  alpha sum z %.3f' % (da, nchain, nbelow, Q, Qd, Vref, ILp, Y.max(), np.maximum(E, 0).sum(), alpha * z.sum()))
    # search: bumps in log v, m = h * bump, clipped to feasibility by scaling h down
    best = (0.0, None)
    lv = np.log(v)
    for cen in np.linspace(np.log(v[A.idx[0]]), np.log(0.9), 25):
        for s in [0.05, 0.1, 0.2, 0.4, 0.8, 1.6, 3.2]:
            for shape in ('par', 'gau', 'tri'):
                xx = (lv - cen) / s
                if shape == 'par': bmp = np.maximum(0, 1 - xx ** 2)
                elif shape == 'gau': bmp = np.exp(-xx ** 2)
                else: bmp = np.maximum(0, 1 - np.abs(xx))
                bmp = bmp * A.gv
                m0 = np.zeros(len(v)); m0[A.idx] = bmp[A.idx]
                if m0.max() <= 0: continue
                for hh in np.geomspace(1e-4, 1, 25):
                    m = hh * m0
                    if not A.feasible(m): continue
                    pr = A.profit(m)
                    if pr > best[0]: best = (pr, m.copy())
    if verbose and best[1] is not None:
        m = best[1]; k = np.argmax(m)
        print('   bump search: sup profit %.3e at peak m %.2e (v %.4f)' % (best[0], m[k], v[k]))
    # local refinement with smoothed positive part and linear constraints (SLSQP)
    if best[1] is not None:
        x0 = best[1][A.idx]
        cons = [{'type': 'ineq', 'fun': lambda x: -np.diff(A.drift(A.full(x)))},
                {'type': 'ineq', 'fun': lambda x: A.drift(A.full(x))[-1] + w},
                {'type': 'ineq', 'fun': lambda x: (A.gv + (1 - v) * A.drift(A.full(x)) - A.full(x))[1:-1]}]
        r = minimize(lambda x: -A.profit(A.full(x), smooth=1e-4), x0, method='SLSQP', bounds=[(0, None)] * len(x0),
                     constraints=cons, options=dict(maxiter=300, ftol=1e-12))
        m = A.full(np.maximum(r.x, 0))
        if A.feasible(m, tol=1e-9) and A.profit(m) > best[0]:
            best = (A.profit(m), m)
        if verbose:
            m = best[1]; k = np.argmax(m)
            print('   refined:     sup profit %.3e at peak m %.2e (v %.4f); S %.3e, Z %.3e'
                  % (best[0], m[k], v[k], A.S(m), A.Z(m)))
    if best[1] is not None:
        m = best[1]
        Vt, Qt = D.V(v, -w * v * np.log(v) - m)
        V0, Q0 = D.V(v, -w * v * np.log(v))
        print('   true (exact chain LP, grid drift) at that m: V %.3e vs saturated on the same grid %.3e; Q %.5f vs %.5f'
              % (Vt, V0, Qt, Q0))
    return Vref, best[0]


if __name__ == '__main__':
    import json
    from fractions import Fraction as Fr
    ctl = {k: float(Fr(s)) for k, s in json.load(open(sys.argv[1])).items()}
    nchain = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    for da in [-4e-4, -1.2e-3]:
        for gr in (False, True):
            print('right region by (B)' if not gr else 'right region exact on the grid')
            Vref, loss = run(ctl, da, nchain, chain_only=True, grid_right=gr)
            print('   => V_ref + loss = %.3e  (%s)' % (Vref + loss, 'KEEPS' if Vref + loss < 0 else 'fails'))
