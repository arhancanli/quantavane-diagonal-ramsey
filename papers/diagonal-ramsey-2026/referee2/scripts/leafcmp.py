import sys, json
sys.path.insert(0, 'research/tier2/ramsey-zbs/code/lemmaD')
sys.path.insert(1, 'research/tier2/ramsey-lemma/cert_independent')
from fractions import Fraction as F
import checkD_A as DA, checkD_B as DB, checkD_C as DC
path = sys.argv[1]
cert = json.load(open(path))
LA = DA.LemmaD(cert); LB = DB.LemmaD(cert)
cc = DC.load_cert(path); ch = DC.Checker(cc, log=lambda s: None); ok = ch.data_checks()
ch.IRs = ch.full.integral_up(cc['u_b'], F(1))
w = cc['w']; yc = cc['y_c']
ch.Ecap_const = ((DC.IV.of(yc * yc - w * w) / 2) + w * w * (1 - DC.iexp(-1 - yc / w))).hif()
rect = (F(0), F(cert['G_up']), -LA.w, F(cert['P_up']))
mx = 0; n = 0; worst = []
for bx in DA.walk(cert['tree'], rect):
    ua, _ = LA.box(*bx)
    ub_, _ = LB.box(*(DB.Q('%d/%d' % (t.numerator, t.denominator)) for t in bx))
    st, uc, _ = ch.box_U(*bx)
    ub_ = F(int(ub_.p), int(ub_.q))
    d = max(abs(ua - ub_), abs(ua - uc)); n += 1
    if ua != -1: mx = max(mx, d / max(abs(ua), F(1, 10**12)))
    worst.append((float(ua), float(ub_), float(uc)))
worst.sort(reverse=True)
print('leaves', n, 'max relative disagreement of U among A,B,C', float(mx))
for t in worst[:5]: print('top U: A %.6e  B %.6e  C %.6e' % t)
