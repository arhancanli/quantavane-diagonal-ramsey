import json, sys, math
from fractions import Fraction as Fr
exec(open("vafloat.py").read().split("# a(0): left root")[0].replace("fn = sys.argv[1]", "fn = sys.argv[1]"))
lo, hi = 1e-12, mu
for _ in range(200):
    m = 0.5*(lo+hi)
    if G0(m) >= 0: lo = m
    else: hi = m
a0 = hi
qs = [a0 + (mu - a0)*i/20000 for i in range(1, 20001)]
best = max((Ht(q), q) for q in qs)
print(fn.split('/')[-1], "max_{q in F} Ht(q) = %.6e at q=%.6f ; a0=%.6f mu=%.6f" % (best[0], best[1], a0, mu))
