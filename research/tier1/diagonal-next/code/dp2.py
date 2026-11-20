"""dp2.py -- REALISABLE float model of the ZBS / Lu-Wang bank fixed point (exploration only; proves nothing).

Differences from dp.py (pointwise model, which interpolates a concave optimum and so drifts downward without bound):
  * log-uniform ratio grid symmetric under r -> 1/r on [1/smax, smax], extended down to smin;
  * every profile cell [s_{i-1}, s_i] is realised by ONE leaf or ONE route (theta <= s_{i-1}) with ONE terminal source
    line (a', B*(a')); the cell's requirement is checked at both ends (exact: on a cell the realisation is the max of
    two affine functions, hence convex); knot value = max of the two adjacent cells' requirements;
  * the closed profile U is realised cell by cell by ONE complementary pair (on a symmetric log grid, r L(1/r) is affine
    on each cell, so max(L_j, r L_j'(1/r)) is convex there and the knots bound it);
  * the root is a point (as in the certificates: a tiny domain around 1): z = best value at (1/2, 1).
Sources: F = min(fhat, U) on the grid points of [1/smax, smax] (exact for PL U), fhat on a fine grid elsewhere.
"""
import numpy as np
from dp import LWf, es_hat, load_table


class Model2:
    def __init__(self, PP, MU, W, a, fhat, dl=0.01, smax=5.0, smin=0.01, nG=200, Agrid=(0.25, 12.0, 2e-4),
                 routes=True, feedback=True):
        self.PP = np.asarray(PP, float); self.MU = np.asarray(MU, float); self.W = np.asarray(W, float)
        a = np.where(np.isfinite(a), a, np.inf)
        self.a = np.minimum.accumulate(a, axis=0)
        self.b = -np.log(self.MU) + 1e-9
        self.fhat = fhat
        n2 = int(round(np.log(smax) / dl)); dl = np.log(smax) / n2
        n1 = int(np.ceil(np.log(1 / smin) / dl))
        self.S = np.exp(dl * np.arange(-n1, n2 + 1))
        self.nS = len(self.S); self.nP = len(self.PP); self.nG = nG
        self.i1 = n1                                             # S[i1] = 1
        self.sym_lo = n1 - n2                                     # S[sym_lo] = 1/smax
        self.d = np.concatenate([[1e-6], -np.log1p(-self.PP)]) + 1e-9
        self.Ag = np.arange(*Agrid)
        self.routes, self.feedback = routes, feedback
        lam_out = np.exp(np.concatenate([np.linspace(np.log(1e-4), np.log(self.S[self.sym_lo]), 3000),
                                         np.linspace(np.log(smax), np.log(1e4), 3000)]))
        self.lam_out = lam_out; self.F_out = fhat(lam_out)
        self.fS = fhat(self.S)
        self.L = np.full((self.nP, self.nS), np.inf)
        self.U = np.full(self.nS, np.inf)
        self.jh = int(np.argmin(abs(self.PP - 0.5)))
        self.jp = np.array([int(np.searchsorted(self.PP, 1 - p + 1e-12)) - 1 for p in self.PP])
        self.zhist = []

    # ---------------------------------------------------------------- closed profile U (pairs, cell by cell)
    def comp_U(self, Lpm):
        lo, i1, S = self.sym_lo, self.i1, self.S
        n2 = self.nS - 1 - i1
        idx = np.arange(lo, self.nS)                             # grid points with 1/S also on the grid
        rec = 2 * i1 - idx                                       # S[rec] = 1/S[idx]
        best = np.full(len(idx) - 1, np.inf); req = np.full((2, len(idx) - 1), np.inf)
        for j in range(self.nP):
            jp = self.jp[j]
            if jp < 0: continue
            g = np.maximum(Lpm[j, idx], S[idx] * Lpm[jp, rec])
            c0, c1 = g[:-1], g[1:]
            m = np.maximum(c0, c1)
            bt = m < best
            best = np.where(bt, m, best); req[0] = np.where(bt, c0, req[0]); req[1] = np.where(bt, c1, req[1])
        U = np.full(self.nS, np.inf)
        k = np.full(len(idx), -np.inf)
        k[:-1] = np.maximum(k[:-1], req[0]); k[1:] = np.maximum(k[1:], req[1])
        U[idx] = np.where(np.isfinite(k), k, np.inf)
        return U

    # ---------------------------------------------------------------- sources
    def sources(self):
        lam = np.concatenate([self.lam_out, self.S[self.sym_lo:]])
        F = np.concatenate([self.F_out, np.minimum(self.fS[self.sym_lo:], self.U[self.sym_lo:]) if self.feedback
                            else self.fS[self.sym_lo:]])
        B = np.empty(len(self.Ag))
        for s0 in range(0, len(self.Ag), 400):
            A = self.Ag[s0:s0 + 400]
            B[s0:s0 + 400] = np.max((F[None, :] - A[:, None]) / lam[None, :], axis=1)
        self.Bst = B
        V = self.Ag[None, :] + self.S[:, None] * B[None, :]                  # (nS, nA)
        rev = V[:, ::-1]
        am = np.minimum.accumulate(rev, axis=1)
        # index of the suffix minimiser (for the cell's fixed line)
        nA = len(self.Ag)
        pos = np.where(rev == am, np.arange(nA)[None, :], -1)
        pos = np.maximum.accumulate(pos, axis=1)                             # last index (in reversed order) attaining
        self.Lam = am[:, ::-1]
        self.Larg = (nA - 1 - pos)[:, ::-1]                                  # minimiser index a' >= a

    # ---------------------------------------------------------------- descent
    def descent(self, Lb, Gt):
        """returns g1 (nS, nG): path value at S[e-1] (nan if no child fits on the first step), and
        Mr (nS, nG, nMU) = max over theta <= S[e-1] of psi(theta) - theta b (-inf if dead)."""
        nB = Lb.shape[0]; S = self.S
        E = np.full((nB, self.nS), np.inf)
        dS = np.diff(S)
        E[:, 1:] = np.maximum(Lb[:, 1:], Lb[:, :-1] + dS[None, :] * self.d[:, None])
        m = np.minimum.accumulate(E, axis=0)
        g = Gt.copy(); alive = np.ones(g.shape, bool)
        Mr = np.full(g.shape + (len(self.b),), -np.inf)
        g1 = np.full(g.shape, np.nan)
        ee = np.arange(self.nS)
        for k in range(self.nS - 1):
            i = ee - k
            act = i >= 1
            if not act.any(): break
            idx = np.where(act, i, 1)
            mm = m[:, idx]
            cnt = (mm[:, :, None] >= g[None, :, :] - 1e-12).sum(axis=0)
            ok = act[:, None] & alive & (cnt < nB)
            if not ok.any(): break
            jj = np.minimum(cnt, nB - 1)
            g = np.where(ok, g - dS[idx - 1][:, None] * self.d[jj], g)
            alive = ok
            if k == 0: g1 = np.where(ok, g, np.nan)
            upd = g[:, :, None] - S[idx - 1][:, None, None] * self.b[None, None, :]
            Mr = np.where(ok[:, :, None], np.maximum(Mr, upd), Mr)
        return g1, Mr

    # ---------------------------------------------------------------- one round
    def round(self):
        S = self.S; nP, nMU, nW, nS = self.nP, len(self.MU), len(self.W), self.nS
        Lpm = np.minimum.accumulate(self.L, axis=0)
        self.U = np.minimum(self.U, self.comp_U(Lpm))
        self.sources()
        W = self.W
        a = self.a                                                            # (nP, nMU, nW)
        ia = np.clip(np.searchsorted(self.Ag, a), 0, len(self.Ag) - 1)
        ia = np.where(np.isfinite(a) & (a <= self.Ag[-1]), ia, -1)
        # candidates per end index e (cell [e-1, e]); store right/left values of the best candidates
        VR = np.full((nP, nS), np.inf); VL = np.full((nP, nS), np.inf)       # chosen realisation of cell ending at e
        PT = np.full((nP, nS), np.inf)                                         # point optimum at S[e]
        if self.routes:
            Lb = np.vstack([self.U[None, :], Lpm])
            cur = np.min(np.vstack([Lpm, self.U[None, :], self.fS[None, :]]), axis=0)
            lo = np.maximum(cur - 0.5, 0.005); hi = self.fS + 0.02
            Gt = lo[:, None] + (hi - lo)[:, None] * np.linspace(0, 1, self.nG)[None, :]
            g1, Mr = self.descent(Lb, Gt)
        for e in range(1, nS):
            r, rl = S[e], S[e - 1]
            iaa = np.where(ia >= 0, self.Larg[e][np.maximum(ia, 0)], -1)    # a'' per (j, mu, w)
            ap = np.where(ia >= 0, self.Ag[np.maximum(iaa, 0)], np.inf)
            Bp = np.where(ia >= 0, self.Bst[np.maximum(iaa, 0)], np.inf)
            Cr = ap + r * Bp; Cl = ap + rl * Bp                               # (nP, nMU, nW)
            wb = W[None, None, :] * self.b[None, :, None]
            leafR = (Cr + r * wb) / (1 + W); leafL = (Cl + rl * wb) / (1 + W)
            candR = [leafR.reshape(nP, -1)]; candL = [leafL.reshape(nP, -1)]
            if self.routes:
                Gs = Gt[e]; gl = g1[e]
                okG = np.isfinite(gl)
                if okG.sum() >= 2:
                    Gs2, gl2 = Gs[okG], gl[okG]
                    RR = np.full((nP, nMU, nW), np.inf); LL = np.full((nP, nMU, nW), np.inf)
                    for im in range(nMU):
                        Mm = Mr[e, okG, im]
                        fin = np.isfinite(Mm)
                        if fin.sum() < 2: continue
                        G3, M3, g3 = Gs2[fin], Mm[fin], gl2[fin]
                        for iw in range(nW):
                            w = W[iw]
                            Phr = G3 + w * M3
                            Phi = np.maximum.accumulate(Phr)
                            tgt = Cr[:, im, iw]; tl = Cl[:, im, iw]
                            okv = np.isfinite(tgt) & (tgt >= Phr[0])
                            # (1) largest grid start k0 with Phi <= tgt, its path shifted up by delta (still valid:
                            #     children stay below a raised path); (2) the next start k0 + 1 unshifted.
                            k0 = np.clip(np.searchsorted(Phi, tgt, side='right') - 1, 0, len(G3) - 1)
                            k0 = np.where(Phr[k0] <= tgt, k0, 0)
                            dlt = np.maximum((tgt - Phr[k0]) / (1 + w), 0)
                            vr0 = G3[k0] + dlt
                            vl0 = np.maximum(g3[k0] + dlt, (tl + w * (g3[k0] - M3[k0])) / (1 + w))
                            k1 = np.minimum(k0 + 1, len(G3) - 1)
                            vr1 = np.maximum(G3[k1], (tgt + w * (G3[k1] - M3[k1])) / (1 + w))
                            vl1 = np.maximum(g3[k1], (tl + w * (g3[k1] - M3[k1])) / (1 + w))
                            use1 = vr1 < vr0
                            vr = np.where(use1, vr1, vr0); vl = np.where(use1, vl1, vl0)
                            RR[:, im, iw] = np.where(okv, vr, np.inf); LL[:, im, iw] = np.where(okv, vl, np.inf)
                    candR.append(RR.reshape(nP, -1)); candL.append(LL.reshape(nP, -1))
            CR = np.concatenate(candR, axis=1); CL = np.concatenate(candL, axis=1)
            CR = np.where(np.isfinite(CR), CR, np.inf); CL = np.where(np.isfinite(CL), CL, np.inf)
            ptR = CR.min(axis=1); ptL = CL.min(axis=1)
            PT[:, e] = ptR
            with np.errstate(invalid='ignore'):
                reg = np.maximum(CR - ptR[:, None], CL - ptL[:, None])
            reg = np.where(np.isfinite(reg), reg, np.inf)
            kb = np.argmin(reg, axis=1)
            VR[:, e] = CR[np.arange(nP), kb]; VL[:, e] = CL[np.arange(nP), kb]
        knot = np.full((nP, nS), -np.inf)
        knot[:, 1:] = np.maximum(knot[:, 1:], VR[:, 1:])
        knot[:, :-1] = np.maximum(knot[:, :-1], VL[:, 1:])
        knot = np.where(np.isfinite(knot), knot, np.inf)
        self.L = np.minimum(self.L, knot)
        self.PT = PT
        Lpm = np.minimum.accumulate(self.L, axis=0)
        self.U = np.minimum(self.U, self.comp_U(Lpm))
        z = float(min(PT[self.jh, self.i1], Lpm[self.jh, self.i1]))
        self.zhist.append(z)
        return z

    def run(self, rounds, tol=2e-7, log=None):
        for r in range(rounds):
            z = self.round()
            if log: log('round %d  z = %.7f  e^z = %.5f  knot L_1/2(1) = %.7f' % (
                r, z, np.exp(z), np.minimum.accumulate(self.L, axis=0)[self.jh, self.i1]))
            h = self.zhist
            if len(h) > 3 and abs(h[-3] - h[-1]) < tol: break
        return self.zhist
