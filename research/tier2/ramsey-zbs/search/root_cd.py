"""Second claim (assuming Theorem A): re-optimise the ROOT route of a gen2 state with its control fixed at the exact
(mu, w) of the ZBS-only root and x = x_D (Lemma D target, CD list), everything else unchanged.  Writes the state with
last_root replaced (record key 'cd_x' = x_D).  usage: python3 root_cd.py state.pkl out.pkl x_D"""
import sys, math, json, pickle      # pickle: our own local model state
from fractions import Fraction as Fr
import numpy as np
import root_refine as RR

g = pickle.load(open(sys.argv[1], 'rb'))
xD = sys.argv[3]
root = g.last_root
if len(sys.argv) > 4:
    # pin the root's (mu, w) to a STORED Lemma D certificate's control (needed when the generator was rerun and the
    # refined root moved): the route is re-optimised with exactly that control
    sc = json.load(open(sys.argv[4]))['control']
    assert Fr(sc['x']) == Fr(xD)
    root = dict(root); root['custom'] = (float(Fr(sc['mu'])), float(Fr(sc['w'])), root.get('custom', (0, 0, -math.log(float(Fr(xD)))))[2]); g.last_root = root
mu0, w0, a0 = root['custom']
aD = -math.log(float(Fr(xD)))
RR.xcert = lambda p, m, w: np.full(np.shape(m), float(Fr(xD)))       # the only candidate is the fixed (mu0, w0)
rec = RR.refine(g, rounds=1, span_mu=0.0, span_w=0.0, n=1)
assert abs(rec['custom'][0] - mu0) < 1e-15 and abs(rec['custom'][1] - w0) < 1e-15
rec['cd_x'] = xD
print('root: ZBS-only control a %.9f -> Lemma D target a %.9f (x_D %s); root value %.9f -> %.9f' % (
    a0, aD, xD, root['vals'][-1], rec['vals'][-1]))
g.last_root = rec
pickle.dump(g, open(sys.argv[2], 'wb'))
