"""Exploration (proves nothing): realisability of ZBS's extremal configuration when the BLUE test may also use
sub-pairs (T, Y) with T inside a blue neighbourhood (valid by the induction of ZBS Thm 4.2: (I_{n-1}) applies to any
pair whose potential clears the threshold).  In the limit, blue failure at every T in B_v gives (Jensen)
    avg_{j in T} phi_j <= w log(mu / theta_T),   theta_T = |T|/|X|.
Rows in n quantile blocks (phi decreasing in block index); for each block k and prefix L we impose it for
T = B_k cap (blocks <= L) by tangent cuts of the concave function theta log(mu/theta) (cutting planes)."""
import sys
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix, vstack, csr_matrix
from extremal import ROOT, envelope
from realize_lp import block_data


def solve(Qb, Pb, Fb, w, mu, rounds=30, tol=1e-7, verbose=True):
    n = len(Qb)
    pairs = [(k, l) for k in range(n) for l in range(k, n)]
    pid = np.zeros((n, n), int)
    for i, (k, l) in enumerate(pairs): pid[k, l] = pid[l, k] = i
    nv = len(pairs) + 1
    Aeq = lil_matrix((n, nv)); Aub = lil_matrix((n, nv))
    for k in range(n):
        for l in range(n):
            Aeq[k, pid[k, l]] += 1.0 / n; Aub[k, pid[k, l]] += Fb[l] / n
        Aub[k, nv - 1] = -1.0
    Aeq = Aeq.tocsr(); Aub = Aub.tocsr(); bub = Pb.copy()
    cuts_rows, cuts_b = [], []
    cvec = np.zeros(nv); cvec[-1] = 1.0
    bounds = [(0, 1)] * len(pairs) + [(None, None)]
    for it in range(rounds):
        A = Aub if not cuts_rows else vstack([Aub, csr_matrix(np.array(cuts_rows))])
        b = bub if not cuts_b else np.concatenate([bub, np.array(cuts_b)])
        res = linprog(cvec, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=Qb, bounds=bounds, method='highs')
        x = res.x; W = x[pid]
        # find violated cuts
        newc = 0; worst = 0
        for k in range(n):
            th = np.cumsum(W[k]) / n; sm = np.cumsum(W[k] * Fb) / n
            for L in range(n):
                if th[L] < 1e-9: continue
                v = sm[L] - w * th[L] * np.log(mu / th[L])
                worst = max(worst, v)
                if v > tol:
                    t0 = th[L]; row = np.zeros(nv)
                    coef = (Fb[:L + 1] - w * np.log(mu / t0) + w) / n
                    np.add.at(row, pid[k, :L + 1], coef)
                    # constraint: sum_l<=L W_kl (phi_l - w log(mu/t0) + w)/n <= w t0
                    cuts_rows.append(row); cuts_b.append(w * t0); newc += 1
        if verbose: print('  round %d: slack s = %+.6f, worst blue-subpair violation %.2e, new cuts %d' % (
            it, x[-1], worst, newc), flush=True)
        if newc == 0: break
    return x[-1], W


if __name__ == '__main__':
    c = ROOT; e = envelope(c)
    for n in [int(a) for a in sys.argv[1:]] or [20, 40]:
        Qb, Pb, Fb = block_data(c, n, e)
        s, W = solve(Qb, Pb, Fb, c['w'], c['mu'])
        print('n=%d: min uniform slack with blue sub-pair constraints = %+.6f' % (n, s), flush=True)
