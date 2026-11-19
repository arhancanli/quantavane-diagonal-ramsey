import json, sys, time, bisect
sys.path.insert(0, '.')
from fractions import Fraction as F
from liv import I
P = sys.argv[1]
c = json.load(open(P)); zb = json.load(open("<archive>/ramsey-zbs/zbs_bank.json"))
class Prof:
    def __init__(s, d):
        s.p = F(d["p"]); s.xs = [F(t) for t in d["xs"]]; s.ys = [F(t) for t in d["ys"]]
    def L(s, t):
        t = F(t); xs = s.xs; assert xs[0] <= t <= xs[-1], ("out of domain", float(t), float(xs[0]), float(xs[-1]))
        j = bisect.bisect_right(xs, t) - 1
        if j == len(xs) - 1: return s.ys[-1]
        a, b = xs[j], xs[j+1]; return s.ys[j] + (s.ys[j+1] - s.ys[j]) * (t - a) / (b - a)
cache = {}
def prof(ref):
    key = tuple(ref)
    if key not in cache:
        kind, i = ref; assert i >= 0
        d = {"zr": lambda: zb["raw"][i], "zc": lambda: zb["closed"][i], "nr": lambda: c["raw"][i], "nc": lambda: c["closed"][i]}[kind]()
        cache[key] = Prof(d)
    return cache[key]
def srcAB(ref):
    kind, i = ref
    if kind == "z": return F(zb["A"][i]), F(zb["B"][i])
    s = c["sources"][i]; return F(s["A"]), F(s["B"])
res = []
def chk(name, cond): res.append((name, bool(cond)));  print(("OK  " if cond else "FAIL") , name) if not cond else None
Qi = c["root"]["closed"]; Qd = c["closed"][Qi]; Q = Prof(Qd); z = F(c["root"]["z"])
pcs1 = [pc for pc in Qd["pieces"] if F(pc["lo"]) <= 1 <= F(pc["hi"])]
chk("root: pieces containing 1 nonempty and all pairs", len(pcs1) > 0 and all(pc["kind"] == "pair" for pc in pcs1))
chk("root: L_Q(1) = z", Q.L(1) == z)
print("p_Q", Qd["p"], "I_Q", [str(Q.xs[0]), str(Q.xs[-1])])
for pc in Qd["pieces"]:
    lo, hi = F(pc["lo"]), F(pc["hi"]); bp = [F(t) for t in pc["bp"]]
    R = prof(pc["R"]); assert pc["R"][0] in ("nr", "zr")
    chk("Q bp from lo to hi, increasing", bp[0] == lo and bp[-1] == hi and all(a < b for a, b in zip(bp, bp[1:])))
    chk("dom R contains [lo,hi]", R.xs[0] <= lo and hi <= R.xs[-1])
    kn = [t for t in R.xs + Q.xs if lo < t < hi]; chk("bp has knots of R,Q", all(t in bp for t in kn))
    chk("L_R <= L_Q at bp", all(R.L(t) <= Q.L(t) for t in bp))
    if pc["kind"] == "pair":
        S = prof(pc["S"]); assert pc["S"][0] in ("nr", "zr")
        chk("p_R+p_S<=1", R.p + S.p <= 1); chk("lo>0", lo > 0)
        chk("dom S contains [1/hi,1/lo]", S.xs[0] <= 1/hi and 1/lo <= S.xs[-1])
        chk("bp has 1/knots of S", all(1/t in bp for t in S.xs if lo < 1/t < hi))
        chk("t L_S(1/t) <= L_Q at bp", all(t * S.L(1/t) <= Q.L(t) for t in bp))
# root raw profile R and its pieces
Rref = Qd["pieces"][0]["R"]; Rd = c["raw"][Rref[1]]; R = prof(Rref)
print("R p", Rd["p"], "dom", float(R.xs[0]), float(R.xs[-1]), "pieces", len(Rd["pieces"]))
chk("R pieces cover dom", F(Rd["pieces"][0]["lo"]) == R.xs[0] and F(Rd["pieces"][-1]["hi"]) == R.xs[-1] and all(F(a["hi"]) == F(b["lo"]) for a, b in zip(Rd["pieces"], Rd["pieces"][1:])))
chk("R min>0, min<=L at knots", F(Rd["min"]) > 0 and all(F(Rd["min"]) <= y for y in R.ys))
for pc in Rd["pieces"]:
    t = pc["t"]; ci = t["c"]; ctl = c["controls"][ci]
    p, mu, w, x = (F(ctl[k]) for k in ("p", "mu", "w", "x"))
    xi, nu, ys, aU, bU = (F(t[k]) for k in ("xi", "nu", "ys", "aU", "bU"))
    A_s, B_s = srcAB(t["src"])
    print("control", ci, "kind", "lemmaD" if "lemmaD" in ctl else "cert", "src", t["src"], "A_s", float(A_s), "B_s", float(B_s))
    chk("0<xi<x", 0 < xi < x); chk("xi < e^{-A_s}", I(xi).lt((-I(A_s)).exp()))
    print("   xi", float(xi), "e^-A_s", (-I(A_s)).exp(), "x", float(x))
    chk("0<nu<mu", 0 < nu < mu); chk("ys>0", ys > 0)
    chk("e^-aU <= xi", (-I(aU)).exp().le(xi)); chk("e^-bU <= nu", (-I(bU)).exp().le(nu))
    lo, hi = F(pc["lo"]), F(pc["hi"]); bp = [F(u) for u in pc["bp"]]; margin = F(pc["margin"])
    chk("bp from lo to hi increasing", bp[0] == lo and bp[-1] == hi and all(a < b for a, b in zip(bp, bp[1:])))
    chk("margin>0, lo>0", margin > 0 and lo > 0)
    if pc["kind"] == "route":
        chk("p_gamma < p_P", p < R.p)
        us = [F(u) for u in pc["us"]]; ds = [F(u) for u in pc["ds"]]; g0 = F(pc["g0"]); hm = F(pc["hm"]); th = us[0]
        chk("us incr, theta>0, g0>0, theta<=lo, hi<=uM, hm>0", all(a < b for a, b in zip(us, us[1:])) and th > 0 and g0 > 0 and th <= lo and hi <= us[-1] and hm > 0)
        chk("one call per cell", len(pc["calls"]) == len(us) - 1 == len(ds))
        def gL(s):
            return sum(d * (min(max(s, a), b) - a) for d, a, b in zip(ds, us, us[1:]))
        psi = lambda s: g0 + gL(s)
        minslack_child = None
        for j, call in enumerate(pc["calls"]):
            a, b = us[j], us[j+1]; ch = prof(call["ch"]); zj = F(call["z"]); cbp = [F(u) for u in call["bp"]]
            chk("child dom contains cell %d" % j, ch.xs[0] <= a and b <= ch.xs[-1])
            chk("e^-d <= z_j < 1-p_c, z_j>0 (cell %d)" % j, (-I(ds[j])).exp().le(zj) and 0 < zj < 1 - ch.p)
            chk("call bp from a to b incl child knots (cell %d)" % j, cbp[0] == a and cbp[-1] == b and all(u in cbp for u in ch.xs if a < u < b))
            for u in cbp:
                sl = psi(u) - hm - ch.L(u); minslack_child = sl if minslack_child is None or sl < minslack_child else minslack_child
            chk("L_child <= psi - hm at bp (cell %d)" % j, all(ch.L(u) <= psi(u) - hm for u in cbp))
        print("   min (psi-hm-L_child) slack %.3e" % float(minslack_child))
        chk("bp has knots of L_P and us in (lo,hi)", all(u in bp for u in R.xs + us if lo < u < hi))
        Bg = B_s + ys
        s1 = min(R.L(u) - (margin + psi(u)) for u in bp)
        s2 = min(R.L(u) - (margin + (aU + w * th * bU) / (1 + w) + u * Bg / (1 + w) + (w / (1 + w)) * gL(u)) for u in bp)
        print("   slack margin+psi<=L: %.3e ; terminal slack %.3e" % (float(s1), float(s2)))
        chk("margin+psi<=L_P at bp", s1 >= 0); chk("terminal ineq at bp", s2 >= 0)
    else:
        Bg = B_s + ys
        s = min(R.L(u) - (margin + aU / (1 + w) + u * (margin + (Bg + w * bU) / (1 + w))) for u in bp)
        chk("leaf ineq at bp", s >= 0); print("   leaf slack %.3e" % float(s))
fails = [n for n, v in res if not v]
print("checks:", len(res), "fails:", len(fails), fails[:10])
