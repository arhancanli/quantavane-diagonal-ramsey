"""Certifiable control table (ZBS form, Lemma C with N = 512): a = -log xcert(p, mu, w), beta = 1 - 1e-7,
p = P - 1e-6 for profile densities P = j/80 (j = 1..76) and j/160 (odd j, 0.4 <= P <= 0.6); mu log-spaced in [0.01, 0.80]
(96 points); w log-spaced in [1/8, 16] (64 points; EP's custom controls use mu = 1/81, w = 12).  usage: python3 ctltable2.py out.npz [procs]"""
import sys, time, numpy as np
from multiprocessing import Pool
from ctlvec import xcert
PP = sorted(set([j / 80 for j in range(1, 77)] + [j / 160 for j in range(65, 96, 2)]))
MU = np.exp(np.linspace(np.log(0.01), np.log(0.80), 96))
W = np.exp(np.linspace(np.log(0.125), np.log(16.0), 64))


def row(P):
    m, w = np.meshgrid(MU, W, indexing='ij')
    x = xcert(np.full(m.size, P - 1e-6), m.ravel(), w.ravel())
    with np.errstate(invalid='ignore'):
        return -np.log(x).reshape(m.shape)


if __name__ == '__main__':
    t0 = time.time(); print('START', time.ctime(), flush=True)
    with Pool(int(sys.argv[2]) if len(sys.argv) > 2 else 4) as pool:
        out = []
        for i, r in enumerate(pool.imap(row, PP)):
            out.append(r); print('P %.5f done %.0fs' % (PP[i], time.time() - t0), flush=True)
    np.savez(sys.argv[1], PP=np.array(PP), P=np.array(PP) - 1e-6, MU=MU, W=W, a=np.array(out))
    print('END', time.ctime(), flush=True)
