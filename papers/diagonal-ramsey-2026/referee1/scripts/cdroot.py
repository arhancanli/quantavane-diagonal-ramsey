import json, sys, glob, os
sys.path.insert(0, '.')
from fractions import Fraction as F
from liv import I, Ctl
P = sys.argv[1]
c = json.load(open(P))
Qd = c["closed"][c["root"]["closed"]]; Rd = c["raw"][Qd["pieces"][0]["R"][1]]; ci = Rd["pieces"][0]["t"]["c"]
print("root control index", ci)
cds = [i for i, ct in enumerate(c["controls"]) if "lemmaD" in ct]
both = [i for i, ct in enumerate(c["controls"]) if "lemmaD" in ct and "cert" in ct]
none = [i for i, ct in enumerate(c["controls"]) if "lemmaD" not in ct and "cert" not in ct]
print("n CD controls", len(cds), "with both kinds", len(both), "with neither", len(none))
ctls = {i: c["controls"][i] for i in cds}
del c
vend = {}
for f in sorted(glob.glob("research/tier2/ramsey-zbs/code/lemmaD/certs/*.json")):
    vend[os.path.basename(f)] = json.load(open(f))
print("vendored files", len(vend), "keys of one:", list(next(iter(vend.values())).keys()))
def canon(d): return json.dumps(d, sort_keys=True)
matched = {}
for i, ct in ctls.items():
    ld = ct["lemmaD"]
    m = [n for n, v in vend.items() if all(canon(v.get(k)) == canon(ld.get(k)) for k in ld.keys())]
    matched[i] = m
    ctlv = [v.get("control") for n, v in vend.items() if n in m]
    five = {k: ct[k] for k in ("p", "mu", "w", "beta", "x")}
    fm = [canon({k: F(cv[k]) .__str__() for k in five}) == canon({k: F(five[k]).__str__() for k in five}) for cv in ctlv if cv]
    print("ctl", i, "x", five["x"], "-> vendored", m, "five-fields match vendored control:", fm, "embedded has control field:", "control" in ld)
used = set(n for m in matched.values() for n in m); print("vendored not used:", sorted(set(vend) - used))
# K-checks on each CD control (my own enclosures)
for i, ct in ctls.items():
    p, mu, w, beta, x = (F(ct[k]) for k in ("p", "mu", "w", "beta", "x")); ld = ct["lemmaD"]
    C = Ctl(p, mu, w, beta, x)
    a_cut, a_hi, alpha, u_b, D, y_c, G_up, P_up = (F(ld[k]) for k in ("a_cut", "a_hi", "alpha", "u_b", "Dplus", "y_c", "G_up", "P_up"))
    qg = [F(t) for t in ld["qgrid"]]; jA0 = ld["jA0"]; N = len(qg) - 1
    K1 = 0 < p < 1 and 0 < mu < 1 and w > 0 and 0 < beta < 1 and 0 < x < p and I(x).lt((w * I(1 - mu).ln()).exp())
    # G0'(q) = log p - beta log(p/x) - beta w log mu + beta w (log q - log(1-q))  [from G0 expansion]
    def G0p(q): return C.lp - beta * (C.lp - C.lx) - beta * w * C.lmu + beta * w * (I(q).ln() - I(1 - q).ln())
    gp = G0p(a_hi)
    K2 = 0 < a_cut < a_hi < mu and C.G0(a_cut).ge(0) and C.G0(a_hi).lt(0) and C.G0(mu).lt(0) and gp.lt(0) and (beta / (-gp)).le(alpha)
    nD = (1 - u_b) / D
    K3 = 0 < u_b < 1 and D > 0 and nD.denominator == 1 and nD >= 1
    K4 = N >= 2 and qg[0] == a_cut and qg[N] == mu and all(a < b for a, b in zip(qg, qg[1:])) and qg[1] >= a_hi
    lub = I(u_b).ln(); g = -w * u_b * lub; phis = -w * (1 + lub)
    K8 = phis.ge(y_c)
    K9 = I(G_up).ge(g) and I(P_up).ge(-w * lub)
    # K7: y_c > -w and y_c >= Ht'(mu): Ht'(mu) computed below on the active branch at mu
    A, B = C.AB(mu)
    print("ctl", i, "K1", K1, "K2", K2, "K3", K3, "n=(1-u_b)/D", nD, "u_b", float(u_b), "D", float(D), "K4", K4, "N", N, "jA0", jA0, "K8", K8, "K9", K9,
          "| A-B at mu", (A - B), "y_c", float(y_c), "phi_s(u_b)", phis)
