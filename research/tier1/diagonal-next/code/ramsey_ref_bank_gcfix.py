"""Referee rerun (19 Nov 2026): realisable bank model (dp2.Model2) with every control at the CORRECTED a_GC
(ramsey_ref_agc_fix.py output), as ramsey_levers2.py experiments 'gc' / 'gcc'. FLOAT. Writes nothing.
usage: python3 ramsey_ref_bank_gcfix.py agcfix.npz gc|gcc [rounds] [dl] [smax]"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from dp import LWf, load_table
from dp2 import Model2
path, exp = sys.argv[1], sys.argv[2]
R = int(sys.argv[3]) if len(sys.argv) > 3 else 40
dl = float(sys.argv[4]) if len(sys.argv) > 4 else 0.02
smax = float(sys.argv[5]) if len(sys.argv) > 5 else 20.0
PP, MU, W, a = load_table(mustep=4, wstep=4)
t = np.load(path)
a = t['agc'] if exp == 'gc' else np.where(np.isfinite(a), t['agc'], a)
m = Model2(PP, MU, W, a, LWf().fhat, dl=dl, nG=200, smax=smax)
t0 = time.time()
log = lambda s: print('%s-fixed [%5.0fs] %s' % (exp, time.time() - t0, s), flush=True)
hist = m.run(R, log=log)
log('FINAL %s (corrected a_GC) z = %.7f  e^z = %.5f' % (exp, hist[-1], np.exp(hist[-1])))
