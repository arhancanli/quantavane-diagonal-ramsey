"""Lever experiments on the REALISABLE float bank model (dp2.py).  EXPLORATION ONLY.
usage: python3 ramsey_levers2.py <experiment> [rounds] [mustep] [wstep] [dl] [nG]"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from dp import LWf, load_table, es_hat
from dp2 import Model2

exp = sys.argv[1]
R = int(sys.argv[2]) if len(sys.argv) > 2 else 40
ms = int(sys.argv[3]) if len(sys.argv) > 3 else 4
ws = int(sys.argv[4]) if len(sys.argv) > 4 else 4
dl = float(sys.argv[5]) if len(sys.argv) > 5 else 0.01
nG = int(sys.argv[6]) if len(sys.argv) > 6 else 200
smax = float(sys.argv[7]) if len(sys.argv) > 7 else 5.0
PP, MU, W, a = load_table(mustep=ms, wstep=ws)
P3 = (PP - 1e-6)[:, None, None]; MU3 = MU[None, :, None]; W3 = W[None, None, :]
a_cap = -np.log(np.minimum(P3, (1 - MU3) ** W3))          # Theorem 3.4's hypothesis x < min{p, (1-mu)^w}
a_rand = -np.log(P3 * (1 - MU3) ** W3)                     # red step of a quasi-random host at q = mu
lw = LWf()
fh = lw.fhat
kw = {}
if exp == 'base':
    pass
elif exp.startswith('shift'):                              # shift0.01: every certifiable a lowered by 0.01
    a = np.maximum(a - float(exp[5:]), a_cap + 1e-9)
elif exp.startswith('band'):                               # band0.03_0.45_0.55: shift only for p in [lo, hi]
    dd, lo, hi = (float(v) for v in exp[4:].split('_'))
    sel = ((PP >= lo - 1e-9) & (PP <= hi + 1e-9))[:, None, None]
    a = np.where(sel, np.maximum(a - dd, a_cap + 1e-9), a)
elif exp.startswith('mband') or exp.startswith('wband'):   # mband0.03_0.3_0.5: shift only for mu (or w) in [lo, hi]
    dd, lo, hi = (float(v) for v in exp[5:].split('_'))
    ax = MU3 if exp[0] == 'm' else W3
    sel = (ax >= lo - 1e-9) & (ax <= hi + 1e-9)
    a = np.where(sel, np.maximum(a - dd, a_cap + 1e-9), a)
elif exp.startswith('half'):                               # half: a -> (a + a_rand)/2 only where certified
    a = np.where(np.isfinite(a), 0.5 * (a + a_rand), a)
elif exp.startswith('mix'):                                # mix0.5: a -> a - th (a - a_rand); uncertified cells filled
    th = float(exp[3:]); afill = np.where(np.isfinite(a), a, a_rand + 0.5)
    a = afill - th * (afill - a_rand)
elif exp in ('sym', 'symc'):                              # symmetric-split adversary value (ramsey_asym_table.py)
    t = np.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs', 'asym_m%dw%d.npz' % (ms, ws)))
    a = t['asym'] if exp == 'sym' else np.where(np.isfinite(a), t['asym'], a)
elif exp in ('gc', 'gcc'):                                # Gaussian-cap construction value (ramsey_agc_table.py)
    t = np.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs', 'agc_m%dw%d.npz' % (ms, ws)))
    a = t['agc'] if exp == 'gc' else np.where(np.isfinite(a), t['agc'], a)
elif exp.startswith('gprox'):                            # gprox0.35: a -> a - th (a - a_rand) on certified cells only
    th = float(exp[5:]); a = np.where(np.isfinite(a), a - th * (a - a_rand), a)
elif exp == 'gcert':                                     # Gaussian-gain envelope (ramsey_gcert_table.py), box only
    t = np.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs', 'agcert_m%dw%d.npz' % (ms, ws)))
    a = np.minimum(a, t['agcert'])
elif exp.startswith('wgam'):                             # wgam0.25: weak-GGL envelope table (ramsey_wgam_table.py)
    t = np.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs', 'aw%s_m%dw%d.npz' % (exp[4:].replace('0.', '0'), ms, ws)))
    a = np.minimum(a, t['aw'])
elif exp == 'gcproved':                                  # a_GC on the provable range, a_rand elsewhere
    t = np.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs', 'agcp_m%dw%d.npz' % (ms, ws)))
    a = t['agc']
elif exp == 'rand':
    a = a_rand.copy()
elif exp == 'cap':
    a = a_cap + 1e-6
elif exp.startswith('src'):                                # src0.01: fhat lowered by 0.01 (1 + lam)
    dd = float(exp[3:]); fh = lambda l, f=lw.fhat, dd=dd: f(l) - dd * (1 + np.asarray(l))
elif exp == 'es':
    fh = es_hat
elif exp == 'noroute':
    kw['routes'] = False
elif exp == 'nofeed':
    kw['feedback'] = False
else:
    raise SystemExit('unknown experiment')
m = Model2(PP, MU, W, a, fh, dl=dl, nG=nG, smax=smax, **kw)
t0 = time.time()
log = lambda s: print('%s [%5.0fs] %s' % (exp, time.time() - t0, s), flush=True)
log('grid nP %d nMU %d nW %d nS %d dl %.4f nG %d smax %g' % (len(PP), len(MU), len(W), m.nS, dl, nG, smax))
hist = m.run(R, log=log)
tag = '%s_m%d_w%d_dl%g_s%g' % (exp, ms, ws, dl, smax)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs', 'state2_%s.npz' % tag)
np.savez(out, L=m.L, U=m.U, S=m.S, PP=m.PP, hist=np.array(hist), Ag=m.Ag, Bst=m.Bst, PT=m.PT)
log('FINAL %s z = %.7f  e^z = %.5f' % (exp, hist[-1], np.exp(hist[-1])))
