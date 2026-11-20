"""dp.py -- pointwise float model of the ZBS / Lu-Wang bank fixed point, written from SELF_CONTAINED.md Sections
14-17 (Definitions 5.1-5.6, Lemma 5.8, Theorem 5.7).  EXPLORATION ONLY: it ranks levers, it proves nothing.

Objects (all logs natural):
  F(lam)      source: R(k, lam k) <= exp(k F(lam) + o(k));  F = min(fhat_LW, U) with U from complementary pairs.
  L[j, i]     direct profile at density P_j, ratio S_i: d_R(V) >= P_j and |V| >= e^{k L} => red K_k or blue K_{S_i k}.
  U[i]        closed profile (complementary pairs), any host:  U(r) = min_j max(L_j(r), r L_{j'}(1/r)), P_j + P_j' <= 1.
  control     (pi = P_j - 1e-6, mu, w, a = -log x) from a table;  b = -log mu.
  B*(a)       best source line through intercept a:  sup_lam (F(lam) - a)/lam.
  Lam(a, r)   = min_{a' >= a} (a' + r B*(a'))   (terminal source intercept a' >= the control's a).
  leaf        L(p, r) <= (Lam(a, r) + r w b)/(1 + w).
  route       L(p, r) <= G* where G* + w M_G = Lam(a, r), M_G = max_theta (psi_G(theta) - theta b), psi_G the greedy
              backward path from (r, G) with child slopes d_c = -log(1 - P_c) (bucket 0 = U, d ~ 0), psi > child.
"""
import json
import numpy as np
from fractions import Fraction as Fr

LWPATH = '<archive>/ramsey-unconditional/lw_5ec98f47/source.json'
TABLE = '<archive>/ramsey-zbs/ctltable2.npz'


class LWf:
    def __init__(self, path=LWPATH):
        d = json.load(open(path))
        self.x = np.array([float(Fr(a)) for a in d['nodes']]); self.v = np.array([float(Fr(a)) for a in d['values']])
        self.dv = np.array([float(Fr(a)) for a in d['derivatives']])

    def P(self, t):
        t = np.asarray(t, float); i = np.clip(np.searchsorted(self.x, t, 'right') - 1, 0, len(self.x) - 2)
        a, b = self.x[i], self.x[i + 1]; dl = b - a; u = t - a; D = self.v[i + 1] - self.v[i]
        return (self.v[i] + self.dv[i] * u + (3 * D / dl - 2 * self.dv[i] - self.dv[i + 1]) / dl * u ** 2
                + (self.dv[i] + self.dv[i + 1] - 2 * D / dl) / dl ** 2 * u ** 3)

    def f(self, s):
        s = np.asarray(s, float)
        with np.errstate(all='ignore'):
            h = (1 + s) * np.log1p(s) - np.where(s > 0, s * np.log(np.where(s > 0, s, 1)), 0)
        return h + s * np.exp(-s) * self.P(s)

    def fhat(self, lam):
        lam = np.asarray(lam, float)
        return np.where(lam <= 1, self.f(np.minimum(lam, 1)), lam * self.f(1 / np.maximum(lam, 1)))


def es_hat(lam):
    """Erdos-Szekeres exponent: (1+lam) log(1+lam) - lam log lam (symmetric: lam*es(1/lam) = es(lam))."""
    lam = np.asarray(lam, float)
    return (1 + lam) * np.log1p(lam) - lam * np.log(lam)


class Model:
    def __init__(self, PP, MU, W, a, fhat, h=1 / 80, smax=5.0, nG=160, Agrid=(0.25, 4.0, 4e-4), routes=True,
                 feedback=True, umin=0.2):
        self.PP = np.asarray(PP, float); self.MU = np.asarray(MU, float); self.W = np.asarray(W, float)
        a = np.where(np.isfinite(a), a, np.inf)
        self.a = np.minimum.accumulate(a, axis=0)            # a control of lower density may be used
        self.b = -np.log(self.MU) + 1e-9
        self.fhat = fhat
        self.h = h
        self.S = np.round(h * np.arange(1, int(round(smax / h)) + 1), 12)
        self.nS = len(self.S); self.nP = len(self.PP); self.nG = nG
        self.d = np.concatenate([[1e-6], -np.log1p(-self.PP)]) + 1e-9      # bucket 0 = U
        self.Ag = np.arange(*Agrid)
        self.routes, self.feedback, self.umin = routes, feedback, umin
        self.lam = np.exp(np.linspace(np.log(1e-3), np.log(1e3), 8000))
        self.F_lam = self.fhat(self.lam)
        self.L = np.full((self.nP, self.nS), np.inf)
        self.U = np.full(self.nS, np.inf)
        self.jh = int(np.argmin(abs(self.PP - 0.5))); self.i1 = int(np.argmin(abs(self.S - 1.0)))
        # complementary partner: largest j' with P_j + P_j' <= 1
        self.jp = np.array([int(np.searchsorted(self.PP, 1 - p + 1e-12)) - 1 for p in self.PP])

    # ------------------------------------------------------------------ sources
    def comp_U(self, Lpm):
        S = self.S; inv = 1 / S
        ok = (inv >= S[0]) & (inv <= S[-1]) & (S >= self.umin - 1e-12) & (S <= 1 / self.umin + 1e-12)
        U = np.full(self.nS, np.inf)
        for j in range(self.nP):
            jp = self.jp[j]
            if jp < 0: continue
            refl = np.full(self.nS, np.inf)
            refl[ok] = S[ok] * np.interp(inv[ok], S, Lpm[jp])
            U = np.minimum(U, np.maximum(Lpm[j], refl))
        return U

    def sources(self, U):
        F = self.F_lam.copy()
        if self.feedback:
            inS = (self.lam >= self.S[0]) & (self.lam <= self.S[-1])
            Ui = np.interp(self.lam[inS], self.S, np.where(np.isfinite(U), U, 1e9))
            F[inS] = np.minimum(F[inS], Ui)
        self.F = F
        B = np.empty(len(self.Ag))
        for s0 in range(0, len(self.Ag), 500):
            A = self.Ag[s0:s0 + 500]
            B[s0:s0 + 500] = np.max((F[None, :] - A[:, None]) / self.lam[None, :], axis=1)
        self.Bst = B
        # Lam table: for each ratio, suffix-min over a' >= a of a' + r B*(a')
        V = self.Ag[None, :] + self.S[:, None] * B[None, :]
        self.Lam = np.minimum.accumulate(V[:, ::-1], axis=1)[:, ::-1]           # (nS, nA)

    def Lam_of(self, e, a):
        return np.interp(a, self.Ag, self.Lam[e], left=np.nan, right=np.inf)

    # ------------------------------------------------------------------ descent
    def descent(self, Lb, Gt):
        """Lb (nB, nS) child values (bucket 0 = U); Gt (nS, nG) start values per end index.
        Returns M (nS, nG, nMU) = max over theta in path of psi(theta) - theta*b."""
        nB = Lb.shape[0]; h = self.h; S = self.S
        E = np.full((nB, self.nS), np.inf)
        E[:, 1:] = np.maximum(Lb[:, 1:], Lb[:, :-1] + h * self.d[:, None])
        m = np.minimum.accumulate(E, axis=0)                    # (nB, nS) nonincreasing in j
        g = Gt.copy(); alive = np.ones(g.shape, bool)
        M = g[:, :, None] - S[:, None, None] * self.b[None, None, :]
        ee = np.arange(self.nS)
        for k in range(self.nS - 1):
            i = ee - k
            act = (i >= 1)
            if not act.any(): break
            idx = np.where(act, i, 1)
            mm = m[:, idx]                                       # (nB, nS)
            cnt = (mm[:, :, None] >= g[None, :, :] - 1e-12).sum(axis=0)      # first bucket with m < g
            ok = act[:, None] & alive & (cnt < nB)
            if not ok.any(): break
            jj = np.minimum(cnt, nB - 1)
            g = np.where(ok, g - h * self.d[jj], g)
            alive = ok
            upd = g[:, :, None] - S[np.maximum(idx - 1, 0)][:, None, None] * self.b[None, None, :]
            M = np.where(ok[:, :, None], np.maximum(M, upd), M)
        return M

    # ------------------------------------------------------------------ one round
    def round(self):
        Lpm = np.minimum.accumulate(self.L, axis=0)
        U = self.comp_U(Lpm)
        self.U = np.minimum(self.U, U)
        self.sources(self.U)
        nP, nMU, nW, nS = self.nP, len(self.MU), len(self.W), self.nS
        W = self.W
        # leaves
        Vleaf = np.full((nP, nS), np.inf)
        LamA = np.empty((nS, nP, nMU, nW))
        for e in range(nS):
            LamA[e] = self.Lam_of(e, self.a)
            v = (LamA[e] + self.S[e] * W[None, None, :] * self.b[None, :, None]) / (1 + W[None, None, :])
            Vleaf[:, e] = np.nanmin(v.reshape(nP, -1), axis=1)
        V = Vleaf
        if self.routes:
            Lb = np.vstack([self.U[None, :], Lpm])
            cur = np.minimum(np.min(Lpm, axis=0), Vleaf.min(axis=0))
            hi = np.minimum(Vleaf.max(axis=0), self.fhat(self.S)) + 0.02
            lo = np.maximum(cur - 0.45, 0.01)
            Gt = lo[:, None] + (hi - lo)[:, None] * np.linspace(0, 1, self.nG)[None, :]
            M = self.descent(Lb, Gt)
            Vr = np.full((nP, nS), np.inf)
            for e in range(nS):
                Gs = Gt[e]
                for im in range(nMU):
                    for iw in range(nW):
                        Phi = np.maximum.accumulate(Gs + W[iw] * M[e, :, im])
                        tgt = LamA[e][:, im, iw]
                        Gv = np.interp(tgt, Phi, Gs, left=np.nan, right=np.inf)
                        Gv = np.where(np.isfinite(tgt), Gv, np.inf)
                        Vr[:, e] = np.fmin(Vr[:, e], Gv)
            self.low_flag = int(np.isnan(Vr).sum())
            V = np.fmin(V, Vr)
        self.L = np.minimum(self.L, V)
        Lpm = np.minimum.accumulate(self.L, axis=0)
        self.U = np.minimum(self.U, self.comp_U(Lpm))
        return float(Lpm[self.jh, self.i1]), float(self.U[self.i1])

    def run(self, rounds, tol=1e-7, log=None):
        hist = []
        for r in range(rounds):
            z, zu = self.round()
            hist.append(z)
            if log: log('round %d  L_1/2(1) = %.7f  U(1) = %.7f  e^z = %.5f' % (r, z, zu, np.exp(zu)))
            if len(hist) > 2 and abs(hist[-2] - hist[-1]) < tol: break
        return hist


def load_table(path=TABLE, pstep=1, mustep=1, wstep=1):
    t = np.load(path)
    PP, MU, W, a = t['PP'], t['MU'], t['W'], t['a']
    sel = np.arange(0, len(PP), pstep)
    return PP[sel], MU[::mustep], W[::wstep], a[sel][:, ::mustep, ::wstep]
