"""Second claim, CD-bank form (certCD3): continue a saved generator state for N rounds with the control table lowered
at Lemma D controls, then a root_only round.  The lowered table: the cdmap entries at -log x' + 1e-12 (stored
certificates) and the root-density row (p = 1/2) lowered by the designer's float shift map at 0.92 x
(ramsey-lemma cert/certs/SHIFT_MAP_root.tsv, eadc4b15a: float(mu) = 3.13e-4 + 1.41e-3 (mu - 0.40273)); every control
the certificate finally uses at a lowered entry must carry a stored Lemma D certificate (materialise asserts it) or is
backed off to Lemma C.  usage: python3 cd_rounds.py state.pkl cdmap.json N out.pkl"""
import sys, json, math, pickle      # pickle: our own local model state
import numpy as np
from fractions import Fraction as Fr
EX = np.array([0, 0.001, 0.002, 0.004, 0.007, 0.01, 0.015, 0.02, 0.03, 0.045, 0.06, 0.08, 0.1, 0.13, 0.17, 0.22, 0.3, 0.4, 0.5, 0.6])
g = pickle.load(open(sys.argv[1], 'rb')); m = json.load(open(sys.argv[2])); N = int(sys.argv[3])
# a state saved after run_gen2's final root_only round carries one extra history entry (E_hist, Bown_hist, Uhist, a
# duplicate of the next round's); drop it so that history index = round index (materialise's cone needs that)
if len(g.E_hist) == g.round + 1:
    for h in ('E_hist', 'Bown_hist', 'Uhist'): getattr(g, h).pop()
assert len(g.E_hist) == len(g.Bown_hist) == len(g.Uhist) == g.round == len(g.recs_hist)
jh = int(np.argmin(abs(g.PP - 0.5)))
for e in m:
    new = -math.log(float(Fr(e['x']))) + 1e-12
    if int(e['j']) == jh: continue          # the root row is lowered by the shift map below (its certificates are >= it)
    assert new < g.acl[e['j'], e['imu'], e['iw']]; g.acl[e['j'], e['imu'], e['iw']] = new
shift = lambda mu: 0.92 * (3.13e-4 + 1.41e-3 * (mu - 0.40273))
for imu in range(len(g.MU)): g.acl[jh, imu, :] -= shift(g.MU[imu])
log = lambda s: print(s, flush=True)
for r in range(N): g.run_round(EX, log=log)
g.run_round(EX, log=log, root_only=True)
pickle.dump(g, open(sys.argv[4], 'wb'))
