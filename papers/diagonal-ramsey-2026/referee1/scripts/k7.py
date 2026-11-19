import json, sys, glob, os
sys.path.insert(0, '.')
from fractions import Fraction as F
from liv import I, Ctl
# K7 on vendored certs (each has its own control field) + root file
for f in sorted(glob.glob("research/tier2/ramsey-zbs/code/lemmaD/certs/*.json")):
    v = json.load(open(f)); ct = v["control"]
    p, mu, w, beta, x = (F(ct[k]) for k in ("p", "mu", "w", "beta", "x")); C = Ctl(p, mu, w, beta, x)
    q = mu; A, B = C.AB(q)
    l = C.lp + w * I(1 - q).ln() - C.lx
    Ap = (-w * q - l) / (q * q); Bp = I(-w / q)
    if A.gt(B):
        eB = (beta * B).exp(); eA = (beta * A).exp(); Z = (eB - p * eA) / (1 - p); Zp = (beta * Bp * eB - p * beta * Ap * eA) / (1 - p)
        Htp = p * (-l - w) + ((1 - p) / beta) * (Z.ln() + q * Zp / Z)
    else:
        Htp = B + q * Bp
    yc = F(v["y_c"])
    print(os.path.basename(f), "x", ct["x"], "Ht'(mu)", Htp, "y_c", float(yc), "K7", yc > -w and I(yc).ge(Htp), "u_b", v["u_b"], "Dplus", v["Dplus"])
