"""Compare ivA (checker A) and checkD_C interval exp/log against Arb at 2000 bits on adversarial rationals."""
import sys, random
sys.path.insert(0, 'research/tier2/ramsey-zbs/code/checkA')
sys.path.insert(1, 'research/tier2/ramsey-lemma/cert_independent')
from fractions import Fraction as F
import flint
from flint import arb, fmpq
flint.ctx.prec = 2000
import ivA, checkD_C as C
rng = random.Random(7)
def contains(lo, hi, ref):          # ref an arb (tight); require lo <= ref <= hi certainly
    return arb(fmpq(lo.numerator, lo.denominator)) <= ref and ref <= arb(fmpq(hi.numerator, hi.denominator))
bad = 0; n = 0
vals = []
for _ in range(3000):
    a = rng.choice([1, 2, 3, 7, 10**6, 10**12, 2**60, 3**40]); b = rng.choice([1, 2, 3, 7, 10**6 + 1, 10**15, 2**61 + 1, 5**30])
    v = F(rng.randint(1, a * 10), rng.randint(1, b))
    vals.append(v)
vals += [F(1), F(2), F(1, 2), F(2**256 - 1, 2**256), F(2**256 + 1, 2**256), F(1, 2**200), F(2**300), F(3, 1) , F(10**-0 + 0)]
for v in vals:
    ref_log = arb(fmpq(v.numerator, v.denominator)).log()
    l = ivA.log(v); n += 1
    if not contains(l.lof(), l.hif(), ref_log): bad += 1; print('ivA log fails at', v)
    lc = C.ilog(C.IV.of(v))
    if not contains(lc.lof(), lc.hif(), ref_log): bad += 1; print('C log fails at', v)
for _ in range(2000):
    t = F(rng.randint(-60 * 10**9, 60 * 10**9), rng.choice([10**9, 3**19, 2**40 + 1, 7]))
    if abs(t) > 150: continue
    ref = arb(fmpq(t.numerator, t.denominator)).exp()
    e = ivA.exp(t); n += 1
    if not contains(e.lof(), e.hif(), ref): bad += 1; print('ivA exp fails at', t)
    ec = C.iexp(C.IV.of(t))
    if not contains(ec.lof(), ec.hif(), ref): bad += 1; print('C exp fails at', t)
for t in [F(-199), F(-201), F(-1000), F(1, 2**300), F(-1, 2**300), F(200), F(37, 2)]:
    ref = arb(fmpq(t.numerator, t.denominator)).exp()
    ec = C.iexp(C.IV.of(t)); e = ivA.exp(t)
    print('t', float(t), 'C ok', contains(ec.lof(), ec.hif(), ref), 'A ok', contains(e.lof(), e.hif(), ref))
print('tested', n, 'bad', bad)
