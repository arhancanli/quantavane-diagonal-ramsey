import json, sys, time
sys.path.insert(0, '.')
from fractions import Fraction as F
from liv import I, Ctl
P = sys.argv[1]; ci = int(sys.argv[2]) if len(sys.argv) > 2 else None
c = json.load(open(P))
if ci is None:
    Q = c["closed"][c["root"]["closed"]]; R = c["raw"][Q["pieces"][0]["R"][1]]; ci = R["pieces"][0]["t"]["c"]
ctl = c["controls"][ci]; del c
p, mu, w, beta, x = (F(ctl[k]) for k in ("p", "mu", "w", "beta", "x"))
lxU, l1mL = F(ctl["lxU"]), F(ctl["l1mL"])
C = Ctl(p, mu, w, beta, x)
ok = []
ok.append(("0<p<1 etc", 0 < p < 1 and 0 < mu < 1 and w > 0 and 0 < beta < 1 and 0 < x < p))
ok.append(("x<=e^lxU", I(x).le(I(lxU).exp()) ))
ok.append(("e^l1mL<=1-mu", I(l1mL).exp().le(1 - mu)))
ok.append(("lxU<w l1mL", lxU < w * l1mL))
ok.append(("direct x<(1-mu)^w", I(x).lt((w * I(1 - mu).ln()).exp())))
ce = ctl["cert"]; q = [F(t) for t in ce["q"]]; h = [F(t) for t in ce["h"]]; sec = ce["sec"]; k = ce["k"]; N = len(q) - 1
ok.append(("q0=a_cut", q[0] == F(ce["a_cut"]) and q[0] > 0)); ok.append(("qN=mu", q[N] == mu))
ok.append(("incr", all(q[i] < q[i+1] for i in range(N)))); ok.append(("N>=2,0<=k<=N", N >= 2 and 0 <= k <= N))
g0a = C.G0(q[0]); g0m = C.G0(mu)
ok.append(("G0(q0)>=0", g0a.ge(0))); ok.append(("G0(mu)<0", g0m.lt(0)))
print("G0(q0)", g0a, "G0(mu)", g0m)
Hc = {}
def H(j):
    if j not in Hc: Hc[j] = C.H(q[j])
    return Hc[j]
t = time.time(); worst = None
for i in range(N):
    u, v = sec[i]
    assert 0 <= u < v <= N and (v <= i or u >= i + 1), ("sec idx", i, u, v)
    Hu, Hv = H(u), H(v)
    for node in (i, i + 1):
        lam = (q[node] - q[u]) / (q[v] - q[u])
        T = Hu * (1 - lam) + Hv * lam
        slack = F(h[node]) - T.hi
        if worst is None or slack < worst[0]: worst = (slack, i, node)
        assert T.le(h[node]), ("secant fails", i, node, T, float(h[node]))
print("secants ok; min slack %.3e at cell %d node %d; %.1fs" % (float(worst[0]), worst[1], worst[2], time.time() - t))
ok.append(("dominance", all(h[j] <= h[k] for j in range(k + 1, N + 1))))
S = I(h[k] - w * q[k])
for i in range(k):
    Di = w * (q[i+1] - q[i]); ri = (h[i] - h[i+1]) / Di
    S = S + Di * I(ri).exp()
print("hinge sum", S)
ok.append(("hinge<0", S.lt(0)))
# also the true CERT bound with the (e^r - r - 1) form, as a cross-check of telescoping
for name, val in ok: print(name, val)
print("ALL OK" if all(v for _, v in ok) else "SOME FAIL")
