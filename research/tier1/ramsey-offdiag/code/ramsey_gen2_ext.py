"""ramsey_gen2_ext.py: copy of research/tier2/ramsey-zbs/search/gen2.py (19 Nov 2026) with the ratio range [1/5, 5]
made a parameter RMAX (environment QV_RMAX, default 5 = the original). FLOAT GATE for extending the bank below ratio
1/5 (off-diagonal lane); proves nothing.

gen2.py: REALISABLE search model for an extended ZBS bank (exploration; proposes data, proves nothing).

Replaces fixedpoint.py.  Every value is meant to be realisable by objects in ZBS's certificate format
(Lemmas/DiagRamsey_V5Fast.lean: LeafF, RouteF, ClosedPF.complRaw, SourceF):
 * raw objects = ZBS raw profiles (Lean-checked by ZBS) + new raw profiles (one per density bucket per round), all with
   knots on the ratio grid S_i = (5 + i)/400; a new profile is realised piecewise (kp grid steps per piece) by ONE leaf
   or ONE route, and its node values are the realisation's exact values (shared knots: max of the two pieces);
 * one closed object U per round (density 1e-6; ClosedPF.complRaw with RAW objects only), knots on T_U = grid points
   of [1/5, 5] and their reciprocals;
 * a route step [S_{i-1}, S_i] with child bucket j uses ONE raw object o (or U for j = 0) with
   max(o(S_i), o(S_{i-1}) + h d_j) < g(S_i)  (child below the path at both ends; knots on the grid, so exact);
 * source lines A + B t: cells of T_U (pairs of raw objects R, S with p_R + p_S <= 1, line above R(t) and t S(1/t) at
   both cell ends) or grounded (one LW tangent line of ZBS's 1,128), LW lines elsewhere; plus ZBS's own 2,713 lines;
 * controls: certifiable a = -log x from ctltable2 (Lemma C, ZBS form, N = 512); a route/leaf uses a' = a + e >= A
   of its terminal source (aU >= max(a, A)), b = B(a').
Fixes over fixedpoint.py: children from single objects (not mixed bucket envelopes); exact node values; T(lo) uses the
UNSHIFTED path (fixedpoint.py lowered it by fix 1's slack, an optimistic bug); piece choice by minimax regret over the
piece's candidates at both ends (fix (b)); 1/160 densities near 1/2; extended control box (mu >= 0.01, w <= 16)."""
import json, os
import numpy as np
from fractions import Fraction as Fr

H = 1.0 / 400
RMAX = float(os.environ.get("QV_RMAX", "5"))
NS = int(round(RMAX * 400)) - 4             # S_i = (5 + i)/400, i = 0..NS-1 (0.0125 .. RMAX); 1996 for RMAX = 5
DELTA = 1e-9                                # strict-inequality slack used everywhere in the float model


def fr(s): return float(Fr(s))


class Gen:
    def __init__(self, zbs_json, table_npz, kp=5, nG=200):
        b = json.load(open(zbs_json))
        self.S = (5 + np.arange(NS)) / 400.0
        t = np.load(table_npz)
        self.PP = np.concatenate([[1e-6], t['PP']])               # bucket 0: the closed pair object U
        self.nB = len(self.PP)
        self.d = -np.log1p(-self.PP) + 1e-9
        a = np.where(np.isfinite(t['a']), t['a'], np.inf)
        self.acl = np.concatenate([np.full((1,) + a.shape[1:], np.inf), a])
        self.MU, self.W = t['MU'], t['W']
        self.C = -np.log(self.MU) + 1e-9                           # bU slightly above -log mu (nu < mu)
        self.kp, self.nG = kp, nG
        L = np.array([[fr(c), fr(d)] for c, d in b['lines']])
        self.lc, self.ld = L[:, 0], L[:, 1]
        A = np.array([fr(x) for x in b['A']]); Bz = np.array([fr(x) for x in b['B']])
        o = np.argsort(A); self.zA, self.zB = A[o], np.minimum.accumulate(Bz[o])
        # raw pool: ZBS raw profiles
        self.pool_p, self.pool_v, self.pool_tag = [], [], []
        for k, d in enumerate(b['raw']):
            xs = np.array([fr(x) for x in d['xs']]); ys = np.array([fr(y) for y in d['ys']])
            i0 = int(round(xs[0] * 400)) - 5; i1 = int(round(xs[-1] * 400)) - 5
            assert abs(self.S[i0] - xs[0]) < 1e-12 and abs(self.S[i1] - xs[-1]) < 1e-12
            v = np.full(NS, np.inf); v[i0:i1 + 1] = np.interp(self.S[i0:i1 + 1], xs, ys)
            self.add_raw(fr(d['p']), v, ('zr', k))
        # T_U: grid points of [1/5, 5] and reciprocals
        g = self.S[(self.S >= 1 / RMAX - 1e-12)]
        self.TU = np.unique(np.round(np.concatenate([g, 1.0 / g]), 12))
        self.TU = self.TU[(self.TU >= 1 / RMAX - 1e-12) & (self.TU <= RMAX + 1e-12)]
        # coarse knots of U: multiples of 1/80 in [1/5, 5] and their reciprocals (a subset of T_U, closed under 1/t)
        c80 = np.arange(int(round(80 / RMAX)), int(round(80 * RMAX)) + 1) / 80.0
        K = np.unique(np.round(np.concatenate([c80, 1.0 / c80]), 12))
        self.K = K[(K >= 1 / RMAX - 1e-12) & (K <= RMAX + 1e-12)]
        self.Kidx = np.searchsorted(self.TU, self.K - 1e-12)
        assert np.all(np.abs(self.TU[self.Kidx] - self.K) < 1e-11)
        self.Krec = np.searchsorted(self.K, 1.0 / self.K - 1e-9)
        assert np.all(np.abs(self.K[self.Krec] - 1.0 / self.K) < 1e-9)
        self.U = None; self.Uhist = []
        self.round = 0

    # ---------------- pool ----------------
    def bucket_of(self, p):
        return int(np.searchsorted(self.PP, p - 1e-12))

    def add_raw(self, p, v, tag):
        self.pool_p.append(p); self.pool_v.append(v); self.pool_tag.append(tag)

    def arrays(self):
        V = np.array(self.pool_v); P = np.array(self.pool_p)
        Bk = np.array([self.bucket_of(p) for p in P])
        return V, P, Bk

    # ---------------- children ----------------
    def child_env(self):
        """E[j, i] (i >= 1): min over raw objects of bucket j of max(v(S_i), v(S_{i-1}) + h d_j); bucket 0 = U with its
        interior knots.  Only the object's own bucket is needed (first-fit descent picks the least slope)."""
        V, P, Bk = self.arrays()
        E = np.full((self.nB, NS), np.inf); Earg = np.full((self.nB, NS), -1, np.int64)
        for j in range(1, self.nB):
            idx = np.nonzero(Bk == j)[0]
            if len(idx) == 0: continue
            M = np.maximum(V[idx, 1:], V[idx, :-1] + H * self.d[j])
            a = np.argmin(M, axis=0)
            E[j, 1:] = M[a, np.arange(NS - 1)]; Earg[j, 1:] = idx[a]
        if self.Uhist:
            rows = np.array([self._e0(h[0]) for h in self.Uhist])
            q = np.argmin(rows, axis=0)
            E[0] = rows[q, np.arange(NS)]; Earg[0] = np.where(np.isfinite(E[0]), q, -1); E[0, 0] = np.inf
        self.E, self.Earg = E, Earg
        self.negm = -np.minimum.accumulate(E, axis=0)            # -prefix-min over buckets, nondecreasing in j

    def _e0(self, Q):
        """step needs of one U object (values Q at T_U; PL between its knots, which lie in T_U)."""
        T = self.TU
        ok = np.isfinite(Q)
        st = np.clip(np.ceil((T - self.S[0]) / H - 1e-9).astype(int), 1, NS - 1)
        val = Q + (self.S[st] - T) * self.d[0]
        e0 = np.full(NS, -np.inf); np.maximum.at(e0, st[ok], val[ok])
        Ug = np.full(NS, np.inf)
        inT = np.searchsorted(T, self.S - 1e-12)
        on = (inT < len(T)) & (np.abs(T[np.minimum(inT, len(T) - 1)] - self.S) < 1e-12)
        Ug[on] = Q[inT[on]]
        e0[1:] = np.maximum(e0[1:], np.maximum(Ug[1:], Ug[:-1] + H * self.d[0]))
        e0[~np.isfinite(e0)] = np.inf
        e0[0] = np.inf
        return e0

    def descent(self, r, G):
        """first-fit backward descent from S_r with start values G (array).  Returns gp (value at node i, -inf if
        dead), jst (bucket used on step i), sl (slack on step i)."""
        nG = len(G); g = np.array(G, float)
        gp = np.full((nG, r + 1), -np.inf); gp[:, r] = g
        jst = np.full((nG, r + 1), -1, np.int64); sl = np.full((nG, r + 1), np.inf)
        alive = np.ones(nG, bool)
        for i in range(r, 0, -1):
            j = np.searchsorted(self.negm[:, i], -(g - DELTA), side='right')
            alive = alive & (j < self.nB)
            if not alive.any(): break
            jj = np.minimum(j, self.nB - 1)
            slack = g - self.E[jj, i]
            g = np.where(alive, g - H * self.d[jj], g)
            gp[:, i - 1] = np.where(alive, g, -np.inf)
            jst[:, i] = np.where(alive, jj, -1); sl[:, i] = np.where(alive, slack, np.inf)
        return gp, jst, sl

    # ---------------- sources ----------------
    def lw_T(self, t):
        t = np.atleast_1d(t)
        return np.min(self.lc[None, :] + self.ld[None, :] * t[:, None], axis=1)

    def lw_line_at(self, t):
        t = np.atleast_1d(t)
        return np.argmin(self.lc[None, :] + self.ld[None, :] * t[:, None], axis=1)

    def pair_cells(self):
        """for each T_U cell k = [T_k, T_{k+1}]: best pair of raw objects (R, S), p_R + p_S <= 1, minimising the larger
        endpoint requirement; returns req0, req1 (requirements at both ends) and the object indices."""
        V, P, Bk = self.arrays()
        T = self.TU; nT = len(T)
        lo_i = np.array([np.argmax(np.isfinite(v)) for v in V]); hi_i = NS - 1 - np.array([np.argmax(np.isfinite(v[::-1])) for v in V])
        dlo, dhi = self.S[lo_i], self.S[hi_i]
        VT = np.full((len(V), nT), np.inf); VR = np.full((len(V), nT), np.inf)
        for o in range(len(V)):
            m = (T >= dlo[o] - 1e-12) & (T <= dhi[o] + 1e-12)
            if m.any(): VT[o, m] = np.interp(T[m], self.S[lo_i[o]:hi_i[o] + 1], V[o, lo_i[o]:hi_i[o] + 1])
            mr = (1 / T >= dlo[o] - 1e-12) & (1 / T <= dhi[o] + 1e-12)
            if mr.any(): VR[o, mr] = T[mr] * np.interp(1 / T[mr], self.S[lo_i[o]:hi_i[o] + 1], V[o, lo_i[o]:hi_i[o] + 1])
        Rm = np.full((self.nB, nT - 1), np.inf); Ra = np.full((self.nB, nT - 1), -1)
        Sm = np.full((self.nB, nT - 1), np.inf); Sa = np.full((self.nB, nT - 1), -1)
        for j in range(1, self.nB):
            idx = np.nonzero(Bk == j)[0]
            if len(idx) == 0: continue
            mR = np.maximum(VT[idx, :-1], VT[idx, 1:]); a = np.argmin(mR, 0)
            Rm[j] = mR[a, np.arange(nT - 1)]; Ra[j] = idx[a]
            mS = np.maximum(VR[idx, :-1], VR[idx, 1:]); a = np.argmin(mS, 0)
            Sm[j] = mS[a, np.arange(nT - 1)]; Sa[j] = idx[a]
        # prefix minima over buckets (objects of lower density usable at higher buckets)
        for X, Xa in ((Rm, Ra), (Sm, Sa)):
            for j in range(1, self.nB):
                b = X[j - 1] < X[j]
                X[j] = np.where(b, X[j - 1], X[j]); Xa[j] = np.where(b, Xa[j - 1], Xa[j])
        best = np.full(nT - 1, np.inf); bR = np.full(nT - 1, -1); bS = np.full(nT - 1, -1)
        for j in range(1, self.nB):
            jp = int(np.searchsorted(self.PP, 1 - self.PP[j] + 1e-12)) - 1
            if jp < 1: continue
            v = np.maximum(Rm[j], Sm[jp]); bb = v < best
            best = np.where(bb, v, best); bR = np.where(bb, Ra[j], bR); bS = np.where(bb, Sa[jp], bS)
        k = np.arange(nT - 1); ok = bR >= 0
        req0 = np.full(nT - 1, np.inf); req1 = np.full(nT - 1, np.inf)
        req0[ok] = np.maximum(VT[bR[ok], k[ok]], VR[bS[ok], k[ok]])
        req1[ok] = np.maximum(VT[bR[ok], k[ok] + 1], VR[bS[ok], k[ok] + 1])
        return req0, req1, bR, bS

    def build_sources(self):
        """U (closed pair object) and the best-line function B(A) for the current pool."""
        req0, req1, bR, bS = self.pair_cells()
        T = self.TU; K, Ki = self.K, self.Kidx
        y = np.full(len(T), -np.inf)
        y[:-1] = np.maximum(y[:-1], req0); y[1:] = np.maximum(y[1:], req1)
        y[~np.isfinite(y)] = np.inf
        # coarse closed object: knots K; on each coarse interval the chord must lie above every fine requirement
        nK = len(K); e = np.full(nK - 1, np.inf)
        for m in range(nK - 1):
            f = slice(Ki[m], Ki[m + 1] + 1); yy = y[f]
            if not np.all(np.isfinite(yy)): continue
            ch = yy[0] + (yy[-1] - yy[0]) * (T[f] - T[Ki[m]]) / (T[Ki[m + 1]] - T[Ki[m]])
            e[m] = max(0.0, float(np.max(yy - ch)))
        QK = np.full(nK, np.inf)
        el = np.concatenate([[-np.inf], e]); er = np.concatenate([e, [-np.inf]])
        okK = np.isfinite(y[Ki])
        rise = np.maximum(np.where(np.isfinite(el), el, -np.inf), np.where(np.isfinite(er), er, -np.inf))
        defined = okK & np.isfinite(rise)
        QK[defined] = y[Ki][defined] + rise[defined]
        # a knot whose two neighbouring intervals are undefined is unusable; an interval is usable if both ends are
        U = np.full(len(T), np.inf)
        for m in range(nK - 1):
            if np.isfinite(e[m]) and np.isfinite(QK[m]) and np.isfinite(QK[m + 1]):
                f = slice(Ki[m], Ki[m + 1] + 1)
                U[f] = QK[m] + (QK[m + 1] - QK[m]) * (T[f] - K[m]) / (K[m + 1] - K[m])
        self.U = U; self.Uhist.append((U.copy(), bR.copy(), bS.copy(), QK.copy()))
        self.paircells = (req0, req1, bR, bS)
        # source cells: coarse intervals of K with the pair (U, U) [p = 1e-6 each], or grounded fine cells
        FK = np.maximum(QK, K * QK[self.Krec])
        mid = 0.5 * (T[:-1] + T[1:]); k = self.lw_line_at(mid)
        g0 = self.lc[k] + self.ld[k] * T[:-1]; g1 = self.lc[k] + self.ld[k] * T[1:]
        out = np.exp(np.concatenate([np.linspace(np.log(2e-3), np.log(1 / RMAX), 1500), np.linspace(np.log(RMAX), np.log(500), 1500)]))
        out = np.unique(out); om = 0.5 * (out[:-1] + out[1:]); ko = self.lw_line_at(om)
        keep = ~((out[:-1] >= 1 / RMAX - 1e-12) & (out[1:] <= RMAX + 1e-12))
        o0, o1 = out[:-1][keep], out[1:][keep]; ko = ko[keep]
        self.cells = dict(T=T, K=K, Ki=Ki, FK=FK, g0=g0, g1=g1, o0=o0, o1=o1,
                          og0=self.lc[ko] + self.ld[ko] * o0, og1=self.lc[ko] + self.ld[ko] * o1)
        Ag = np.arange(0.10, 8.0, 0.0005)
        c = self.cells
        Bst = np.full(len(Ag), -np.inf)
        for s0 in range(0, len(Ag), 200):
            A = Ag[s0:s0 + 200][:, None]
            vg = np.maximum((c['g0'][None] - A) / T[None, :-1], (c['g1'][None] - A) / T[None, 1:])   # fine grounded
            vgK = np.maximum.reduceat(vg, Ki[:-1], axis=1)                                         # per coarse interval
            vp = np.maximum((FK[None, :-1] - A) / K[None, :-1], (FK[None, 1:] - A) / K[None, 1:])
            vp = np.where(np.isfinite(vp), vp, np.inf)
            inner = np.max(np.minimum(vp, vgK), axis=1)
            outer = np.max(np.maximum((c['og0'][None] - A) / c['o0'][None], (c['og1'][None] - A) / c['o1'][None]), axis=1)
            Bst[s0:s0 + 200] = np.maximum(inner, outer)
        Bst = np.maximum(Bst, 1e-6) + 2e-9
        self.Ag, self.Bown = Ag, Bst
        self.Bown_hist = getattr(self, 'Bown_hist', []); self.Bown_hist.append(Bst.copy())
        k = np.searchsorted(self.zA, Ag, 'right') - 1
        self.Bz = np.where(k >= 0, self.zB[np.maximum(k, 0)], np.inf)
        self.Bgrid = np.minimum(self.Bown, self.Bz)

    def Bfun(self, a):
        """B at intercept a: linear interpolation of the convex own function (>= the true B*: realisable), or ZBS's line
        with A <= a."""
        a = np.asarray(a, float)
        own = np.full(a.shape, np.inf)
        for Bq in getattr(self, 'Bown_hist', [self.Bown]):       # a line valid for an earlier pool stays valid
            own = np.minimum(own, np.interp(a, self.Ag, Bq, left=np.inf, right=Bq[-1]))
        k = np.searchsorted(self.zA, a, 'right') - 1
        z = np.where(k >= 0, self.zB[np.maximum(k, 0)], np.inf)
        return np.minimum(own, z)


    # ---------------- one knot ----------------
    def Mtab(self, gp, suf, l, r):
        """for every mu: M[G, imu] = max_{i <= l} (g_i - S_i c), theta index, slack sigma over steps (theta, r]."""
        X = gp[:, :l + 1]; Sx = self.S[:l + 1]; nG = X.shape[0]
        M = np.empty((nG, len(self.C))); th = np.empty((nG, len(self.C)), np.int64)
        for imu, c in enumerate(self.C):
            val = X - Sx[None, :] * c
            t = np.argmax(val, axis=1); th[:, imu] = t; M[:, imu] = val[np.arange(nG), t]
        sig = suf[np.arange(nG)[:, None], np.minimum(th + 1, r)]
        return M, th, sig

    def exact_cands(self, combos, extras, Gs, gp, M, sig, l, r):
        """EXACT end values for candidates (imu, iw, e) per bucket: every sampled start value G_k gives a realisable
        route (path from the descent at G_k, start lowered by its slack sigma_k):
          V(hi) = max(G_k - sigma_k, (a' + hi b + w (G_k - M_k)) / (1 + w)),
          V(lo) = max(g_k(lo) - sigma_k, (a' + lo b + w (g_k(lo) - M_k)) / (1 + w)).
        For each (bucket, extra) the sample minimising V(hi) is found on the Pareto frontier of (G - sigma, G - M).
        Leaves: V(s) = (a' + s (b + w c)) / (1 + w).  Returns list of (imu, iw, kind, Vlo, Vhi, kidx)."""
        rho, slo = self.S[r], self.S[l]
        gl = gp[:, l]
        out = []
        for imu, iw in combos:
            c, w = self.C[imu], self.W[iw]; wp = w / (1 + w)
            ap = self.acl[:, imu, iw][:, None] + extras[None, :]
            bb = self.Bfun(ap)
            out.append((imu, iw, 0, (ap + slo * (bb + w * c)) / (1 + w), (ap + rho * (bb + w * c)) / (1 + w), None))
            ok = np.isfinite(M[:, imu]) & np.isfinite(gl)
            if not ok.any(): continue
            k_ok = np.nonzero(ok)[0]
            Ge = Gs[k_ok] - sig[k_ok, imu]; D = Gs[k_ok] - M[k_ok, imu]
            o = np.lexsort((D, Ge)); Ge, D, kk = Ge[o], D[o], k_ok[o]
            keep = D < np.minimum.accumulate(np.concatenate([[np.inf], D[:-1]]))
            Ge, D, kk = Ge[keep], D[keep], kk[keep]
            key = Ge - wp * D                                         # increasing along the frontier
            Cc = (ap + rho * bb) / (1 + w)
            ks = np.searchsorted(key, Cc)
            k1 = np.clip(ks, 0, len(kk) - 1); k0 = np.clip(ks - 1, 0, len(kk) - 1)
            f1 = np.maximum(Ge[k1], Cc + wp * D[k1]); f0 = np.maximum(Ge[k0], Cc + wp * D[k0])
            use0 = f0 < f1
            kb = np.where(use0, k0, k1); Vhi = np.where(use0, f0, f1)
            kg = kk[kb]
            glk = gl[kg]; sgk = sig[kg, imu]; Mk = M[kg, imu]
            Vlo = np.maximum(glk - sgk, (ap + slo * bb) / (1 + w) + wp * (glk - Mk))
            Vhi = np.where(np.isfinite(ap) & np.isfinite(bb), Vhi, np.inf)
            out.append((imu, iw, 1, Vlo, Vhi, kg))
        return out

    @staticmethod
    def pick(cands, point):
        """minimax regret over candidates per bucket (point: least right-end value)."""
        VL = np.stack([np.where(np.isfinite(c[3]), c[3], np.inf) for c in cands])
        VH = np.stack([np.where(np.isfinite(c[4]), c[4], np.inf) for c in cands])
        if point: score = VH
        else:
            with np.errstate(invalid='ignore'):
                bl = VL.min(axis=(0, 2)); bh = VH.min(axis=(0, 2))
                score = np.maximum(VL - bl[None, :, None], VH - bh[None, :, None])
                score = np.where(np.isfinite(score), score, np.inf)
        nc, nB, ne = score.shape
        flat = score.transpose(1, 0, 2).reshape(nB, -1)
        k = np.argmin(flat, axis=1)
        return k // ne, k % ne, flat[np.arange(nB), k]

    def Ggrid(self, Lcol, rho, point):
        fin = np.unique(np.round(Lcol[np.isfinite(Lcol)], 4))
        if len(fin) == 0:
            top = float(self.lw_T(rho)[0]) + 1.0; return np.linspace(0.02, top, 300)
        parts = [np.linspace(max(fin.min() - 0.3, 1e-3), fin.max() + 0.1, 150)]
        loc = np.linspace(-0.02, 0.004, 400 if point else 32)
        for v in fin: parts.append(v + loc)
        return np.unique(np.concatenate(parts))

    def knot(self, r, extras, Lcol, point=False, only=None, full=False):
        """realise the piece [S_{r-kp}, S_r] (point: the single ratio S_r, routes with theta <= S_{r-1}, or a leaf) for
        every bucket (or the buckets in `only`).  Returns a list of records with EXACT node values."""
        l = r - 1 if point else r - self.kp
        rho = self.S[r]
        if only is not None: Lcol = np.where(np.isin(np.arange(self.nB), list(only)), Lcol, np.nan)
        Gs = self.Ggrid(Lcol, rho, point)
        gp, jst, sl = self.descent(r, Gs)
        suf = np.minimum.accumulate(sl[:, ::-1], axis=1)[:, ::-1]
        M, th, sig = self.Mtab(gp, suf, l, r)
        nmu, nw = len(self.MU), len(self.W)
        if full: combos = [(i, k) for i in range(nmu) for k in range(nw)]
        else: combos = [(i, k) for i in range(1, nmu, 4) for k in range(1, nw, 4)]
        cands = self.exact_cands(combos, extras, Gs, gp, M, sig, l, r)
        ci, ei, sc = self.pick(cands, point)
        if not full:
            need = set()
            for j in range(self.nB):
                if not np.isfinite(sc[j]): continue
                imu, iw = cands[ci[j]][0], cands[ci[j]][1]
                for a in range(-2, 3):
                    for b in range(-2, 3):
                        if 0 <= imu + a < nmu and 0 <= iw + b < nw: need.add((imu + a, iw + b))
            need -= set(combos)
            if need:
                cands = cands + self.exact_cands(sorted(need), extras, Gs, gp, M, sig, l, r)
                ci, ei, sc = self.pick(cands, point)
        recs = [None] * self.nB
        for j in range(self.nB):
            if only is not None and j not in only: continue
            if not np.isfinite(sc[j]): continue
            imu, iw, kind, _, _, kg = cands[ci[j]]
            c, w = self.C[imu], self.W[iw]
            e = extras[ei[j]]; ap = self.acl[j, imu, iw] + e; bb = float(self.Bfun(ap))
            rec = dict(j=j, r=r, l=l, kind=kind, imu=imu, iw=iw, a=ap, b=bb, round=self.round)
            if kind == 0:
                rec['vals'] = (ap + self.S[l:r + 1] * (bb + w * c)) / (1 + w)
            else:
                k = int(kg[j, ei[j]]); t = int(th[k, imu]); sg = float(sig[k, imu])
                gpath = gp[k, l:r + 1]
                T = (ap + self.S[l:r + 1] * bb + w * (self.S[t] * c + gpath - gp[k, t])) / (1 + w)
                rec.update(G=float(Gs[k]), th=t, sigma=sg, vals=np.maximum(gpath - sg, T))
            recs[j] = rec
        return recs

    # ---------------- rounds ----------------
    def envelope(self):
        V, P, Bk = self.arrays()
        L = np.full((self.nB, NS), np.inf)
        for j in range(1, self.nB):
            idx = np.nonzero(Bk == j)[0]
            if len(idx): L[j] = V[idx].min(axis=0)
        L = np.minimum.accumulate(L, axis=0)
        return L

    def run_round(self, extras, log=print, root_only=False):
        import time
        t0 = time.time()
        self.build_sources(); self.child_env()
        self.E_hist = getattr(self, 'E_hist', []); self.E_hist.append((self.E.copy(), self.Earg.copy()))
        L = self.envelope()
        i1 = int(np.argmin(abs(self.S - 1.0))); jh = int(np.argmin(abs(self.PP - 0.5)))
        root = self.knot(i1, extras, L[:, i1], point=True, only={jh}, full=True)[jh]
        log('round %d: sources/children %.0fs; ROOT (point, p=1/2, ratio 1) %.9f  [%s]  B(1.0862)=%.6f' % (
            self.round, time.time() - t0, root['vals'][-1] if root else np.nan,
            'leaf' if root and root['kind'] == 0 else 'route mu=%.4f w=%.4f a=%.5f b=%.5f' % (
                self.MU[root['imu']], self.W[root['iw']], root['a'], root['b']) if root else '-', float(self.Bfun(1.0862))))
        self.last_root = root
        if root_only: return root
        newv = np.full((self.nB, NS), np.inf); recs = []
        for r in range(self.kp, NS, self.kp):
            rr = self.knot(r, extras, L[:, r])
            for rec in rr:
                if rec is None: continue
                j, l = rec['j'], rec['l']
                v = rec['vals']
                newv[j, l] = max(newv[j, l], v[0]) if np.isfinite(newv[j, l]) else v[0]
                newv[j, l + 1:r + 1] = v[1:]
                recs.append(rec)
        # pieces that are not realised leave gaps (inf); shared knots took the max of both pieces
        gain = np.where(np.isfinite(newv) & np.isfinite(L), L - newv, np.nan)
        for j in range(1, self.nB):
            if np.isfinite(newv[j]).any(): self.add_raw(self.PP[j], newv[j], ('nr', self.round, j))
        self.recs_hist = getattr(self, 'recs_hist', []); self.recs_hist.append(recs)
        log('   round %d done %.0fs; new pieces %d; max gain over old envelope %.5f; L_1/2(1) old %.9f new %.9f' % (
            self.round, time.time() - t0, len(recs), np.nanmax(gain), L[jh, i1], newv[jh, i1]))
        self.round += 1
        return root
