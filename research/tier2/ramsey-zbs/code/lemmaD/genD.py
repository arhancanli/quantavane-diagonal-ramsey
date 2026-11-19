"""Generator for Lemma D certificates (CERT_DESIGN.md).  Float search for the data, then a branch-and-bound over
(Phi_b, p_b) boxes evaluated with checker A's own rigorous box bound; writes cert JSON with the bisection tree.
Usage: python3 genD.py <control.json|root> <shift da> <u_b> <out.json> [max_depth]
The certificate proves nothing until checkD_A.py and checkD_B.py both accept it."""
import json
import math
import sys
import time
from fractions import Fraction as Fr

import checkD_A as A
import checkD_B
from flint import fmpq

ROOT = dict(p='499999/1000000', mu='80725349867/200000000000', w='120299011257/250000000000',
            beta='9999999/10000000', x='8107422360171/25000000000000')


def fG0(q, p, mu, w, beta, x):
    return q * math.log(p) + beta * (1 - q) * (math.log(p) + w * math.log(1 - q) - math.log(x)) \
        - beta * w * q * (math.log(mu) - math.log(q))


def left_root(p, mu, w, beta, x):
    lo, hi = 1e-9, mu
    for _ in range(200):
        m = 0.5 * (lo + hi)
        if fG0(m, p, mu, w, beta, x) < 0: hi = m
        else: lo = m
    return hi


def rat(x, den=10**15):
    return Fr(round(x * den), den)


def skeleton(ctl, ub, Dplus_inv=10**7):
    p, mu, w, beta, x = (float(Fr(ctl[k])) for k in ('p', 'mu', 'w', 'beta', 'x'))
    a = left_root(p, mu, w, beta, x)
    a_cut, a_hi = rat(a - 2e-12), rat(a + 2e-12)
    qmu = Fr(ctl['mu'])
    # q grid: dense where Ht'' is large (left part), coarser towards mu
    qs = [a_cut, a_hi]
    q = float(a_hi)
    while q < float(qmu):
        f = (q - a) / (float(qmu) - a)
        step = (float(qmu) - a) * (1.2e-3 if f < 0.12 else (4e-4 if f < 0.43 else (9e-4 if f < 0.73 else 2.5e-3)))
        q += step
        if q < float(qmu) - step / 2: qs.append(rat(q, 10**12))
    qs.append(qmu)
    G = A.Ctl(*(Fr(ctl[k]) for k in ('p', 'mu', 'w', 'beta', 'x')))
    wF = Fr(ctl['w'])
    d = G.dG0(a_hi)
    alpha = A.cup(A.hi(A.I(Fr(ctl['beta'])) / (-d)), 10**12)
    _, Ht1, _ = G.jet(qmu)
    yc = A.cup(A.hi(Ht1), 10**12)
    ubF = rat(ub, 10**6)
    n = 10**6
    Dp = (1 - ubF) / n
    gub = -float(wF) * ub * math.log(ub)
    Pup = rat(-float(wF) * math.log(ub) + 1e-9, 10**12)
    jA0 = 1
    for j in range(len(qs) - 1, 0, -1):            # largest node with Ht'(q_j) >= P_up: q_A(p) >= q_jA0 for p <= P_up
        if A.lo(G.jet(qs[j])[1]) >= Pup:
            jA0 = j; break
    cert = dict(control={k: str(Fr(ctl[k])) for k in ('p', 'mu', 'w', 'beta', 'x')},
                a_cut=str(a_cut), a_hi=str(a_hi), alpha=str(alpha), u_b=str(ubF), Dplus=str(Dp),
                qgrid=[str(t) for t in qs], y_c=str(yc), jA0=jA0,
                G_up=str(rat(gub + 1e-9, 10**12)), P_up=str(Pup))
    return cert


def bnb(L, rect, budget, depth_max=40, log=None, LB=None):
    """returns the bisection tree; raises if a box cannot be closed within depth_max."""
    t0 = time.time(); stats = dict(n=0, worst=None)
    def rec(bx, depth):
        U, info = L.box(*bx)
        if U is not None and U < 0 and LB is not None:          # require checker B's bound too
            UB, _ = LB.box(*(fmpq(t.numerator, t.denominator) for t in bx))
            if UB is None or not UB < 0: U, info = None, 'checker B bound not negative'
        stats['n'] += 1
        if stats['n'] % 200 == 0 and log:
            log('  %d boxes, %.0fs, depth %d' % (stats['n'], time.time() - t0, depth))
        if U is not None and U < 0:
            if stats['worst'] is None or U > stats['worst'][0]: stats['worst'] = (U, bx, info)
            return 'L'
        if depth >= depth_max:
            raise RuntimeError('cannot close box %s: %s %s' % ([float(t) for t in bx], U and float(U), info))
        Pl, Ph, pl, ph = bx
        # split the axis with the larger relative width (Phi range ~ g(u_b), p range ~ P_up + w)
        if (Ph - Pl) / (rect[1] - rect[0]) >= (ph - pl) / (rect[3] - rect[2]):
            m = (Pl + Ph) / 2
            return ['P', rec((Pl, m, pl, ph), depth + 1), rec((m, Ph, pl, ph), depth + 1)]
        m = (pl + ph) / 2
        return ['p', rec((Pl, Ph, pl, m), depth + 1), rec((Pl, Ph, m, ph), depth + 1)]
    tree = rec(rect, 0)
    return tree, stats


def certify(ctl, da, ub=0.03, depth=48, log=None):
    """entry point for materialise: ctl = dict of rational strings (p, mu, w, beta, x) of the BANK control; returns
    (x_new as str, lemmaD dict) with x_new = floor(x e^{-da} 10^15)/10^15, or raises RuntimeError if the branch and
    bound cannot close (caller halves da and retries, then falls back to Lemma C)."""
    ctl = dict(ctl)
    if da != 0:
        xf = float(Fr(ctl['x'])) * math.exp(-float(da))
        ctl['x'] = str(Fr(math.floor(xf * 10**15), 10**15))
    cert = skeleton(ctl, ub)
    L = A.LemmaD(cert); LB = checkD_B.LemmaD(cert)
    rect = (Fr(0), Fr(cert['G_up']), -L.w, Fr(cert['P_up']))
    tree, st = bnb(L, rect, None, depth, log, LB)
    cert['tree'] = tree
    lem = {k: v for k, v in cert.items() if k != 'control'}
    return ctl['x'], lem


def build(p, mu, w, beta, x, ub=0.03, depth=48):
    """materialise entry point: the TARGET control (rationals or strings; x already lowered); returns the 'lemmaD'
    dict (both checkers' box bounds negative on every leaf) or None if the branch and bound cannot close."""
    ctl = dict(p=str(Fr(p)), mu=str(Fr(mu)), w=str(Fr(w)), beta=str(Fr(beta)), x=str(Fr(x)))
    try:
        return certify(ctl, 0, ub, depth)[1]
    except (RuntimeError, ArithmeticError, AssertionError):
        return None


if __name__ == '__main__':
    ctl = ROOT if sys.argv[1] == 'root' else json.load(open(sys.argv[1]))
    da = Fr(sys.argv[2]); ub = float(sys.argv[3]); out = sys.argv[4]
    depth = int(sys.argv[5]) if len(sys.argv) > 5 else 40
    ctl = dict(ctl)
    if da != 0:
        # x' = x * exp(-da), rounded DOWN to a rational (larger a = -log x' is conservative only if rounded so that
        # a' >= a_root - |da|: we report a' = -log x' exactly from the rational x')
        xf = float(Fr(ctl['x'])) * math.exp(-float(da))
        ctl['x'] = str(Fr(math.floor(xf * 10**15), 10**15))
    cert = skeleton(ctl, ub)
    log = lambda s: print(s, flush=True)
    t = time.time()
    L = A.LemmaD(cert)
    log('setup %.1fs, %d q-nodes, hull %d lines, IRs = %.6e' % (time.time() - t, len(L.qs), len(L.envall.c), float(L.IRs)))
    w = L.w
    rect = (Fr(0), Fr(cert['G_up']), -w, Fr(cert['P_up']))
    LB = checkD_B.LemmaD(cert)
    tree, st = bnb(L, rect, None, depth, log, LB)
    cert['tree'] = tree
    json.dump(cert, open(out, 'w'))
    U, bx, info = st['worst']
    log('done: %d boxes, worst U = %.6e at %s %s, %.0fs' % (st['n'], float(U), [float(v) for v in bx], info, time.time() - t))
