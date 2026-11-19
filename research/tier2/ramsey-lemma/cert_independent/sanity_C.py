#!/usr/bin/env python3
"""sanity_C: brute-force cross-checks of checkD_C's ingredients on one certificate (not part of acceptance).

1. Hhat+(y) >= Ht(q) - q y at dense sample points q in [q_1, mu] (heights really majorise), and the gap.
2. Psi+_{j0}(y) >= Ht(q) - q y for q >= q_j0 (for a few j0).
3. |Ht''(q)| <= d2_i at sample points of cells i >= jA0, and the gap max d2 / max sampled.
4. Ht'(q_j) from the jets vs the difference quotient of H (different code path: values only).
5. Hull integral: telescoped formula vs piece-by-piece sum, and vs a midpoint rule.
6. Concavity of H (Lemma C (iii), which K5 relies on): Ht'' < 0 enclosure on cells i >= 1.
7. Branch census: nodes with A > B certified / A <= B certified / uncertain.
"""
import os
import sys
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import checkD_C as C  # noqa: E402


def main():
    path = sys.argv[1]
    cert = C.load_cert(path)
    lines = []
    ch = C.Checker(cert, log=lines.append)
    ok = ch.data_checks()
    print('data checks', ok)
    M, q, N, w = ch.M, ch.q, ch.N, cert['w']
    bad = 0
    # 7. branch census
    cen = {'bind': 0, 'free': 0, 'both': 0}
    for j in range(1, N + 1):
        AmB = M.branches(C.IV.of(q[j]), 0)[0]
        cen['bind' if AmB.lo > 0 else 'free' if AmB.hi <= 0 else 'both'] += 1
    print('7. branch census at nodes:', cen)
    # 1. Hhat+ dominance at samples
    ys = [-w, cert['y_c'], Fr(-1, 10), Fr(0), Fr(1, 2), Fr(1), Fr(115, 100), Fr(14, 10), Fr(16, 10)]
    samples = []
    for i in range(1, N):
        for k in (1, 2, 3):
            samples.append(q[i] + (q[i + 1] - q[i]) * k / 4)
    samples += q[1:]
    vals = []
    for s in samples:
        H, _ = M.node(s)
        vals.append((s, H - w * C.IV.of(s)))           # Ht enclosure
    for y in ys:
        Hh = ch.env_at_y(ch.full, y)
        best = max((Ht - C.IV.of(s) * y).hif() for s, Ht in vals)
        gap = Hh - best
        if gap < 0:
            bad += 1
        print('1. y=%-10s Hhat+=%s  max sampled=%s  gap=%s %s' % (C.dec(y, 4), C.dec(Hh, 10), C.dec(best, 10), C.dec(gap, 4),
                                                              'OK' if gap >= 0 else 'VIOLATION'))
    # 2. Psi+ for a few j0
    for j0 in (1, N // 3, N // 2, (2 * N) // 3):
        psi = ch.psi_hull(j0)
        for y in ys[::2]:
            Ps = ch.env_at_y(psi, y)
            best = max((Ht - C.IV.of(s) * y).hif() for s, Ht in vals if s >= q[j0])
            if Ps < best:
                bad += 1
                print('2. VIOLATION j0=%d y=%s' % (j0, C.dec(y)))
    print('2. Psi+ dominance checked for 4 values of j0')
    # 3. d2 vs sampled |Ht''|
    mx_s = Fr(0)
    for i in range(cert['jA0'], N):
        for k in (0, 1, 2, 3, 4):
            s = q[i] + (q[i + 1] - q[i]) * k / 4
            for J in M.active(C.IV.of(s), 2):
                v = J.deriv(2).absmax()
                mx_s = max(mx_s, v)
                if v > ch.d2[i]:
                    bad += 1
                    print('3. VIOLATION cell %d' % i)
    print('3. max d2 bound %s vs max sampled |Ht\'\'| %s (ratio - 1 = %s)' % (
        C.dec(ch.d2suf[cert['jA0']], 10), C.dec(mx_s, 10), C.dec(ch.d2suf[cert['jA0']] / mx_s - 1, 4)))
    # 4. derivative check by values
    hh = Fr(1, 10 ** 24)
    worst = Fr(0)
    for j in range(2, N, max(1, N // 40)):
        Hp_, _ = M.node(q[j] + hh)
        Hm_, _ = M.node(q[j] - hh)
        dq = (Hp_ - Hm_) / (2 * hh)
        der = ch.Htpn[j] + w
        diff = abs(dq.lof() - der.lof())
        worst = max(worst, diff)
    print('4. max |H\' (jets) - difference quotient| = %s' % C.dec(worst, 4))
    if worst > Fr(1, 10 ** 20):
        bad += 1
    # 5. hull integral: telescoped vs piece sum vs midpoint rule, on [u_b, 1]
    hull = ch.full
    ta, tb = cert['u_b'], Fr(1)
    tel = hull.integral_up(ta, tb)
    sa = C.ilog(ta).lof()
    ra = hull.piece(sa)
    tot = C.ZERO
    tcur = C.IV.of(ta)
    scur = C.ilog(ta)
    r = ra
    while True:
        nb = hull.bps[r] if r < len(hull.bps) else None
        if nb is None or nb >= 0:
            tend, send = C.IV.of(tb), C.ZERO
        else:
            tend, send = C.iexp(C.IV.of(nb)), C.IV.of(nb)
        c, d = hull.c[r], hull.d[r]
        tot = tot + (tend * (send * d + c - d)) - (tcur * (scur * d + c - d))
        if nb is None or nb >= 0:
            break
        tcur, scur, r = tend, send, r + 1
    print('5. IRs telescoped %s, piece sum %s, diff %s' % (C.dec(tel, 14), C.dec(tot.hif(), 14), C.dec(tel - tot.hif(), 3)))
    if abs(tel - tot.hif()) > Fr(1, 10 ** 50):
        bad += 1
    n = 4000
    mid = Fr(0)
    for k in range(n):
        t = ta + (tb - ta) * (2 * k + 1) / (2 * n)
        mid += hull.value(C.ilog(t).lof()) * (tb - ta) / n
    print('5. midpoint rule (n=%d) %s, diff %s' % (n, C.dec(mid, 10), C.dec(tel - mid, 3)))
    if abs(tel - mid) > Fr(1, 10 ** 6):
        bad += 1
    # 6. concavity of H on cells i >= 1 (Ht'' upper bound < 0), subdividing cells if needed
    nonconc = 0
    maxH2 = None
    for i in range(1, N):
        pieces = [(q[i], q[i + 1])]
        okc = False
        for depth in range(6):
            nxt = []
            okc = True
            for (a, b) in pieces:
                cell = C.IV(C.IV.of(a).lo, C.IV.of(b).hi)
                try:
                    js = M.active(cell, 2)
                    hi = max(J.deriv(2).hif() for J in js)
                except ArithmeticError:
                    hi = None
                if hi is None or hi >= 0:
                    okc = False
                    m = (a + b) / 2
                    nxt += [(a, m), (m, b)]
                else:
                    maxH2 = hi if maxH2 is None else max(maxH2, hi)
            if okc:
                break
            pieces = nxt
        if not okc:
            nonconc += 1
            if nonconc <= 5:
                print('6. cell %d: concavity not certified after subdivision' % i)
    print('6. cells 1..N-1 with Ht\'\' < 0 certified: %d of %d (max upper bound of Ht\'\' %s)' % (
        N - 1 - nonconc, N - 1, C.dec(maxH2) if maxH2 is not None else 'n/a'))
    print('sanity_C: %s' % ('PASS' if bad == 0 else '%d PROBLEMS' % bad))
    return 0 if bad == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
