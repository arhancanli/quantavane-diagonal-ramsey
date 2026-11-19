"""FLOAT GATE (exploration; proves nothing): dedicated point-domain roots at off-diagonal ratios vs the generic pair.
Loads a gen2 state (pickle written by the lab's own generator, research/tier2/ramsey-zbs/search). For gamma with
gamma and 1/gamma on the 1/400 grid: generic pair = min_j max(L[j, r(g)], g * min_{j': p_j' <= 1 - p_j} L[j', r(1/g)])
from the state's envelope; dedicated = the same with L replaced by point-root values (gen2.knot(point=True, full=True))
for the buckets in a window around the generic optimum. usage: ramsey_rootgate.py state.pkl g1,g2,...  [window]"""
import sys, time, pickle
sys.path.insert(0, 'research/tier2/ramsey-zbs/search')
import numpy as np
import gen2  # noqa: F401  (class used by the pickle)

EX = np.array([0, 0.001, 0.002, 0.004, 0.007, 0.01, 0.015, 0.02, 0.03, 0.045, 0.06, 0.08, 0.1, 0.13, 0.17, 0.22, 0.3, 0.4, 0.5, 0.6])


def ridx(g, t):
    i = int(round(t * 400)) - 5
    assert abs(g.S[i] - t) < 1e-12, t
    return i


def best_pair(PP, red, blue, gam):
    best = (np.inf, None, None)
    for j in range(1, len(PP)):
        if not np.isfinite(red[j]): continue
        ok = [k for k in range(1, len(PP)) if PP[k] <= 1 - PP[j] + 1e-12 and np.isfinite(blue[k])]
        if not ok: continue
        k = min(ok, key=lambda k: blue[k])
        v = max(red[j], gam * blue[k])
        if v < best[0]: best = (v, j, k)
    return best


def main():
    t0 = time.time()
    g = pickle.load(open(sys.argv[1], 'rb'))
    gams = [float(x) for x in sys.argv[2].split(',')]
    win = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    L = g.envelope()
    print('state loaded %.0fs; round %d; root %.9f' % (time.time() - t0, g.round, g.last_root['vals'][-1]), flush=True)
    for gam in gams:
        r1, r2 = ridx(g, gam), ridx(g, 1 / gam)
        gen = best_pair(g.PP, L[:, r1], L[:, r2], gam)
        _, j0, k0 = gen
        js = {j for j in range(max(1, j0 - win), min(g.nB, j0 + win + 1))}
        ks = {k for k in range(max(1, k0 - win), min(g.nB, k0 + win + 1))}
        t1 = time.time()
        recR = g.knot(r1, EX, L[:, r1], point=True, only=js, full=True)
        recB = g.knot(r2, EX, L[:, r2], point=True, only=ks, full=True)
        red = np.full(g.nB, np.inf); blue = np.full(g.nB, np.inf)
        for rec in recR:
            if rec is not None: red[rec['j']] = rec['vals'][-1]
        for rec in recB:
            if rec is not None: blue[rec['j']] = rec['vals'][-1]
        # dedicated objects may pair with generic ones on the other side
        red = np.minimum(red, L[:, r1]); blue = np.minimum(blue, L[:, r2])
        ded = best_pair(g.PP, red, blue, gam)
        print('g=%.4f generic %.6f (p_R %.4f, p_S %.4f) dedicated %.6f (p_R %.4f, p_S %.4f) gain %.6f  [%.0fs]' % (
            gam, gen[0], g.PP[j0], g.PP[k0], ded[0], g.PP[ded[1]], g.PP[ded[2]], gen[0] - ded[0], time.time() - t1), flush=True)


if __name__ == '__main__':
    main()
