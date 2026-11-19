import sys, json, copy
sys.path.insert(0, 'research/tier2/ramsey-zbs/code/checkA')
from fractions import Fraction as F
import ctlA
cert = json.load(open(sys.argv[1])); ci = int(sys.argv[2])
c = cert['controls'][ci]
ok, tot = ctlA.check_control(c); print('untampered hinge bound', float(tot))
def fs(x): return '%d/%d' % (x.numerator, x.denominator)
for f in [F(1, 10**9), F(1, 10**7), F(1, 10**6), F(1, 10**5), F(1, 10**4)]:
    for key in ('x', 'p', 'w'):
        c2 = copy.deepcopy(c)
        c2[key] = fs(F(c[key]) * (1 + f) if key != 'p' else F(c[key]) * (1 + f))
        if key == 'x': c2['lxU'] = fs(F(c['lxU']) + 2 * f)
        try:
            ok, t = ctlA.check_control(c2); r = 'ACCEPTED hinge %.3e' % float(t)
        except Exception as e:
            r = 'refused %s: %s' % (type(e).__name__, str(e)[:60])
        print('%s * (1 + %.0e): %s' % (key, float(f), r), flush=True)
