"""Refine the root's control continuously (exploration): local (mu, w) grid around the table optimum with the
certifiable a computed on the spot (ctlvec.xcert, Lemma C form, N = 512), finer extras, the exact frontier evaluation
of gen2 on the final pool.  Writes the improved root record into the state (key 'custom' = (mu, w, a)).
usage: python3 root_refine.py state.pkl out.pkl"""
import sys, pickle      # pickle: our own local model state
import numpy as np
from gen2 import Gen, H
from ctlvec import xcert


def refine(g, rounds=3, span_mu=0.06, span_w=0.09, n=13):
    root = g.last_root
    r = root['r']; l = r - 1; j = root['j']
    L = g.envelope()
    Gs = g.Ggrid(np.where(np.arange(g.nB) == j, L[:, r], np.nan), g.S[r], True)
    Gs = np.unique(np.concatenate([Gs, root.get('G', Gs[0]) + np.linspace(-0.004, 0.004, 801)]))
    gp, jst, sl = g.descent(r, Gs)
    suf = np.minimum.accumulate(sl[:, ::-1], axis=1)[:, ::-1]
    X = gp[:, :l + 1]; Sx = g.S[:l + 1]; rho = g.S[r]
    mu0, w0 = g.MU[root['imu']], g.W[root['iw']]
    if 'custom' in root: mu0, w0 = root['custom'][0], root['custom'][1]
    best = (root['vals'][-1], None)
    EX = np.concatenate([[0], np.geomspace(1e-4, 0.3, 120)])
    for it in range(rounds):
        mus = mu0 * np.exp(np.linspace(-span_mu, span_mu, n)); ws = w0 * np.exp(np.linspace(-span_w, span_w, n))
        mm, ww = np.meshgrid(mus, ws, indexing='ij'); mm, ww = mm.ravel(), ww.ravel()
        a = -np.log(xcert(np.full(mm.size, g.PP[j] - 1e-6), mm, ww))
        for k in range(mm.size):
            if not np.isfinite(a[k]): continue
            c = -np.log(mm[k]) + 1e-9; w = ww[k]; wp = w / (1 + w)
            val = X - Sx[None, :] * c
            t = np.argmax(val, axis=1); M = val[np.arange(len(Gs)), t]
            sig = suf[np.arange(len(Gs)), np.minimum(t + 1, r)]
            ok = np.isfinite(M)
            ap = a[k] + EX; bb = g.Bfun(ap)
            leaf = (ap + rho * (bb + w * c)) / (1 + w)
            Ge = (Gs - sig)[ok]; D = (Gs - M)[ok]
            Vh = np.maximum(Ge[None, :], ((ap + rho * bb) / (1 + w))[:, None] + wp * D[None, :])
            e = np.unravel_index(np.argmin(Vh), Vh.shape)
            cand = [(Vh[e], ('route', mm[k], w, a[k], EX[e[0]], np.nonzero(ok)[0][e[1]]))]
            el = int(np.argmin(leaf)); cand.append((leaf[el], ('leaf', mm[k], w, a[k], EX[el], None)))
            for v, info in cand:
                if v < best[0]: best = (v, info)
        if best[1] is not None: mu0, w0 = best[1][1], best[1][2]
        span_mu /= 3; span_w /= 3
        print('refine iteration %d: best %.9f' % (it, best[0]), flush=True)
    if best[1] is None: return root
    kind, mu, w, a, e, kG = best[1]
    c = -np.log(mu) + 1e-9; ap = a + e; bb = float(g.Bfun(ap))
    rec = dict(root); rec.update(kind=1 if kind == 'route' else 0, a=ap, b=bb, custom=(float(mu), float(w), float(a)))
    if kind == 'route':
        val = X[kG] - Sx * c; t = int(np.argmax(val)); sg = float(suf[kG, min(t + 1, r)])
        gpath = gp[kG, l:r + 1]
        T = (ap + g.S[l:r + 1] * bb + w * (g.S[t] * c + gpath - gp[kG, t])) / (1 + w)
        rec.update(G=float(Gs[kG]), th=t, sigma=sg, vals=np.maximum(gpath - sg, T))
    else:
        rec['vals'] = (ap + g.S[l:r + 1] * (bb + w * c)) / (1 + w)
    return rec


if __name__ == '__main__':
    g = pickle.load(open(sys.argv[1], 'rb'))
    old = g.last_root['vals'][-1]
    # g.E, g.U, g.Bown_hist are those of the final pool (the last run_round(root_only=True) built them)
    rec = refine(g)
    print('root: table controls %.9f -> continuous controls %.9f  (mu %.6f w %.6f a %.7f)' % (old, rec['vals'][-1], *rec['custom']))
    g.last_root = rec
    pickle.dump(g, open(sys.argv[2], 'wb'))
