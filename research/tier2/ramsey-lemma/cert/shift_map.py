"""Float map (proves nothing) of the Lemma D a-shift over candidate root controls, for ramsey-zbs's root refinement.
For each (mu, w) on a grid in log space around (mu0, w0): x = ctlvec.xcert(p, mu, w) (the Lemma C certifiable x the
refinement uses), then the float Lemma D threshold at u_b = 0.03 (screenD.threshold). The certifiable estimate is 0.88 x
the float threshold (all 23 route-tree certificates closed at that ratio).
Usage: python3 shift_map.py p mu0 w0 span_mu span_w n out.tsv"""
import sys
import numpy as np

sys.path.insert(0, __file__.rsplit('/', 1)[0])
sys.path.insert(0, __file__.rsplit('/', 3)[0] + '/ramsey-zbs/search')
import screenD                      # noqa: E402
from ctlvec import xcert            # noqa: E402  (ramsey-zbs, read only)

if __name__ == '__main__':
    p, mu0, w0, smu, sw = (float(s) for s in sys.argv[1:6]); n = int(sys.argv[6]); out = sys.argv[7]
    mus = mu0 * np.exp(np.linspace(-smu, smu, n)); ws = w0 * np.exp(np.linspace(-sw, sw, n))
    mm, ww = np.meshgrid(mus, ws, indexing='ij'); mm, ww = mm.ravel(), ww.ravel()
    xs = xcert(np.full(mm.size, p), mm, ww)
    with open(out, 'w') as f:
        f.write('mu\tw\ta_lemmaC\tlemmaD_float_threshold\tlemmaD_cert_estimate\n')
        for mu, w, x in zip(mm, ww, xs):
            if not np.isfinite(x):
                f.write('%.9f\t%.9f\tnan\tnan\tnan\n' % (mu, w)); continue
            ctl = dict(p=p, mu=mu, w=w, beta=1 - 1e-7, x=x)
            t = screenD.threshold(ctl, 0.03, nq=50001, it=7)
            f.write('%.9f\t%.9f\t%.9f\t%.3e\t%.3e\n' % (mu, w, -np.log(x), t, 0.88 * t)); f.flush()
            print('mu %.6f w %.6f a %.6f  float %.3e  cert~ %.3e' % (mu, w, -np.log(x), t, 0.88 * t), flush=True)
