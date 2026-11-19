"""Float gate (exploration; proves nothing): REGION-DEPENDENT multipliers for the two-region Lemma D' bound.

Branch and bound over boxes of anchor values lo_a <= Phi(v_a) <= hi_a (a few key scales). In a box, ONE cut (chain-LP
duals fitted at the box's current worst vertex, cutq_float.Gate.lp) and the tangent of IL at its Q give the separable
convex bound f (dp_gate.DPGate); its EXACT max over the box is a longest-path DP over the box polytope's vertices:
piecewise-linear Phi with kinks only at grid points on g or at anchor nodes (v_a, lo_a) / (v_a, hi_a); chords
passing an anchor scale must stay in [lo_a, hi_a]; at an anchor node below g concavity is enforced (incoming slope >=
outgoing slope); at nodes on g it is automatic. A box closes when the exact max is < 0 (refit up to R times at the
maximising vertex, then split the anchor with the largest relative width).
Usage: python3 region_bb.py control.json nchain da anchors(comma) [max_boxes] [refits]"""
import sys
import time
import numpy as np

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from cutq_float import Gate   # noqa: E402
from dp_gate import DPGate     # noqa: E402


class RegionBB:
    def __init__(self, G, anchors):
        self.G = G; self.D = DPGate(G)
        self.A = [int(np.argmin(np.abs(G.v - a))) for a in anchors]
        assert all(G.b < a < G.n - 1 for a in self.A)
        v, gv = G.v, G.gv
        chord = gv[G.b] + (0 - gv[G.b]) * (v - v[G.b]) / (1 - v[G.b])       # least concave Phi with these ends
        self.root = [(chord[a], gv[a]) for a in self.A]

    def fdict(self, cut):
        self.D.fs = []; self.D.add_f(cut); return self.D.fs[0]

    def dp(self, f, box):
        G = self.G; v, gv, b, n = G.v, G.gv, G.b, G.n
        lo = {a: bx[0] for a, bx in zip(self.A, box)}; hi = {a: bx[1] for a, bx in zip(self.A, box)}
        # nodes: (x index, Phi value, is_anchor)
        nodes = []
        for k in range(b, n):
            if k in lo:
                if lo[k] <= gv[k] <= hi[k] + 1e-15: nodes.append((k, gv[k], False))
                nodes.append((k, lo[k], True))
                if hi[k] < gv[k] - 1e-15: nodes.append((k, hi[k], True))
            else:
                nodes.append((k, gv[k], False))
        N = len(nodes); X = np.array([t[0] for t in nodes]); Yv = np.array([t[1] for t in nodes])
        isA = np.array([t[2] for t in nodes])
        best = np.full(N, -np.inf); best[0] = 0.0; pred = [None] * N
        inrec = [[] for _ in range(N)]                 # anchor nodes: (slope_in, value, pred)
        Aidx = np.array(self.A)
        for i in range(N):
            if X[i] == n - 1: continue
            if isA[i]:
                if not inrec[i]: continue
                rec = sorted(inrec[i], key=lambda r: -r[0])        # descending slope_in
                sl = np.array([r[0] for r in rec]); vals = np.array([r[1] for r in rec])
                pm = np.maximum.accumulate(vals); parg = [0]
                for t in range(1, len(vals)): parg.append(t if vals[t] > vals[parg[-1]] else parg[-1])
            elif not np.isfinite(best[i]):
                continue
            ends = np.where(X > X[i])[0]
            if len(ends) == 0: continue
            s = (Yv[ends] - Yv[i]) / (v[X[ends]] - v[X[i]])
            ok = np.ones(len(ends), dtype=bool)
            for a in self.A:                           # pass-through anchors strictly inside
                inside = (X[i] < a) & (X[ends] > a)
                if inside.any():
                    val_a = Yv[i] + s * (v[a] - v[X[i]])
                    ok &= ~inside | ((val_a >= lo[a] - 1e-15) & (val_a <= hi[a] + 1e-15))
            if not ok.any(): continue
            ends, s = ends[ok], s[ok]
            cells = np.arange(X[i] + 1, n)             # cell k spans (v_{k-1}, v_k]
            jj = cells - (b + 1)
            P = self.D.psi(f, jj[:, None], s[None, :])
            cs = np.cumsum(P, axis=0)
            val = cs[X[ends] - (X[i] + 1), np.arange(len(ends))]
            if isA[i]:
                # start value for each edge: max over incoming with slope_in >= s_out
                pos = np.searchsorted(-sl, -s, side='right') - 1    # last index with sl >= s
                base = np.where(pos >= 0, pm[np.maximum(pos, 0)], -np.inf)
                parg_e = [rec[parg[p]][2] if p >= 0 else None for p in pos]
            else:
                base = np.full(len(ends), best[i]); parg_e = [None] * len(ends)
            tot = base + val
            for e, j in enumerate(ends):
                if not np.isfinite(tot[e]): continue
                src = (i, parg_e[e])
                if isA[j]:
                    inrec[j].append((s[e], tot[e], src))
                if tot[e] > best[j]:
                    best[j] = tot[e]; pred[j] = src
        end = N - 1
        if not np.isfinite(best[end]): return -np.inf, None
        # backtrack (anchor predecessors carry their own best incoming record)
        path = [end]; cur = end
        while cur != 0:
            i, sub = pred[cur] if not isA[cur] else pred[cur]
            path.append(i); cur = i
            if isA[i] and sub is not None:
                pred[i] = sub
        path = path[::-1]
        Phi = gv.copy()
        for p, q in zip(path[:-1], path[1:]):
            k0, k1 = X[p], X[q]
            Phi[k0:k1 + 1] = Yv[p] + (Yv[q] - Yv[p]) * (v[k0:k1 + 1] - v[k0]) / (v[k1] - v[k0])
        m = gv - Phi; m[:b + 1] = 0
        return best[end] + f['const'], m

    def run(self, max_boxes=400, refits=3, log=print):
        G = self.G; t0 = time.time()
        _, cut0 = G.lp(np.zeros(G.n))
        stack = [(self.root, cut0, 0)]; closed = 0; opened = 0; worst_closed = -np.inf
        while stack:
            box, cut, depth = stack.pop()
            opened += 1
            if opened > max_boxes:
                log('   budget of %d boxes exhausted: %d closed, %d still open' % (max_boxes, closed, len(stack) + 1))
                return False, closed, opened
            val = None
            for r in range(refits + 1):
                val, m = self.dp(self.fdict(cut), box)
                if m is None or val < 0: break
                if r < refits:
                    _, cut = G.lp(np.maximum(m, 0))
            if m is None or val < 0:
                closed += 1; worst_closed = max(worst_closed, val if m is not None else -np.inf)
                continue
            # split the anchor with the largest relative width
            wid = [(hi - lo) / (self.root[k][1] - self.root[k][0]) for k, (lo, hi) in enumerate(box)]
            k = int(np.argmax(wid)); lo, hi = box[k]; mid = 0.5 * (lo + hi)
            for half in ((lo, mid), (mid, hi)):
                nb = list(box); nb[k] = half; stack.append((nb, cut, depth + 1))
            if opened % 20 == 0:
                log('   %d boxes opened, %d closed, %d open, depth %d, last max %.2e (%.0fs)'
                    % (opened, closed, len(stack), depth, val, time.time() - t0))
        log('   ALL BOXES CLOSED: %d boxes opened, %d leaves, worst leaf max %.3e (%.0fs)'
            % (opened, closed, worst_closed, time.time() - t0))
        return True, closed, opened


if __name__ == '__main__':
    import json
    from fractions import Fraction as Fr
    ctl = {k: float(Fr(s)) for k, s in json.load(open(sys.argv[1])).items()}
    nchain = int(sys.argv[2]); da = float(sys.argv[3]); anchors = [float(s) for s in sys.argv[4].split(',')]
    maxb = int(sys.argv[5]) if len(sys.argv) > 5 else 400
    ref = int(sys.argv[6]) if len(sys.argv) > 6 else 3
    c = dict(ctl); c['x'] = ctl['x'] * np.exp(da)
    G = Gate(c, nchain)
    R = RegionBB(G, anchors)
    print('da %.1e chain %d anchors %s: saturated V %.3e' % (da, nchain, [round(G.v[a], 4) for a in R.A],
                                                             G.Vtrue(np.zeros(G.n))), flush=True)
    R.run(maxb, ref, log=lambda s: print(s, flush=True))
