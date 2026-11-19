"""Float screen (proves nothing): Lemma D's robust two-region bound (float_lemmaD.Bound, point boxes over the feasible
(Phi_b, p_b) region) for bank controls; finds the largest a-shift da at which the float max U is still negative.
Usage: python3 screenD.py controls.tsv name1,name2,... [ubs]   (tsv columns: control ... p mu w x; beta = 1 - 1e-7)"""
import sys
import numpy as np
from fractions import Fraction as Fr

sys.path.insert(0, __file__.rsplit('/', 1)[0])
import float_lemmaD as FL   # noqa: E402


def maxU(c, ub, nq):
    F = FL.Fn(c, nq=nq)
    B = FL.Bound(F, ub); w = F.w; gb = B.gs(ub); pbs = B.fs(ub)
    best = B.U(gb, gb, pbs, pbs)
    for mbr in np.concatenate([[0], np.geomspace(1e-5, 0.999, 30)]):
        Ph = gb * (1 - mbr)
        lo = max(-w, -Ph / (1 - ub)); hi = Ph / ub
        for pb in np.concatenate([np.linspace(lo, hi, 40), pbs + np.array([-0.3, -0.1, -0.03, -0.01, 0, 0.01, 0.03])]):
            if pb < lo or pb > hi: continue
            best = max(best, B.U(Ph, Ph, pb, pb))
    return best


def threshold(ctl, ub, nq=100001, hi=8e-4, it=9):
    """largest da in [0, hi] (bisection) with float max U < 0 at x e^{da}; 0 if even da = 0 fails."""
    def ok(da):
        c = dict(ctl); c['x'] = ctl['x'] * np.exp(da)
        return maxU(c, ub, nq) < 0
    if not ok(1e-6): return 0.0
    lo = 1e-6
    if ok(hi): return hi
    for _ in range(it):
        m = 0.5 * (lo + hi)
        if ok(m): lo = m
        else: hi = m
    return lo


if __name__ == '__main__':
    rows = {}
    for line in open(sys.argv[1]):
        f = line.rstrip('\n').split('\t')
        if f[0] == 'control': hdr = f; continue
        rows[f[0]] = dict(zip(hdr, f))
    names = sys.argv[2].split(',')
    ubs = [float(s) for s in (sys.argv[3].split(',') if len(sys.argv) > 3 else ['0.02', '0.03', '0.045', '0.07'])]
    for nm in names:
        r = rows[nm]
        ctl = dict(p=float(Fr(r['p'])), mu=float(Fr(r['mu'])), w=float(Fr(r['w'])), beta=1 - 1e-7, x=float(Fr(r['x'])))
        res = []
        for ub in ubs:
            res.append((threshold(ctl, ub), ub))
        best = max(res)
        print('%-6s uses %-3s a %s  thresholds %s  -> best da %.2e at u_b %.3f'
              % (nm, r['uses_at_min_depth'], r['a=-log x'], ' '.join('%.3f:%.2e' % (u, t) for t, u in res), best[0], best[1]),
              flush=True)
