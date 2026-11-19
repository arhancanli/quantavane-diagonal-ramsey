# Referee's independent re-check of the Section 5 bank conditions (not Lemma C/D internals) over ALL new objects.
import json, sys, time, bisect, random
sys.path.insert(0, '.')
from fractions import Fraction as F
from liv import I
P = sys.argv[1]; T0 = time.time()
c = json.load(open(P)); zb = json.load(open("<archive>/ramsey-zbs/zbs_bank.json"))
fails = []; cnt = {}
def chk(name, cond, info=None):
    cnt[name] = cnt.get(name, 0) + 1
    if not cond:
        fails.append((name, info))
        if len(fails) < 30: print("FAIL", name, info, flush=True)
class Prof:
    __slots__ = ("p", "xs", "ys")
    def __init__(s, d): s.p = F(d["p"]); s.xs = [F(t) for t in d["xs"]]; s.ys = [F(t) for t in d["ys"]]
    def L(s, t):
        xs = s.xs
        if not (xs[0] <= t <= xs[-1]): raise ValueError("dom")
        j = bisect.bisect_right(xs, t) - 1
        if j == len(xs) - 1: return s.ys[-1]
        a, b = xs[j], xs[j+1]; return s.ys[j] + (s.ys[j+1] - s.ys[j]) * (t - a) / (b - a)
zr = [Prof(d) for d in zb["raw"]]; zc = [Prof(d) for d in zb["closed"]]
nr = [Prof(d) for d in c["raw"]]; nc = [Prof(d) for d in c["closed"]]
def prof(ref):
    k, i = ref
    if not (isinstance(i, int) and i >= 0): raise ValueError("bad index")
    return {"zr": zr, "zc": zc, "nr": nr, "nc": nc}[k][i]
lines = [(F(a), F(b)) for a, b in zb["lines"]]
def srcAB(ref):
    k, i = ref; assert i >= 0
    if k == "z": return F(zb["A"][i]), F(zb["B"][i])
    s = c["sources"][i]; return F(s["A"]), F(s["B"])
expcache = {}
def emx(v):  # enclosure of e^{-v}
    if v not in expcache: expcache[v] = (-I(v)).exp()
    return expcache[v]
ctl = c["controls"]
# controls: basic part of Def 5.2 check (Lemma C / D internals sampled elsewhere)
for i, ct in enumerate(ctl):
    p, mu, w, beta, x, lxU, l1mL = (F(ct[k]) for k in ("p", "mu", "w", "beta", "x", "lxU", "l1mL"))
    chk("ctl ranges", 0 < p < 1 and 0 < mu < 1 and w > 0 and 0 < beta < 1 and 0 < x < p, i)
    chk("ctl x<(1-mu)^w via lxU,l1mL", I(x).le(I(lxU).exp()) and I(l1mL).exp().le(1 - mu) and lxU < w * l1mL, i)
    chk("ctl exactly one kind", ("cert" in ct) != ("lemmaD" in ct), i)
print("controls done %.0fs" % (time.time() - T0), flush=True)
minsl = {}
def rec(name, v):
    if name not in minsl or v < minsl[name][0]: minsl[name] = (v,)
for ri, (Rd, R) in enumerate(zip(c["raw"], nr)):
    chk("raw p", 0 < R.p < 1, ri); chk("raw knots", len(R.xs) >= 2 and R.xs[0] > 0 and all(a < b for a, b in zip(R.xs, R.xs[1:])), ri)
    mn = F(Rd["min"]); chk("raw min", mn > 0 and all(mn <= y for y in R.ys), ri)
    pcs = Rd["pieces"]
    chk("raw cover", F(pcs[0]["lo"]) == R.xs[0] and F(pcs[-1]["hi"]) == R.xs[-1] and all(F(a["hi"]) == F(b["lo"]) for a, b in zip(pcs, pcs[1:])), ri)
    for pi, pc in enumerate(pcs):
        lo, hi = F(pc["lo"]), F(pc["hi"]); bp = [F(u) for u in pc["bp"]]; margin = F(pc["margin"])
        chk("piece bp lo..hi", bp[0] == lo and bp[-1] == hi and all(a < b for a, b in zip(bp, bp[1:])) and lo > 0 and lo < hi, (ri, pi))
        chk("piece margin>0", margin > 0, (ri, pi))
        bps = set(bp)
        chk("piece bp has L_P knots", all(u in bps for u in R.xs if lo < u < hi), (ri, pi))
        t = pc["t"] if pc["kind"] == "route" else pc
        ct = ctl[t["c"]]; p, mu, w, x = (F(ct[k]) for k in ("p", "mu", "w", "x"))
        xi, nu, ys, aU, bU = (F(t[k]) for k in ("xi", "nu", "ys", "aU", "bU")); A_s, B_s = srcAB(t["src"])
        chk("term 0<xi<x", 0 < xi < x, (ri, pi)); chk("term xi<e^-A_s", I(xi).lt(emx(A_s)), (ri, pi))
        chk("term 0<nu<mu", 0 < nu < mu, (ri, pi)); chk("term ys>0", ys > 0, (ri, pi))
        chk("term e^-aU<=xi", emx(aU).le(xi), (ri, pi)); chk("term e^-bU<=nu", emx(bU).le(nu), (ri, pi))
        Bg = B_s + ys
        if pc["kind"] == "leaf":
            chk("leaf p_g<=p_P", p <= R.p, (ri, pi))
            sl = min(R.L(u) - (margin + aU / (1 + w) + u * (margin + (Bg + w * bU) / (1 + w))) for u in bp)
            chk("leaf ineq", sl >= 0, (ri, pi)); rec("leaf", sl)
        elif pc["kind"] == "route":
            chk("route p_g<p_P", p < R.p, (ri, pi))
            us = [F(u) for u in pc["us"]]; ds = [F(u) for u in pc["ds"]]; g0 = F(pc["g0"]); hm = F(pc["hm"]); th = us[0]
            chk("route us", all(a < b for a, b in zip(us, us[1:])) and th > 0 and g0 > 0 and th <= lo and hi <= us[-1] and hm > 0, (ri, pi))
            chk("route calls count", len(pc["calls"]) == len(us) - 1 == len(ds), (ri, pi))
            gk = [F(0)]
            for d, a, b in zip(ds, us, us[1:]): gk.append(gk[-1] + d * (b - a))
            def gL(s):
                j = bisect.bisect_right(us, s) - 1; j = min(max(j, 0), len(us) - 2)
                return gk[j] + ds[j] * (s - us[j])
            chk("route bp has us knots", all(u in bps for u in us if lo < u < hi), (ri, pi))
            for j, call in enumerate(pc["calls"]):
                a, b = us[j], us[j+1]
                try: ch = prof(call["ch"])
                except Exception: chk("call ref valid", False, (ri, pi, j)); continue
                zj = F(call["z"]); cbp = [F(u) for u in call["bp"]]; cset = set(cbp)
                chk("call child dom", ch.xs[0] <= a and b <= ch.xs[-1], (ri, pi, j))
                chk("call z", 0 < zj < 1 - ch.p and emx(ds[j]).le(zj), (ri, pi, j))
                chk("call bp a..b + child knots", cbp[0] == a and cbp[-1] == b and all(u1 < u2 for u1, u2 in zip(cbp, cbp[1:])) and all(u in cset for u in ch.xs if a < u < b), (ri, pi, j))
                sl = min(g0 + gL(u) - hm - ch.L(u) for u in cbp)
                chk("call L_c<=psi-hm", sl >= 0, (ri, pi, j)); rec("call", sl)
            s1 = min(R.L(u) - margin - g0 - gL(u) for u in bp)
            s2 = min(R.L(u) - (margin + (aU + w * th * bU) / (1 + w) + u * Bg / (1 + w) + (w / (1 + w)) * gL(u)) for u in bp)
            chk("route psi ineq", s1 >= 0, (ri, pi)); chk("route terminal ineq", s2 >= 0, (ri, pi)); rec("route_psi", s1); rec("route_term", s2)
        else:
            chk("piece kind", False, (ri, pi))
print("raw done %.0fs" % (time.time() - T0), flush=True)
for qi, (Qd, Q) in enumerate(zip(c["closed"], nc)):
    chk("closed p", 0 < Q.p < 1, qi); chk("closed knots", len(Q.xs) >= 2 and Q.xs[0] > 0 and all(a < b for a, b in zip(Q.xs, Q.xs[1:])), qi)
    mn = F(Qd["min"]); chk("closed min", mn > 0 and all(mn <= y for y in Q.ys), qi)
    pcs = Qd["pieces"]
    chk("closed cover", F(pcs[0]["lo"]) == Q.xs[0] and F(pcs[-1]["hi"]) == Q.xs[-1] and all(F(a["hi"]) == F(b["lo"]) for a, b in zip(pcs, pcs[1:])), qi)
    for pi, pc in enumerate(pcs):
        lo, hi = F(pc["lo"]), F(pc["hi"]); bp = [F(u) for u in pc["bp"]]; bps = set(bp)
        chk("closed R raw", pc["R"][0] in ("zr", "nr"), (qi, pi)); R = prof(pc["R"])
        chk("closed bp", bp[0] == lo and bp[-1] == hi and all(a < b for a, b in zip(bp, bp[1:])), (qi, pi))
        chk("closed dom R", R.xs[0] <= lo and hi <= R.xs[-1], (qi, pi))
        chk("closed bp knots", all(u in bps for u in R.xs + Q.xs if lo < u < hi), (qi, pi))
        chk("closed L_R<=L_Q", all(R.L(u) <= Q.L(u) for u in bp), (qi, pi))
        if pc["kind"] == "density": chk("density p_R<=p_Q", R.p <= Q.p, (qi, pi))
        elif pc["kind"] == "pair":
            chk("pair S raw", pc["S"][0] in ("zr", "nr"), (qi, pi)); S = prof(pc["S"])
            chk("pair dens", R.p + S.p <= 1 and lo > 0, (qi, pi)); chk("pair dom S", S.xs[0] <= 1 / hi and 1 / lo <= S.xs[-1], (qi, pi))
            chk("pair bp recip", all(1 / u in bps for u in S.xs if lo < 1 / u < hi), (qi, pi))
            chk("pair ineq", all(u * S.L(1 / u) <= Q.L(u) for u in bp), (qi, pi))
        else: chk("closed kind", False, (qi, pi))
print("closed done %.0fs" % (time.time() - T0), flush=True)
for si, s in enumerate(c["sources"]):
    A, B, Lo, Hi, eps, eta = (F(s[k]) for k in ("A", "B", "Lo", "Hi", "eps", "eta"))
    chk("src basic", A > 0 and B > 0 and 0 < Lo < Hi and eps > 0 and eta > 0, si)
    cL, dL = lines[s["kL"]]; cR, dR = lines[s["kR"]]
    chk("src left tail", all(cL + dL * t <= A + B * t - eps * (1 + t) for t in (F(0), Lo)), si)
    chk("src right tail", cR + dR * Hi <= A + B * Hi - eps * (1 + Hi) and dR <= B - eps, si)
    cells = s["cells"]
    chk("src cells cover", F(cells[0]["lo"]) == Lo and F(cells[-1]["hi"]) == Hi and all(F(a["hi"]) == F(b["lo"]) for a, b in zip(cells, cells[1:])) and all(F(a["lo"]) < F(a["hi"]) for a in cells), si)
    for ci, cl in enumerate(cells):
        lo, hi = F(cl["lo"]), F(cl["hi"])
        if cl["kind"] == "grounded":
            cc, dd = lines[cl["k"]]
            chk("grounded", all(cc + dd * t <= A + B * t - eta * (1 + t) for t in (lo, hi)), (si, ci))
        elif cl["kind"] == "pair":
            PR, PB = prof(cl["PR"]), prof(cl["PB"]); bp = [F(u) for u in cl["bp"]]; bps = set(bp)
            chk("srcpair dens", PR.p + PB.p <= 1, (si, ci))
            chk("srcpair dom", PR.xs[0] <= lo and hi <= PR.xs[-1] and PB.xs[0] <= 1 / hi and 1 / lo <= PB.xs[-1], (si, ci))
            chk("srcpair bp", bp[0] == lo and bp[-1] == hi and all(a < b for a, b in zip(bp, bp[1:])) and all(u in bps for u in PR.xs if lo < u < hi) and all(1 / u in bps for u in PB.xs if lo < 1 / u < hi), (si, ci))
            sl = min(min((A - eta) + (B - eta) * u - PR.L(u), (A - eta) + (B - eta) * u - u * PB.L(1 / u)) for u in bp)
            chk("srcpair ineq", sl >= 0, (si, ci)); rec("srcpair", sl)
        else: chk("cell kind", False, (si, ci))
print("sources done %.0fs" % (time.time() - T0), flush=True)
print("counts:", json.dumps(cnt))
print("min slacks:", {k: float(v[0]) for k, v in minsl.items()})
print("TOTAL FAILS", len(fails), fails[:20])
