"""Driver for gen2 (exploration).  usage: python3 run_gen2.py <zbs_bank.json> <ctltable2.npz> <rounds> <out.pkl> [kp]"""
import sys, pickle, time, numpy as np
from gen2 import Gen
zb, tab, R, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
kp = int(sys.argv[5]) if len(sys.argv) > 5 else 5
EX = np.array([0, 0.001, 0.002, 0.004, 0.007, 0.01, 0.015, 0.02, 0.03, 0.045, 0.06, 0.08, 0.1, 0.13, 0.17, 0.22, 0.3, 0.4, 0.5, 0.6])
print('START', time.ctime(), flush=True)
g = Gen(zb, tab, kp=kp)
for r in range(R):
    g.run_round(EX, log=lambda s: print(s, flush=True))
    with open(out, 'wb') as f: pickle.dump(g, f)
g.run_round(EX, log=lambda s: print(s, flush=True), root_only=True)
with open(out, 'wb') as f: pickle.dump(g, f)
print('END', time.ctime(), flush=True)
