import sys, json
sys.path.insert(0, 'research/tier2/ramsey-zbs/code/lemmaD')
sys.path.insert(1, 'research/tier2/ramsey-lemma/cert_independent')
from fractions import Fraction as F
import checkD_A as DA, checkD_B as DB, checkD_C as DC
cert = json.load(open(sys.argv[1]))
LA = DA.LemmaD(cert); LB = DB.LemmaD(cert)
cc = DC.load_cert(sys.argv[1]); ch = DC.Checker(cc, log=lambda s: None); ch.data_checks()
M = ch.M; qs = LA.qs
worst = None; nbad = 0
for i in sorted(LA.d2):
    pts = [qs[i], (qs[i] + qs[i + 1]) / 2, qs[i + 1]]
    lb = F(0)
    for q in pts:
        js = M.active(DC.IV.of(q), 2)
        # lower bound of |Ht''(q)|: min over possibly active branch values of the lower bound of |.|
        for J in js:
            v = J.deriv(2); l = min(abs(v.lof()), abs(v.hif())) if (v.lof() > 0 or v.hif() < 0) else F(0)
            lb = max(lb, l) if len(js) == 1 else lb
    dA = LA.d2[i]; dB = F(int(LB.d2[i].p), int(LB.d2[i].q)); dC = ch.d2[i]
    if dA < lb or dB < lb or dC < lb: nbad += 1; print('UNSOUND cell', i, float(dA), float(dB), float(dC), float(lb))
    r = (dA / lb) if lb else None
    if worst is None or (r is not None and r < worst[0]): worst = (r, i, float(dA), float(dB), float(dC), float(lb))
print('cells', len(LA.d2), 'bad', nbad, 'tightest ratio d2_A / pointwise lower bound', worst)
i = 517; print('cell 517: A', float(LA.d2[i]), 'B', float(F(int(LB.d2[i].p), int(LB.d2[i].q))), 'C', float(ch.d2[i]))
