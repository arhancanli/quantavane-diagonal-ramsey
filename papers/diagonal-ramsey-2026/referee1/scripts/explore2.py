import json, sys
from fractions import Fraction as F
P = sys.argv[1]
c = json.load(open(P))
Q = c["closed"][c["root"]["closed"]]
ref = Q["pieces"][0]["R"]; R = c["raw"][ref[1]]
print("R p", R["p"], "xs", R["xs"], "ys", R["ys"], "min", R["min"], "npieces", len(R["pieces"]))
pc = R["pieces"][0]
d = {k: v for k, v in pc.items() if k != "calls"}
print("piece", json.dumps(d)[:3000])
print("ncalls", len(pc["calls"]), json.dumps(pc["calls"][:3])[:1500])
ci = pc["t"]["c"]; ctl = c["controls"][ci]
print("root control index", ci, {k: ctl[k] for k in ctl if k not in ("cert","lemmaD","gen")})
if "cert" in ctl:
    ce = ctl["cert"]; print("cert keys", list(ce.keys()), "N", len(ce["q"]) - 1, "k", ce["k"], "a_cut", ce["a_cut"])
if "lemmaD" in ctl:
    ld = ctl["lemmaD"]; print("lemmaD keys", list(ld.keys()), {k: ld[k] for k in ld if k not in ("tree","qgrid")}, "N", len(ld["qgrid"]) - 1)
print("gen", json.dumps(ctl.get("gen"))[:400])
src = pc["t"]["src"]; print("src", src)
if src[0] == "n": s = c["sources"][src[1]]; print("A,B", s["A"], s["B"])
