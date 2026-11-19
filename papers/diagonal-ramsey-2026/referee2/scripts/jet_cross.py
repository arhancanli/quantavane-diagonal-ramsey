import sys, json
sys.path.insert(0, 'research/tier2/ramsey-zbs/code/lemmaD')
sys.path.insert(1, 'research/tier2/ramsey-lemma/cert_independent')
from fractions import Fraction as F
import checkD_A as DA, checkD_B as DB, checkD_C as DC
from flint import arb, fmpq
cert = json.load(open(sys.argv[1]))
c = cert['control']; p, mu, w, beta, x = (F(c[k]) for k in ('p', 'mu', 'w', 'beta', 'x'))
A = DA.Ctl(p, mu, w, beta, x)
B = DB.Ctl(*(DB.Q(c[k]) for k in ('p', 'mu', 'w', 'beta', 'x')))
M = DC.Model(p, mu, w, beta, x)
qs = [F(t) for t in cert['qgrid']]
idx = sorted(set([1, 2, 3, 10, 50, len(qs) // 3, len(qs) // 2, len(qs) - 2, len(qs) - 1]))
def ov(alo, ahi, blo, bhi): return not (ahi < blo or bhi < alo)
bad = 0
for j in idx:
    q = qs[j]
    a = A.jet(q)                                   # Ht, Ht', Ht''
    b = B.jet(arb(fmpq(q.numerator, q.denominator)))   # H, H', H''
    js = M.active(DC.IV.of(q), 2)
    for k in range(3):
        alo, ahi = DA.lo(a[k]), DA.hi(a[k])
        bb = b[k] - (arb(fmpq(w.numerator, w.denominator)) * (arb(fmpq(q.numerator, q.denominator)) if k == 0 else 1) if k < 2 else 0)
        blo, bhi = (lambda u, v: (F(int(u.p), int(u.q)), F(int(v.p), int(v.q))))(DB.lo_q(bb, 2**200), DB.ub_q(bb, 2**200))
        cc = None
        for J in js:
            v = J.deriv(k); cc = v if cc is None else cc.hull(v)
        clo, chi = cc.lof(), cc.hif()
        ok = ov(alo, ahi, blo, bhi) and ov(alo, ahi, clo, chi) and ov(blo, bhi, clo, chi)
        if not ok: bad += 1
        if k == 2 or not ok: print(j, 'k', k, 'A', float(alo), 'B', float(blo), 'C', float(clo), 'overlap', ok)
print('bad', bad)
