import sys, json
sys.path.insert(0, 'research/tier2/ramsey-zbs/code/lemmaD')
sys.path.insert(1, 'research/tier2/ramsey-lemma/cert_independent')
from fractions import Fraction as F
import checkD_A as DA, checkD_B as DB, checkD_C as DC
path = sys.argv[1]
cert = json.load(open(path))
LA = DA.LemmaD(cert); LB = DB.LemmaD(cert)
def f(x): return F(int(x.p), int(x.q)) if hasattr(x, 'p') else F(x)
hA = LA.h; hB = [f(t) for t in LB.h]
dh = [hB[j] - hA[j] for j in range(len(hA))]
print('heights B - A: max', float(max(dh)), 'min', float(min(dh)), 'argmax', dh.index(max(dh)))
print('IRs A', float(LA.IRs), 'B', float(f(LB.IRs)))
cc = DC.load_cert(path); ch = DC.Checker(cc, log=lambda s: None); ch.data_checks()
print('heights C - A: max', float(max(ch.h[j] - hA[j] for j in range(len(hA)))), 'min', float(min(ch.h[j] - hA[j] for j in range(len(hA)))))
rect = (F(0), F(cert['G_up']), -LA.w, F(cert['P_up']))
best = None
for bx in DA.walk(cert['tree'], rect):
    ub_, _ = LB.box(*(DB.Q('%d/%d' % (t.numerator, t.denominator)) for t in bx))
    if best is None or f(ub_) > best[0]: best = (f(ub_), bx)
bx = best[1]
print('worst-B box', [float(t) for t in bx])
ua, ia = LA.box(*bx); print('A', float(ua), ia)
