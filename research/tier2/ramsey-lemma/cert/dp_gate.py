"""Float gate (exploration; proves nothing numerically, but its sup is EXACT over all grid deficits, not searched).

For each cut j of cutq_float (a valid lower bound of Q_min(m) for every m) and the tangent of the concave IL at
Q_j*, f_j(m) := IL(Q_j*) + |IL'(Q_j*)| (Q_j* - cut_j(m)) + R(m) >= V(m) whenever cut_j is the best cut, and in fact
V(m) <= min_j f_j(m) <= sum_j lambda_j f_j(m) for every lambda in the simplex. In the drift variables s_k (right cells)
every f_j is a SEPARABLE CONVEX function sum_k psi_jk(s_k) + const (Hhat convex; the cut's min(0, affine) enters
with a minus sign; m is affine in s). A convex function on the polytope {s nonincreasing, Phi <= g, Phi(u_b) = g(u_b),
Phi(1) = 0} attains its max at a vertex, and the vertices are the CHORD PROFILES: Phi = chord of g between consecutive
touching points u_b = t_0 < t_1 < ... < t_B = 1 (grid points). So sup_m sum_j lambda_j f_j(m) is a longest-path
dynamic programme over touching points (O(n^3)), exact. lambda is optimised by an LP over the vertices found
(min-max cutting planes), and new Q-cuts are added at the maximising vertex.
Gate: min_lambda sup_m sum lambda_j f_j < 0 (a certificate of this form would be rigorous up to mesh terms)."""
import sys
import numpy as np
from scipy.optimize import linprog

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from cutq_float import Gate   # noqa: E402


class DPGate:
    def __init__(self, G):
        self.G = G; b, n = G.b, G.n
        self.pts = np.arange(b, n)                     # touching-point candidates (grid points v_b .. v_{n-1} = 1)
        self.cells = np.arange(b + 1, n)               # right cells
        self.fs = []                                   # list of (const, Dl*Gamma, Dl_prev, Y_prev, W_prev, ILp)
        dqg = np.gradient(G.ILarr, G.qg); self.dIL = dqg

    def ILtan(self, Q):
        j = min(np.searchsorted(self.G.qg, Q), len(self.G.qg) - 1)
        return self.G.ILarr[j], abs(self.dIL[j])

    def add_f(self, cut, Qstar=None):
        G = self.G; b, n, Dl = G.b, G.n, G.Dl
        Qs = cut['Q'] if Qstar is None else Qstar
        IL0, ILp = self.ILtan(Qs)
        gm = cut['gm']; Gam = np.cumsum(gm[::-1])[::-1]
        Y, W = cut['Y'], cut['W']
        sfix = G.sig                                    # left drift saturated
        const_cut = cut['C'] - np.sum(gm * (G.gv - G.gv[b]) * (np.arange(n) > b))
        const_cut += np.sum(Dl[:b] * np.minimum(0.0, 1 + Y[:b] * sfix[1:b + 1] + W[:b]))
        const_cut += Dl[n - 1] * min(0.0, 1 - G.w * Y[n - 1] + W[n - 1])
        j = self.cells
        f = dict(const=IL0 + ILp * Qs - ILp * const_cut, ILp=ILp, aG=Dl[j] * Gam[j],
                 dprev=Dl[j - 1], Yp=Y[j - 1], Wp=W[j - 1])
        self.fs.append(f)

    def psi(self, f, jj, s):
        """per-cell term (cells index jj into self.cells) at drift s (arrays broadcast)."""
        G = self.G; Dl = G.Dl[self.cells[jj]]
        H = np.interp(s, G.yg, G.Hg)
        return (Dl * H - f['ILp'] * f['aG'][jj] * s
                - f['ILp'] * f['dprev'][jj] * np.minimum(0.0, 1 + f['Yp'][jj] * s + f['Wp'][jj]))

    def fval_m(self, f, m):
        """direct evaluation of f at a deficit vector m (for checking the separable form)."""
        s = self.G.drift(m)[self.cells]
        return f['const'] + np.sum(self.psi(f, np.arange(len(self.cells)), s))

    def dp(self, lam):
        """max over chord profiles of sum_j lam_j f_j; returns value, touching points, per-f values."""
        G = self.G; v, gv = G.v, G.gv; P = self.pts; npt = len(P)
        best = np.full(npt, -np.inf); arg = np.zeros(npt, dtype=int); best[0] = 0.0
        act = [(l, f) for l, f in zip(lam, self.fs) if l > 1e-12]
        for qi in range(1, npt):
            q = P[qi]
            pi = np.arange(qi)
            s = (gv[q] - gv[P[pi]]) / (v[q] - v[P[pi]])          # chord slope for each start p
            # cells in (p, q]: cell indices jj from pi .. qi-1 (cell P[k]+1 has jj = k)
            tot = np.zeros(qi)
            for k in range(qi):                                  # cell jj = k belongs to blocks with p <= k
                sv = s[:k + 1]
                val = np.zeros(k + 1)
                for l, f in act:
                    val += l * self.psi(f, k, sv)
                tot[:k + 1] += val
            cand = best[:qi] + tot
            arg[qi] = int(np.argmax(cand)); best[qi] = cand[arg[qi]]
        # backtrack
        T = [npt - 1]
        while T[-1] != 0: T.append(arg[T[-1]])
        T = [P[t] for t in T[::-1]]
        m = self.m_of(T)
        vals = np.array([self.fval_m(f, m) for f in self.fs])
        return best[-1] + sum(l * f['const'] for l, f in act), T, m, vals

    def m_of(self, T):
        G = self.G; Phi = G.gv.copy()
        for p, q in zip(T[:-1], T[1:]):
            Phi[p:q + 1] = np.interp(G.v[p:q + 1], [G.v[p], G.v[q]], [G.gv[p], G.gv[q]])
        return G.gv - Phi

    def minimax(self, iters=40, log=print):
        """min over lambda of max over chord profiles: LP cutting planes on the vertices found."""
        J = len(self.fs); V = []
        lam = np.full(J, 1.0 / J)
        for it in range(iters):
            val, T, m, vals = self.dp(lam)
            V.append(vals)
            # LP: min t s.t. t >= vals_r . lam for all r, lam in simplex
            A = np.array([np.concatenate([vr, [-1.0]]) for vr in V])
            res = linprog(np.concatenate([np.zeros(J), [1.0]]), A_ub=A, b_ub=np.zeros(len(V)),
                          A_eq=np.concatenate([np.ones(J), [0.0]])[None, :], b_eq=[1.0],
                          bounds=[(0, None)] * J + [(None, None)], method='highs')
            lam_new, lower = res.x[:J], res.x[J]
            if val - lower < 1e-9: break
            lam = lam_new
        return val, lam, T, m


def averaged(cuts, lam):
    """the cut of the averaged multipliers y = sum lam_j y_j (C, Y, W linear in y; the gap term's positive part taken
    after averaging, which is larger than the average of the cuts: Jensen, the dual function is concave in y)."""
    out = dict(C=sum(l * c['C'] for l, c in zip(lam, cuts)), Y=sum(l * c['Y'] for l, c in zip(lam, cuts)),
               W=sum(l * c['W'] for l, c in zip(lam, cuts)), Q=sum(l * c['Q'] for l, c in zip(lam, cuts)))
    out['gm'] = np.maximum(sum(l * c['gr'] for l, c in zip(lam, cuts)), 0)
    return out


def avg_minimax(G, D, iters=150, log=print):
    """min over lam of the exact DP max of f(.; averaged multipliers); lam = softmax(x), Nelder-Mead."""
    from scipy.optimize import minimize
    J = len(G.cuts); memo = {}
    def F(x):
        lam = np.exp(x - x.max()); lam /= lam.sum()
        D.fs = []; D.add_f(averaged(G.cuts, lam))
        val, T, m, _ = D.dp(np.array([1.0]))
        memo[val] = (lam, T, m)
        return val
    x0 = np.zeros(J)
    r = minimize(F, x0, method='Nelder-Mead', options=dict(maxiter=iters, xatol=1e-3, fatol=1e-7))
    val = min(memo); lam, T, m = memo[val]
    return val, lam, T, m


if __name__ == '__main__' and len(sys.argv) > 5 and sys.argv[5] == 'avg':
    import json
    from fractions import Fraction as Fr
    ctl = {k: float(Fr(s)) for k, s in json.load(open(sys.argv[1])).items()}
    nchain = int(sys.argv[2]); das = [float(s) for s in sys.argv[3].split(',')]
    ncut = int(sys.argv[4])
    for da in das:
        c = dict(ctl); c['x'] = ctl['x'] * np.exp(da)
        G = Gate(c, nchain); D = DPGate(G)
        m0 = np.zeros(G.n); G.add_cut(m0)
        print('da %.1e chain %d (averaged multipliers): saturated V %.3e' % (da, nchain, G.Vtrue(m0)), flush=True)
        for k in range(ncut):
            val, lam, T, m = avg_minimax(G, D)
            print('   %2d reference duals: min_lam exact max = %.3e at %d touching points (peak m %.2e at v %.3f); '
                  'true V %.3e; lam support %d' % (len(G.cuts), val, len(T), m.max(), G.v[np.argmax(m)], G.Vtrue(m),
                                                   int((lam > 1e-3).sum())), flush=True)
            if val < 0 and k >= 2: break
            G.add_cut(m)
    sys.exit(0)


if __name__ == '__main__':
    import json
    from fractions import Fraction as Fr
    ctl = {k: float(Fr(s)) for k, s in json.load(open(sys.argv[1])).items()}
    nchain = int(sys.argv[2]); das = [float(s) for s in sys.argv[3].split(',')]
    ncut = int(sys.argv[4]) if len(sys.argv) > 4 else 12
    for da in das:
        c = dict(ctl); c['x'] = ctl['x'] * np.exp(da)
        G = Gate(c, nchain); D = DPGate(G)
        m0 = np.zeros(G.n); Q0, _ = G.add_cut(m0); D.add_f(G.cuts[-1])
        print('da %.1e chain %d: saturated V %.3e  f_0(0) %.3e (Vb(0) %.3e)' % (da, nchain, G.Vtrue(m0),
              D.fval_m(D.fs[0], m0), G.Vb(m0)), flush=True)
        for k in range(ncut):
            val, lam, T, m = D.minimax()
            print('   %2d cuts: min_lambda max_vertex = %.3e at %d touching points (peak m %.2e at v %.3f); true V %.3e; '
                  'lambda support %d' % (len(G.cuts), val, len(T), m.max(), G.v[np.argmax(m)], G.Vtrue(m),
                                         int((lam > 1e-9).sum())), flush=True)
            if val < 0 and k >= 2: break
            Qn, chk = G.add_cut(m); D.add_f(G.cuts[-1])
