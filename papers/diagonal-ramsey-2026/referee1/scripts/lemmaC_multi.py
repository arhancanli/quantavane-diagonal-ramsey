import json, sys, time, random
sys.path.insert(0, '.')
from fractions import Fraction as F
from liv import I, Ctl
P = sys.argv[1]; nrand = int(sys.argv[2])
c = json.load(open(P))
Qd = c["closed"][c["root"]["closed"]]; Rd = c["raw"][Qd["pieces"][0]["R"][1]]
sel = set()
for call in Rd["pieces"][0]["calls"]:
    k, i = call["ch"]
    if k == "nr":
        for pc in c["raw"][i]["pieces"]:
            sel.add((pc["t"] if pc["kind"] == "route" else pc)["c"])
withcert = [i for i, ct in enumerate(c["controls"]) if "cert" in ct]
random.seed(20261119); sel |= set(random.sample(withcert, nrand))
sel = sorted(i for i in sel if "cert" in c["controls"][i])
ctls = {i: c["controls"][i] for i in sel}; del c
print("checking", len(sel), "controls:", sel, flush=True)
worst = None
for i in sel:
    ct = ctls[i]; t = time.time()
    p, mu, w, beta, x = (F(ct[k]) for k in ("p", "mu", "w", "beta", "x")); C = Ctl(p, mu, w, beta, x)
    ce = ct["cert"]; q = [F(u) for u in ce["q"]]; h = [F(u) for u in ce["h"]]; k = ce["k"]; N = len(q) - 1
    ok = q[0] == F(ce["a_cut"]) > 0 and q[N] == mu and all(a < b for a, b in zip(q, q[1:])) and N >= 2 and 0 <= k <= N
    ok = ok and C.G0(q[0]).ge(0) and C.G0(mu).lt(0)
    Hc = {}
    def H(j):
        if j not in Hc: Hc[j] = C.H(q[j])
        return Hc[j]
    for ii, (u, v) in enumerate(ce["sec"]):
        ok = ok and 0 <= u < v <= N and (v <= ii or u >= ii + 1)
        for node in (ii, ii + 1):
            lam = (q[node] - q[u]) / (q[v] - q[u]); T = H(u) * (1 - lam) + H(v) * lam
            ok = ok and T.le(h[node])
    ok = ok and all(h[j] <= h[k] for j in range(k + 1, N + 1))
    S = I(h[k] - w * q[k])
    for ii in range(k):
        Di = w * (q[ii+1] - q[ii]); S = S + Di * I((h[ii] - h[ii+1]) / Di).exp()
    ok = ok and S.lt(0)
    print("ctl %4d N=%4d k=%4d hinge=%.3e ok=%s (%.1fs)" % (i, N, k, float(S.hi), ok, time.time() - t), flush=True)
    if worst is None or S.hi > worst[0]: worst = (S.hi, i)
print("worst hinge", float(worst[0]), "at", worst[1])
