"""Float gate (exploration; proves nothing) for a MULTI-CUT robust bound of Lemma D' at the saturated box.

Chain LP at a deficit vector m (grid relaxation of Lemma DL (a); B1's fix: supporting planes of the jointly concave
K(g, eta) = g M_eta(g) + w g - g eta, valid on the whole domain; F_i >= (a0 - alpha eta_i) v_i; F_i <= mu v_i):
  min F_n  s.t.  sum_{k<=i} DF_k s_{k+1}(m) + F_i (w (1 + log v_i) - Kg_r) <= v_i (K0_r - Kg_r g0_r - Ke_r e0_r) + Ke_r v_i eta_i,
                 0 <= DF_k <= Delta_k   (kept inside),   eta_i in [0, m_i / v_i]   (adversary's gap).
CUT j: the partial Lagrangian with the optimal duals of the LP at a reference deficit m^(j), minimised over the DF box
and over the gaps, is a valid lower bound of Q_min(m) for EVERY m (exact at m^(j)):
  cut_j(m) = C_j - sum_i m_i (E_ij + alpha z_ij)_+ + sum_k Delta_k min(0, 1 + Y_kj s_{k+1}(m) + W_kj).
Bound: V(m) <= Vb(m) := IL(max_j cut_j(m)) + sum_{right cells} Delta_k Hhat(s_k(m))  (right region exact on the grid,
Bregman term kept; left drift saturated). Gate: sup_m Vb(m) < 0, searched (bump families + Nelder-Mead on log-knots),
with cuts added at the searched maximiser (cutting-plane loop) and at the true adversary's worst deficits."""
import sys
import numpy as np
from scipy.optimize import linprog, minimize
from scipy.sparse import coo_matrix

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from explore1 import parts, a_of, G0   # noqa: E402
from dprime_float import DPrime         # noqa: E402
from dl_robust_float import planes      # noqa: E402


class Gate:
    def __init__(self, c, nchain, nbelow=40, ub=0.03, nq=6000):
        self.c = c; w = self.w = c['w']; self.mu = c['mu']
        below = np.geomspace(1e-5, ub, nbelow)[:-1]; chain = np.geomspace(ub, 1, nchain + 1)
        v = self.v = np.concatenate([below, chain]); n = self.n = len(v)
        b = self.b = int(np.searchsorted(v, ub - 1e-15))
        self.Dl = np.diff(np.concatenate([[0.0], v]))
        self.gv = -w * v * np.log(v)
        self.sig = np.diff(np.concatenate([[0.0], self.gv])) / self.Dl
        self.a0 = a_of(0, c)
        h = 1e-7; dG = (G0(self.a0 + h, c['p'], c['mu'], w, c['beta'], c['x'])
                        - G0(self.a0 - h, c['p'], c['mu'], w, c['beta'], c['x'])) / (2 * h)
        self.alpha = c['beta'] / abs(dG)
        self.P = planes(c, self.a0, self.mu)
        self.D = DPrime(c, v, v[b], nq=nq)
        qg, M0 = self.D.qg[self.D.ok0], self.D.M0[self.D.ok0]; Ht = qg * M0
        self.qg = qg
        # left region: IL(Q) = sum_{k<=b} Delta_k max_{q >= Q} (Ht(q) - q sig_k), as suffix maxima on the q grid
        IL = np.zeros(len(qg))
        for k in range(b + 1):
            IL += self.Dl[k] * np.maximum.accumulate((Ht - qg * self.sig[k])[::-1])[::-1]
        self.ILarr = IL
        yg = self.yg = np.linspace(-w - 0.05, self.sig[b + 1:].max() + 0.05, 30001)
        self.Hg = np.array([np.max(Ht - qg * y) for y in yg])
        self.idx = np.arange(b + 1, n - 1)            # free deficits (m_b = m_end = 0)
        self.cuts = []

    # ---- deficit -> drift
    def drift(self, m):
        return self.sig - np.diff(np.concatenate([[0.0], m])) / self.Dl

    def snext(self, m):
        s = self.drift(m); return np.concatenate([s[1:], [-self.w]])

    def feasible(self, m, tol=1e-12):
        s = self.drift(m)
        return m.min() >= -tol and np.all(np.diff(s) <= tol) and s[-1] >= -self.w - tol

    # ---- LP at m and its cut
    def lp(self, m):
        c, w, mu, v, n, b, Dl = self.c, self.w, self.mu, self.v, self.n, self.b, self.Dl
        sn = self.snext(m); eta = m / v
        rows, cols, vals, rhs, tags = [], [], [], [], []; r = 0
        def add(cs, vs, rh, tag):
            nonlocal r
            rows.extend([r] * len(cs)); cols.extend(cs); vals.extend(vs); rhs.append(rh); tags.append(tag); r += 1
        lb = np.zeros(n); ub = np.array(v, dtype=float); ub[0] = Dl[0]
        for k in range(1, n):
            add([k - 1, k], [1, -1], 0.0, None); add([k, k - 1], [1, -1], Dl[k], None)
        for i in range(b + 1, n):
            ub[i] = min(ub[i], mu * v[i])
            add([i], [-1.0], -(self.a0 * v[i] - self.alpha * m[i]), ('low', i))
            base = {}
            for k in range(0, i + 1):
                base[k] = base.get(k, 0.0) + sn[k]
                if k > 0: base[k - 1] = base.get(k - 1, 0.0) - sn[k]
            for (K0, Kg, Ke, g0, e0) in self.P:
                coef = dict(base); coef[i] = coef.get(i, 0.0) + w * (1 + np.log(v[i])) - Kg
                add(list(coef.keys()), list(coef.values()), v[i] * (K0 - Kg * g0 - Ke * e0) + Ke * v[i] * eta[i],
                    ('pl', i, Ke, w * (1 + np.log(v[i])) - Kg, v[i] * (K0 - Kg * g0 - Ke * e0)))
        A = coo_matrix((vals, (rows, cols)), shape=(r, n)).tocsr()
        cv = np.zeros(n); cv[-1] = 1.0
        res = linprog(cv, A_ub=A, b_ub=np.array(rhs), bounds=list(zip(lb, ub)), method='highs')
        assert res.status == 0, res.message
        y = -res.ineqlin.marginals; uu = -res.upper.marginals; ll = res.lower.marginals
        Yi = np.zeros(n); Wi = np.zeros(n); E = np.zeros(n); z = np.zeros(n); C = 0.0
        for yy, tg in zip(y, tags):
            if tg is None or yy <= 0: continue
            if tg[0] == 'pl':
                _, i, Ke, cF, r0 = tg
                Yi[i] += yy; Wi[i] += yy * cF; E[i] += yy * Ke; C -= yy * r0
            else:
                z[tg[1]] += yy; Wi[tg[1]] -= yy; C += yy * self.a0 * v[tg[1]]
        Wi += uu - ll; C -= np.sum(uu * ub) - np.sum(ll * lb)
        Y = np.cumsum(Yi[::-1])[::-1]; W = np.cumsum(Wi[::-1])[::-1]
        cut = dict(C=C, Y=Y, W=W, gr=E + self.alpha * z, gm=np.maximum(E + self.alpha * z, 0), m=m.copy(), Q=res.fun)
        return res.fun, cut

    def cutval(self, cut, m):
        ck = 1.0 + cut['Y'] * self.snext(m) + cut['W']
        return cut['C'] - np.sum(cut['gm'] * m) + np.sum(self.Dl * np.minimum(0.0, ck))

    def add_cut(self, m):
        Q, cut = self.lp(m)
        chk = self.cutval(cut, m)
        self.cuts.append(cut)
        return Q, chk

    # ---- values
    def IL(self, Q):
        j = min(np.searchsorted(self.qg, Q, 'left'), len(self.qg) - 1)
        return self.ILarr[j]

    def R(self, m):
        s = self.drift(m)[self.b + 1:]
        return np.sum(self.Dl[self.b + 1:] * np.interp(s, self.yg, self.Hg))

    def Qb(self, m):
        return max(self.cutval(ct, m) for ct in self.cuts)

    def Vb(self, m):
        return self.IL(self.Qb(m)) + self.R(m)

    def Vtrue(self, m):
        return self.D.V(self.v, self.gv - m)[0]

    # ---- adversary search over m (maximise f)
    def search(self, f, starts=None, nm_iter=400, knots=12, seed=0, refine=0):
        v, lv = self.v, np.log(self.v); best = (-np.inf, None)
        cand = [] if starts is None else list(starts)
        for cen in np.linspace(np.log(v[self.b + 1]), np.log(0.9), 18):
            for s in [0.1, 0.25, 0.5, 1.0, 2.0, 4.0]:
                xx = (lv - cen) / s
                for bmp in (np.maximum(0, 1 - xx ** 2), np.exp(-xx ** 2)):
                    m0 = np.zeros(self.n); m0[self.idx] = (bmp * self.gv)[self.idx]
                    if m0.max() <= 0: continue
                    for hh in np.geomspace(3e-4, 0.5, 18):
                        m = m0 * (hh * 0.168 / m0.max())
                        if self.feasible(m): cand.append(m)
        vals = [(f(m), i) for i, m in enumerate(cand)]
        vals.sort(reverse=True)
        best = (vals[0][0], cand[vals[0][1]])
        kn = np.linspace(np.log(v[self.b]), 0.0, knots + 2)
        def from_knots(x):
            m = np.zeros(self.n); m[self.b:] = np.interp(lv[self.b:], kn, np.concatenate([[0], np.abs(x), [0]]))
            m[self.b] = 0; m[-1] = 0; return m
        for _, i in vals[:4]:
            x0 = np.interp(kn[1:-1], lv[self.b:], cand[i][self.b:])
            def obj(x):
                m = from_knots(x)
                return 1.0 if not self.feasible(m) else -f(m)
            r = minimize(obj, x0, method='Nelder-Mead', options=dict(maxiter=nm_iter, xatol=1e-7, fatol=1e-9))
            m = from_knots(r.x)
            if self.feasible(m) and f(m) > best[0]: best = (f(m), m)
        if refine:
            # full-dimensional random local search (single coordinates, pairs and smooth bumps), feasibility kept
            rng = np.random.default_rng(seed); fb, mb = best; lvb = lv
            for it in range(refine):
                d = np.zeros(self.n); kind = it % 3
                if kind == 0:
                    d[rng.choice(self.idx)] = rng.normal() * max(mb.max(), 1e-4) * 0.05
                elif kind == 1:
                    k = rng.choice(self.idx[:-1]); a = rng.normal() * max(mb.max(), 1e-4) * 0.05
                    d[k] = a; d[k + 1] = -a
                else:
                    cen = rng.uniform(lvb[self.b + 1], 0); s = 10 ** rng.uniform(-1.3, 0.5)
                    d[self.idx] = (np.exp(-((lvb - cen) / s) ** 2) * self.gv)[self.idx] * rng.normal() * 0.1 * max(mb.max(), 1e-4) / 0.168
                m = np.maximum(mb + d, 0); m[self.b] = 0; m[-1] = 0
                if self.feasible(m):
                    fm = f(m)
                    if fm > fb: fb, mb = fm, m
            best = (fb, mb)
        return best


def run(ctl, da, nchain, kmax=12, seed_true=True, log=print, refine=6000):
    c = dict(ctl); c['x'] = ctl['x'] * np.exp(da)
    G = Gate(c, nchain)
    m0 = np.zeros(G.n)
    Q0, chk = G.add_cut(m0)
    V0 = G.Vtrue(m0)
    log('da %.1e chain %d: saturated V %.3e (grid), Q_ref %.5f (cut check %.5f, DPrime %.5f)'
        % (da, nchain, V0, Q0, chk, G.D.qmin(G.gv)))
    if seed_true:
        vt, mt = G.search(G.Vtrue, nm_iter=150)
        log('   true adversary: sup V %.3e at peak m %.2e (v %.3f)' % (vt, mt.max(), G.v[np.argmax(mt)]))
        G.add_cut(mt)
    hist = []
    for K in range(len(G.cuts), kmax + 1):
        vb, mb = G.search(G.Vb, refine=refine, seed=K)
        hist.append((len(G.cuts), vb))
        log('   %2d cuts: sup Vb %.3e at peak m %.2e (v %.3f); true V there %.3e'
            % (len(G.cuts), vb, mb.max(), G.v[np.argmax(mb)], G.Vtrue(mb)))
        if K < kmax: G.add_cut(mb)
    return V0, hist


if __name__ == '__main__':
    import json
    from fractions import Fraction as Fr
    ctl = {k: float(Fr(s)) for k, s in json.load(open(sys.argv[1])).items()}
    nchain = int(sys.argv[2]); das = [float(s) for s in sys.argv[3].split(',')]
    kmax = int(sys.argv[4]) if len(sys.argv) > 4 else 12
    refine = int(sys.argv[5]) if len(sys.argv) > 5 else 6000
    for da in das:
        run(ctl, da, nchain, kmax, log=lambda s: print(s, flush=True), refine=refine)
