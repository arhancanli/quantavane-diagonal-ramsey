"""Float model of the joint fixed point of the ZBS bank construction (exploration only; proves nothing).

State: profile heights L[j, i] at density P[j] (= j/80 - 1e-6) and ratio S[i] (uniform grid), nonincreasing in j.
One round:
  1. Sources: F_src(lam) = min(fhat(lam), U(lam)), U(lam) = min_j max(L_j(lam), lam L_{j'}(1/lam)), P_j + P_j' <= 1.
     B*(a) = sup_lam (F_src(lam) - a)/lam  (best source line with intercept a).
  2. Routes (ZBS Def. 5.4 / Lemma 5.8): end point (rho, G); backward greedy descent g with the lowest density child
     whose profile lies below g on the step; slope d = -log(1 - p_child) (+ tiny). For control (a, b, w, c) the route
     height at rho is the least G with  G + w * max_theta (g_G(theta) - theta c) >= a + rho b, theta in path (theta =
     rho is the leaf).
  3. New L = min(old L, route values), made nonincreasing in j (density copy) and capped by U (complementary pairs).
Control table: a(p, mu, w) = -log x_max (ctltable.py), c = -log mu; terminal source intercept a' >= a (free), b = B*(a').
"""
import numpy as np


class Model:
    def __init__(self, ctl_npz, lw, h=0.0025, smin=0.0125, smax=5.0, ngrid_G=240):
        t = np.load(ctl_npz)
        self.P, self.MU, self.W, self.acl = t['P'], t['MU'], t['W'], t['a']
        self.acl = np.where(np.isfinite(self.acl), self.acl, np.inf)    # no certificate -> unusable
        self.C = -np.log(self.MU)
        self.h = h
        self.S = np.round(np.arange(smin, smax + h / 2, h), 10)
        self.lw = lw
        self.fh = lw.fhat(self.S)
        self.nG = ngrid_G
        self.fix1 = True
        self.PP = np.round(self.P * 80) / 80            # profile densities j/80 (controls at j/80 - 1e-6)
        self.dj = -np.log1p(-self.PP) + 1e-9          # child slopes

    # ---------- sources ----------
    def U_of(self, L):
        """unconditional bound from complementary pairs, on S where both S and 1/S are in range."""
        n = len(self.P); S = self.S
        inv = 1.0 / S
        ok = (inv >= S[0]) & (inv <= S[-1])
        U = np.full(len(S), np.inf)
        for j in range(n):
            jp = None
            # largest j' with P_j + P_j' <= 1
            cand = np.nonzero(self.PP <= 1 - self.PP[j] + 1e-12)[0]
            if len(cand) == 0: continue
            jp = cand[-1]
            refl = np.full(len(S), np.inf)
            refl[ok] = S[ok] * np.interp(inv[ok], S, L[jp])
            U = np.minimum(U, np.maximum(L[j], refl))
        return U

    def Bstar_fn(self, L, extra_lines=None):
        U = self.U_of(L)
        lam = np.exp(np.linspace(np.log(1e-3), np.log(1e3), 6000))
        F = self.lw.fhat(lam)
        inS = (lam >= self.S[0]) & (lam <= self.S[-1])
        F[inS] = np.minimum(F[inS], np.interp(lam[inS], self.S, U))
        self.Fsrc_lam, self.Fsrc = lam, F

        def Bstar(a):
            a = np.atleast_1d(a)
            return np.max((F[None, :] - a[:, None]) / lam[None, :], axis=1)
        return Bstar, U

    # ---------- descent ----------
    def descent_table(self, L, rho_idx, Gs, kp=None):
        """kp: steps per profile piece; if given also returns (M restricted to theta <= rho - kp*h, g at rho - kp*h)."""
        """For end point S[rho_idx] and start values Gs (array), integrate backward; return M[g, c] =
        max over theta in path (incl. rho) of g(theta) - theta*c, for c in self.C."""
        S, h = self.S, self.h
        g = Gs.copy()
        alive = np.ones(len(g), bool)
        M = g[:, None] - S[rho_idx] * self.C[None, :]
        Mr = np.full_like(M, -np.inf); gk = np.full(len(g), np.nan)
        cum = np.full(len(g), np.inf); Sr = np.zeros_like(M)        # cumulative child slack; slack at argmax theta
        for i in range(rho_idx, 0, -1):
            s0, s1 = S[i - 1], S[i]
            # candidate child j: L[j, i] < g and L[j, i-1] < g - h*d_j  (both ends of the step)
            g1 = g[:, None] - h * self.dj[None, :]
            okj = (L[None, :, i] < g[:, None] - 1e-9) & (L[None, :, i - 1] < g1 - 1e-9)
            has = okj.any(axis=1) & alive
            jstar = np.argmax(okj, axis=1)
            gnew = np.where(has, g - h * self.dj[jstar], g)
            st = np.minimum(g - L[jstar, i], gnew - L[jstar, i - 1]) - 1e-9
            cum = np.where(has, np.minimum(cum, st), cum)
            alive = has
            if not alive.any(): break
            g = gnew
            upd = g[:, None] - s0 * self.C[None, :]
            M = np.where(alive[:, None], np.maximum(M, upd), M)
            if kp is not None:
                if i - 1 == rho_idx - kp: gk = np.where(alive, g, np.nan)
                if i - 1 <= rho_idx - kp:
                    newmax = alive[:, None] & (upd > Mr)
                    Sr = np.where(newmax, cum[:, None], Sr)
                    Mr = np.where(newmax, upd, Mr)
        if kp is not None: return M, Mr, gk, Sr
        return M

    def route_values(self, L, Bstar, rho_idx_list, extra=np.linspace(0, 0.6, 61)):
        """returns Z[j, k] = best route/leaf height at density P[j], ratio S[rho_idx_list[k]], and argmin info."""
        nP, nMU, nW = self.acl.shape
        ag = np.linspace(0.0, 8.0, 8001); Bg = Bstar(ag)
        aeff = self.acl[:, None, :, :] + extra[None, :, None, None]          # (nP, ne, nMU, nW)
        beff = np.interp(aeff, ag, Bg)
        Z = np.full((nP, len(rho_idx_list)), np.inf); arg = {}
        for k, ri in enumerate(rho_idx_list):
            rho = self.S[ri]
            col = L[:, ri]
            fin = np.isfinite(col)
            lo = (col[fin].min() - 0.2) if fin.any() else 0.05
            hi = self.fh[ri] + 0.05
            Gs = np.linspace(max(lo, 1e-3), hi, self.nG)
            M = self.descent_table(L, ri, Gs)                                # (nG, nMU)
            rhs = aeff + rho * beff                                          # (nP, ne, nMU, nW)
            best = np.full((nP,), np.inf); barg = [None] * nP
            for im in range(nMU):
                for iw in range(nW):
                    Phi = Gs + self.W[iw] * M[:, im]
                    Phi = np.maximum.accumulate(Phi)
                    r = rhs[:, :, im, iw]
                    Gv = np.interp(r, Phi, Gs, left=Gs[0], right=np.inf)
                    Gv = np.where(np.isfinite(r), Gv, np.inf)
                    m = Gv.min(axis=1); e = Gv.argmin(axis=1)
                    better = m < best
                    for j in np.nonzero(better)[0]:
                        barg[j] = (im, iw, e[j])
                    best = np.where(better, m, best)
            Z[:, k] = best; arg[ri] = barg
        return Z, arg


    def piece_values(self, L, Bstar, kp=5, extra=np.linspace(0, 0.6, 61)):
        """Piece-consistent operator: knots S[0], S[kp], S[2kp], ...; piece k = [S[(k-1)kp], S[k kp]] realised by ONE
        leaf or ONE route with theta <= left end. Returns knot requirements: right[j,k] (piece k at its right end) and
        left[j,k] (piece k at its left end) for the best realisation of each piece (minimising left+right)."""
        nP, nMU, nW = self.acl.shape
        ag = np.linspace(0.0, 8.0, 8001); Bg = Bstar(ag)
        aeff = self.acl[:, None, :, :] + extra[None, :, None, None]
        beff = np.interp(aeff, ag, Bg)
        cw = self.C[None, None, :, None] * self.W[None, None, None, :]
        knots = list(range(kp, len(self.S), kp))
        R = np.full((nP, len(knots)), np.inf); Lft = np.full((nP, len(knots)), np.inf)
        hp = kp * self.h
        for k, ri in enumerate(knots):
            rho = self.S[ri]; lo_s = rho - hp
            # leaf: (a + r (b + w c))/(1+w), linear in r
            Wb = self.W[None, None, None, :]
            leafR = (aeff + rho * (beff + cw)) / (1 + Wb); leafL = (aeff + lo_s * (beff + cw)) / (1 + Wb)
            tot = (leafR + leafL).reshape(nP, -1); idx = np.argmin(tot, axis=1)
            bestR = leafR.reshape(nP, -1)[np.arange(nP), idx]; bestL = leafL.reshape(nP, -1)[np.arange(nP), idx]
            besttot = bestR + bestL
            col = L[:, ri]; fin = np.isfinite(col)
            lo = (col[fin].min() - 0.2) if fin.any() else 0.05
            Gs = np.linspace(max(lo, 1e-3), self.fh[ri] + 0.05, self.nG)
            M, Mr, gk, Sr = self.descent_table(L, ri, Gs, kp=kp)
            ok = np.isfinite(gk)
            if ok.sum() >= 2:
                Gs2, Mr2, gk2, Sr2 = Gs[ok], Mr[ok], gk[ok], Sr[ok]
                rhs = aeff + rho * beff
                for im in range(nMU):
                    for iw in range(nW):
                        w = self.W[iw]
                        Phi = np.maximum.accumulate(Gs2 + w * Mr2[:, im])
                        r = rhs[:, :, im, iw]
                        G = np.interp(r, Phi, Gs2, left=np.nan, right=np.nan)       # outside grid: unusable
                        G = np.where(np.isfinite(r) & (r >= Phi[0]), G, np.nan)
                        gl = np.interp(G, Gs2, gk2)
                        sl = np.maximum(np.interp(G, Gs2, Sr2[:, im]), 0) if self.fix1 else 0.0
                        gl = gl - sl            # fix 1: same path, start value lowered by the path's child slack
                        # left end: V = max(g(lo), T(lo)), T(lo) = (G - hp*b + w g(lo)) / (1+w)
                        Tl = (G - hp * beff[:, :, im, iw] + w * gl) / (1 + w)
                        Vl = np.maximum(gl, Tl)
                        t2 = G + Vl
                        t2 = np.where(np.isfinite(t2), t2, np.inf)
                        e = np.argmin(t2, axis=1); v = t2[np.arange(nP), e]
                        better = v < besttot
                        bestR = np.where(better, G[np.arange(nP), e], bestR)
                        bestL = np.where(better, Vl[np.arange(nP), e], bestL)
                        besttot = np.where(better, v, besttot)
            R[:, k] = bestR; Lft[:, k] = bestL
        return knots, R, Lft
