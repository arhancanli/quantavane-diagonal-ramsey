# Float sanity check (NOT rigorous): CERT and V_A at the saturated profile phi_s (eta=0) for a CD control.
import json, sys, math, time
from fractions import Fraction as Fr
fn = sys.argv[1]
v = json.load(open(fn)); ct = v["control"]
p, mu, w, beta, x = (float(Fr(ct[k])) for k in ("p", "mu", "w", "beta", "x"))
u_b = float(Fr(v["u_b"])); D = float(Fr(v["Dplus"]))
lp, lx, lmu = math.log(p), math.log(x), math.log(mu)
def G0(q): return q*lp + beta*(1-q)*(lp + w*math.log1p(-q) - lx) - beta*w*q*(lmu - math.log(q))
def AB(q):
    l = lp + w*math.log1p(-q) - lx
    return (1-q)/q*l, w*(lmu - math.log(q)), l
def Ht(q):
    A, B, l = AB(q)
    if A <= B: return q*B
    e = p*math.exp(beta*(A-B))
    if e >= 1: return -math.inf
    return q*(p*A + (1-p)/beta*(beta*B + math.log1p(-e) - math.log1p(-p)))
def Htp(q):
    A, B, l = AB(q)
    Bp = -w/q
    if A <= B: return B + q*Bp
    Ap = (-w*q - l)/(q*q); e = p*math.exp(beta*(A-B))
    logZ = beta*B + math.log1p(-e) - math.log1p(-p)
    ZpZ = beta*(Bp - e*Ap)/(1 - e)
    return p*(-l - w) + (1-p)/beta*(logZ + q*ZpZ)
# a(0): left root of G0 on (0, mu)
lo, hi = 1e-12, mu
assert G0(hi) < 0
# find a point where G0>0 to the left: G0(0+) = beta log(p/x) > 0
for _ in range(200):
    m = 0.5*(lo+hi)
    if G0(m) >= 0: lo = m
    else: hi = m
a0 = hi
print("a(0) =", a0, "Ht'(mu) =", Htp(mu), "y_c =", float(Fr(v["y_c"])))
def qhat(y):
    if y <= Htp(mu): return mu
    lo, hi = a0*(1+1e-15), mu
    for _ in range(64):
        m = 0.5*(lo+hi)
        if Htp(m) > y: lo = m
        else: hi = m
    return 0.5*(lo+hi)
qpk = qhat(-w); Hpk = Ht(qpk) + w*qpk
def qrange(c):
    if Hpk < c: return None
    lo, hi = a0*(1+1e-15), qpk
    for _ in range(64):
        m = 0.5*(lo+hi)
        if Ht(m) + w*m >= c: hi = m
        else: lo = m
    qlo = hi
    if Ht(mu) + w*mu >= c: qhi = mu
    else:
        lo, hi = qpk, mu
        for _ in range(64):
            m = 0.5*(lo+hi)
            if Ht(m) + w*m >= c: lo = m
            else: hi = m
        qhi = lo
    return qlo, qhi
def integrand(y, c):
    qh = qhat(y)
    if c is None: q = qh
    else:
        r = qrange(c)
        if r is None: return -math.inf
        q = min(max(qh, r[0]), r[1])
    return Ht(q) - q*y
phis = lambda u: -w*(1 + math.log(u))
# exact c on the grid: suffix sums S_k = sum_{j>=k} v_j * w*log(v_{j+1}/v_j), v_j = u_b + j D, j = 0..n-1, v_n = 1
n = round((1 - u_b)/D)
S = [0.0]*(n+1)
acc = 0.0
for j in range(n-1, -1, -1):
    vj = u_b + j*D; vj1 = 1.0 if j == n-1 else u_b + (j+1)*D
    acc += vj*w*math.log(vj1/vj); S[j] = acc
Stot = S[0]
print("n", n, "S_total", Stot, "vs w(1-u_b)", w*(1-u_b))
def c_exact(u):
    if u <= u_b: return a0*Stot
    k = math.ceil((u - u_b)/D - 1e-12)
    return a0*S[min(k, n)] if k <= n-1 else 0.0
def simpson(f, a, b, N):
    h = (b-a)/N; s = f(a) + f(b)
    for i in range(1, N): s += (4 if i % 2 else 2)*f(a + i*h)
    return s*h/3
t = time.time()
# left part via u = u_b e^{-s}
def left(cfun):
    return simpson(lambda s: integrand(phis(u_b*math.exp(-s)), cfun(u_b*math.exp(-s)))*u_b*math.exp(-s), 0.0, 60.0, 6000)
def right(cfun, N=20000):
    return simpson(lambda u: integrand(phis(u), cfun(u)), u_b, 1.0, N)
cert = left(lambda u: None) + right(lambda u: None)
print("CERT (unconstrained, = int Hhat(phi_s)) ~", cert, "%.0fs" % (time.time()-t))
# c bracketing: c_hi(u) = a0*w*(1-u) >= exact? and c_lo shifted down by mesh; plus exact step
cl = lambda u: a0*Stot if u <= u_b else a0*(w*(1-u) - w*D*(2 + math.log(1/u_b)))
ch = lambda u: a0*Stot if u <= u_b else a0*w*(1-u)
L = left(lambda u: a0*Stot)
VAlo = L + right(ch); VAhi = L + right(cl); VAex = L + right(c_exact)
print("V_A(phi_s) with c_hi: %.6e  with c_lo: %.6e  exact step c: %.6e  (left part %.6e) %.0fs" % (VAlo, VAhi, VAex, L, time.time()-t))
