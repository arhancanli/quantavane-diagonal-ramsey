"""Driver for the extended-range generator (float gate; proves nothing).
usage: QV_RMAX=8 ramsey_gen2_ext_run.py zbs_bank.json ctltable2.npz rounds out.pkl kp"""
import sys, os, pickle, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from ramsey_gen2_ext import Gen, NS, RMAX
zb, tab, R, out, kp = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], int(sys.argv[5])
EX = np.array([0, 0.001, 0.002, 0.004, 0.007, 0.01, 0.015, 0.02, 0.03, 0.045, 0.06, 0.08, 0.1, 0.13, 0.17, 0.22, 0.3, 0.4, 0.5, 0.6])
print('START', time.ctime(), 'RMAX', RMAX, 'NS', NS, 'kp', kp, 'rounds', R, flush=True)
g = Gen(zb, tab, kp=kp)
for r in range(R):
    g.run_round(EX, log=lambda s: print(s, flush=True))
    with open(out, 'wb') as f: pickle.dump(g, f)
    print('saved after round', r, time.ctime(), flush=True)
g.run_round(EX, log=lambda s: print(s, flush=True), root_only=True)
with open(out, 'wb') as f: pickle.dump(g, f)
print('END', time.ctime(), flush=True)
